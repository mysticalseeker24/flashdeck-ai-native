from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
from typing import List, Optional
from pydantic import BaseModel
import uuid
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag_engine import query_vector_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from deck_builder import create_anki_deck
import shutil
import os

app = FastAPI(title="FlashDeck AI API")

# Allow CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "FlashDeck Brain is Online 🧠", "version": "v3.0.0"}

@app.get("/health")
async def health_check():
    # 1. Check RAG Engine
    from rag_engine import check_health
    rag_status = check_health()
    
    status = "healthy" if rag_status else "degraded"
    
    return {
        "status": status,
        "components": {
            "rag_engine": "online" if rag_status else "offline",
            "llm_api": "connected" # Assumed if app is running
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"🔥 Global Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

@app.post("/generate")
async def generate_deck(files: List[UploadFile] = File(...)):
    print(f"📄 Processing {len(files)} files...")
    deck_id = str(uuid.uuid4())
    
    try:
        # 1. Analyze Documents
        from vision_engine import process_pdf
        
        all_content = []
        is_vision_mode = False
        
        for file in files:
            await file.seek(0)
            try:
                result_payload = process_pdf(file.file)
                content = result_payload["content"]
                mode = result_payload["mode"]
                
                if mode == "image":
                    is_vision_mode = True
                    # If any file is vision, we might treat all as vision or mix.
                    # Current Graph expects explicit mode. 
                    # If we mix, we should probably normalize to text if possible, or list of images.
                    # For simplicty: If Vision mode, we extend list of images.
                    # If text mode, we extend list of text strings?
                    if isinstance(content, list): 
                        all_content.extend(content)
                    else:
                        # Convert text to image? No.
                        # Conflict handling:
                        print("Warning: Mixed content types not fully supported. Treating as text if mixed.")
                else:
                    # Text Mode
                    if isinstance(content, str):
                        all_content.append(content)
                
            except Exception as e:
                print(f"Processing Error {file.filename}: {e}")
                # We continue with other files? Or fail?
                # Fail for now to be safe
                raise HTTPException(status_code=400, detail=f"File Read Failed: {file.filename} - {e}")

        # Normalize content for Graph
        # If is_vision_mode, all_content should be list of b64.
        # If text mode, all_content is List[str].
        # But Graph expects `original_text` as Union[str, List[str]].
        # If it's a List[str] (Text Mode), the chunker handles it?
        # Let's see agent_graph.py:88: text = str(content) -> join list?
        
        final_input_content = all_content
        if not is_vision_mode:
            # Join text modules with newlines
            final_input_content = "\n\n".join(all_content)
            
        print(f"Combined Content Size: {len(final_input_content)} chars/images.")

        # 2. Run Multi-Agent Graph
        from agent_graph import app_graph
        try:
            inputs = {
                "original_text": final_input_content, 
                "chunks": [], 
                "partial_cards": [], 
                "final_cards": [],
                "deck_id": deck_id,
                "flowcharts": []
            }
            result = app_graph.invoke(inputs)
            cards_data = result.get("final_cards", [])
            flowcharts = result.get("flowcharts", [])
            
            # Normalize
            cards = []
            for c in cards_data:
                if isinstance(c, dict):
                    cards.append({"q": c.get("q", ""), "a": c.get("a", "")})
                else:
                    cards.append({"q": c.q, "a": c.a})
                    
        except Exception as e:
             print(f"Agent Graph Error: {e}")
             raise HTTPException(status_code=500, detail=f"Agent Processing Failed: {str(e)}")

        print(f"Agents finished. Generated {len(cards)} cards.")

        # 3. Create Anki Deck
        deck_name = f"FlashDeck_{deck_id[:8]}" 
        output_file = create_anki_deck(cards, deck_name=deck_name)
        
        # 4. Return Output
        return {
            "status": "success",
            "deck_name": deck_name,
            "deck_id": deck_id,
            "cards": cards,
            "flowcharts": flowcharts,
            "download_path": output_file
        }
        
    except Exception as e:
        print(f"Unexpected Error in Generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    deck_id: Optional[str] = None

@app.post("/chat")
async def chat_with_deck(req: ChatRequest):
    try:
        print(f"🤖 User Query: {req.message}")
        print(f"🔍 Retrieving context for Deck: {req.deck_id}...")
        
        # 1. Retrieve Context
        docs = query_vector_db(req.message, req.deck_id)
        print(f"📄 Retrieved {len(docs)} relevant chunks.")
        context_text = "\n\n".join([d.page_content for d in docs])
        
        if not context_text:
            context_text = "No relevant context found in the uploaded documents."
            
        # 2. Generate Answer
        from agent_graph import llm
        
        prompt = ChatPromptTemplate.from_template("""
        You are an intelligent assistant for FlashDeck AI. 
        Answer the user's question based ONLY on the following context from their documents.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer (Concise and helpful):
        """)
        
        chain = prompt | llm | StrOutputParser()
        print("🧠 Generating Answer via LLM...")
        answer = chain.invoke({"context": context_text, "question": req.message})
        print("✅ Answer Generated.")
        
        return {"answer": answer, "sources": [d.metadata.get("source", "unknown") for d in docs]}
        
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


