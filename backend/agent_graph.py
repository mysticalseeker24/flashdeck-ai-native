import os
import operator
from typing import List, TypedDict, Annotated, Dict, Any, Union
from typing_extensions import TypedDict as ExtTypedDict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END, START
from langgraph.types import Send
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

# --- SETUP ---
# Load env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

# Model Config
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="google/gemini-3-flash-preview",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "FlashDeckAgent"
    }
)

# --- SCHEMAS ---

class Flashcard(BaseModel):
    q: str = Field(description="Question")
    a: str = Field(description="Answer")

class CardList(BaseModel):
    cards: List[Flashcard]

# Main Graph State
class DeckState(TypedDict):
    original_text: Union[str, List[str]] # Text or List of Base64 Images
    # The reducer will automatically aggregate lists of lists (if we output list) 
    # OR we append to partial_cards list.
    partial_cards: Annotated[List[Dict], operator.add] 
    final_cards: List[Dict]

# Worker State (Input for Map)
class BatchInput(TypedDict):
    batch_content: List[str] # List of 5 images OR text chunk

# --- NODES ---

def chunk_document(state: DeckState):
    """
    MAPPER: splits content into batches.
    Returns nothing to state, but determines valid edges via 'map_batches'
    """
    print("--- NODE: CHUNKER (MAPPER) ---")
    content = state['original_text']
    
    batches = []
    
    # 1. Vision Mode (List of images)
    if isinstance(content, list):
        BATCH_SIZE = 5
        print(f"Vision Mode: {len(content)} pages. Batching by {BATCH_SIZE}...")
        for i in range(0, len(content), BATCH_SIZE):
            batches.append(content[i:i + BATCH_SIZE])
            
    # 2. Text Mode (String)
    else:
        text = str(content)
        splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        docs = splitter.create_documents([text])
        # Text is simple, just list of strings
        # We can also batch text chunks if we want, but usually 1 chunk = 1 context window is fine.
        # Let's just treat each text chunk as a "batch" of 1 item for consistency?
        # Or just pass the string.
        text_chunks = [d.page_content for d in docs]
        batches = [[c] for c in text_chunks] 

    print(f"Created {len(batches)} batches/jobs.")
    # We return the list of batches to be used by the conditional edge Logic
    # But standard graph nodes return State updates.
    # We will pass 'batches' as a temporary key or rely on logic inside the edge function?
    # LangGraph best practice: return to state? 
    # But BatchInput is separate. 
    # Use a hidden key in state? make 'batches' part of state?
    # Actually, we can just return logic for the edge if we move this logic TO the edge?
    # No, keep node. Let's add 'batches' to DeckState so edge can read it.
    return {"batches": batches} # Needs to be added to TypedDict above? 
    # Or strict typing? Let's add it.

# Modified DeckState to holding batches temporarily
class DeckState(TypedDict):
    original_text: Union[str, List[str]]
    partial_cards: Annotated[List[Dict], operator.add] 
    final_cards: List[Dict]
    batches: List[List[str]] # Temp storage for mapper

def generate_batch_node(state: BatchInput):
    """
    WORKER: Processes a single batch of images/text.
    """
    batch = state['batch_content']
    print(f"--- WORKER: Processing Batch ({len(batch)} items) ---")
    
    generated = []
    parser = JsonOutputParser(pydantic_object=CardList)
    
    # Check if this batch is Images (Vision) or Text
    # Heuristic: check first item length/spaces
    first_item = batch[0]
    is_image = len(first_item) > 100 and " " not in first_item[:100]
    
    try:
        if is_image:
            # Construct ONE Multimodal Message for the whole batch
            content_parts = [
                {"type": "text", "text": "Analyze these document slides/pages. Create 15-20 high-quality flashcards covering EVERY key concept shown across these pages. Be comprehensive. Return valid JSON only."}
            ]
            for img in batch:
                content_parts.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                })
                
            msg = {"role": "user", "content": content_parts}
            res = llm.invoke([msg])
            
        else:
            # Text Batch (usually 1 large chunk)
            text_blob = "\n\n".join(batch)
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert tutor. Create 15-20 high-quality flashcards covering all topics in the text. Return JSON with 'q' and 'a' keys."),
                ("user", "{text}")
            ])
            chain = prompt | llm | parser
            # We bypass chain invoke to handle manual parsing if needed, but chain is cleaner for text
            res = chain.invoke({"text": text_blob})
            # chain returns parsed dict usually
            if isinstance(res, dict) and "cards" in res:
                return {"partial_cards": res['cards']}
            elif isinstance(res, list):
                 return {"partial_cards": res}
            return {"partial_cards": []} # Fallback

        if is_image:
             # Manual Parse for Vision
             parsed = parser.parse(res.content)
             if isinstance(parsed, dict) and "cards" in parsed:
                 generated = parsed['cards']
             elif isinstance(parsed, list):
                 generated = parsed
                 
    except Exception as e:
        print(f"Worker Error: {e}")
        
    return {"partial_cards": generated}

def refine_deck(state: DeckState):
    print("--- NODE: REFINER (REDUCER) ---")
    raw_cards = state['partial_cards']
    print(f"Debugging: Aggregated {len(raw_cards)} cards.")
    
    unique_map = {}
    for c in raw_cards:
        if hasattr(c, 'model_dump'): c = c.model_dump()
        elif hasattr(c, 'dict'): c = c.dict()
        
        q = c.get('q') or c.get('Q') or c.get('question') or c.get('front')
        a = c.get('a') or c.get('A') or c.get('answer') or c.get('back')
        
        if q and isinstance(q, str):
            unique_map[q.strip()] = {"q": q, "a": a}
            
    final = list(unique_map.values())
    return {"final_cards": final}

# --- EDGE LOGIC ---

def map_jobs(state: DeckState):
    # Retrieve batches created by chunker
    batches = state.get("batches", [])
    # Create Send objects for parallel execution
    return [Send("generator", {"batch_content": b}) for b in batches]

# --- GRAPH BUILD ---

workflow = StateGraph(DeckState)
workflow.add_node("chunker", chunk_document)
workflow.add_node("generator", generate_batch_node)
workflow.add_node("refiner", refine_deck)

workflow.add_edge(START, "chunker")
workflow.add_conditional_edges("chunker", map_jobs, ["generator"])
workflow.add_edge("generator", "refiner")
workflow.add_edge("refiner", END)

app_graph = workflow.compile()
