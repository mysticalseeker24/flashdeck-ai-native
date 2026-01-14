import os
from typing import List, TypedDict, Annotated, Dict, Any
import operator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

# Load env from parent directory (flashdeck-ai/.env) or current
load_dotenv(find_dotenv(usecwd=True)) 
# Fallback search if backend is CWD, it might check parent? find_dotenv does recursive search or just up?
# Let's use specific path logic if find_dotenv fails, but standard find_dotenv usually works if file is in root.
# Actually, explicitly finding it is safer for this setup.
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# --- CONFIGURATION ---
# LangSmith Config (loaded from env automatically if set, but we can enforce)
# os.environ["LANGSMITH_TRACING"] = "true" # Can be in .env
# Pydantic/LangChain automatically reads defaults, but we can set defaults if missing.

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env")

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="google/gemini-3-pro-preview",
    default_headers={
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "FlashDeckAgent"
    }
)

# --- DATATYPES ---

class Flashcard(BaseModel):
    q: str = Field(description="Question")
    a: str = Field(description="Answer")

class CardList(BaseModel):
    cards: List[Flashcard]

class DeckState(TypedDict):
    original_text: str
    chunks: List[str]
    partial_cards: Annotated[List[Dict], operator.add] 
    final_cards: List[Dict]

# --- NODES ---

def chunk_document(state: DeckState):
    print("--- NODE: CHUNKER ---")
    text = state['original_text']
    # Efficient splitting for 'NotebookLM' feel - decently large chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    docs = splitter.create_documents([text])
    chunks = [d.page_content for d in docs]
    print(f"Created {len(chunks)} chunks.")
    return {"chunks": chunks}

def generate_cards_node(state: DeckState):
    print("--- NODE: GENERATOR ---")
    chunks = state['chunks']
    generated = []
    
    parser = JsonOutputParser(pydantic_object=CardList)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert tutor. Create 5-10 high-quality flashcards from the provided text. Return JSON with keys 'q' (question) and 'a' (answer)."),
        ("user", "{text}")
    ])
    chain = prompt | llm | parser

    # Process chunks 
    for i, chunk in enumerate(chunks):
        if i >= 20: break 
        try:
            print(f"Generating for chunk {i+1}/{len(chunks)}...")
            res = chain.invoke({"text": chunk})
            if isinstance(res, dict) and "cards" in res:
                generated.extend(res['cards'])
            elif isinstance(res, list): 
                 generated.extend(res)
        except Exception as e:
            print(f"Error on chunk {i}: {e}")

    return {"partial_cards": generated}

def refine_deck(state: DeckState):
    print("--- NODE: REFINER ---")
    raw_cards = state['partial_cards']
    print(f"DEBUG: First card raw: {raw_cards[0] if raw_cards else 'None'}")
    
    # Deduplication
    unique_map = {}
    for c in raw_cards:
        # Normalize
        if hasattr(c, 'model_dump'): 
             c = c.model_dump()
        elif hasattr(c, 'dict'):
             c = c.dict()
             
        # Check keys case-insensitive backup
        q = c.get('q') or c.get('Q') or c.get('question') or c.get('Question') or c.get('front') or c.get('Front')
        a = c.get('a') or c.get('A') or c.get('answer') or c.get('Answer') or c.get('back') or c.get('Back')
        
        if q and isinstance(q, str):
            unique_map[q.strip()] = {"q": q, "a": a}
            
    final_list = list(unique_map.values())
    print(f"Refined {len(raw_cards)} cards to {len(final_list)} unique cards.")
    return {"final_cards": final_list}

# --- GRAPH BUILD ---

workflow = StateGraph(DeckState)
workflow.add_node("chunker", chunk_document)
workflow.add_node("generator", generate_cards_node)
workflow.add_node("refiner", refine_deck)

workflow.set_entry_point("chunker")
workflow.add_edge("chunker", "generator")
workflow.add_edge("generator", "refiner")
workflow.add_edge("refiner", END)

app_graph = workflow.compile()
