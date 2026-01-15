from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ai_engine import extract_text
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
    return {"status": "FlashDeck Brain is Online 🧠"}

@app.post("/generate")
async def generate_deck(file: UploadFile = File(...)):
    print(f"📄 Processing {file.filename}...")
    
    try:
        # 1. Analyze Document (Text or Vision)
        from vision_engine import process_pdf
        
        await file.seek(0)
        try:
            # process_pdf returns {"mode": "...", "content": ...}
            # We want to extract just the content for the graph.
            # But the graph "chunker" expects "original_text".
            # If it's a list of images, chunker needs to handle it.
            
            # Let's handle the stream reading inside process_pdf? 
            # Ideally process_pdf takes bytes or stream.
            
            result_payload = process_pdf(file.file)
            content = result_payload["content"]
            mode = result_payload["mode"]
            
        except Exception as e:
            print(f"Processing Error: {e}")
            raise HTTPException(status_code=400, detail=f"PDF Read Failed: {e}")
            
        if not content:
             print("Content empty.")
             raise HTTPException(status_code=400, detail="Could not extract content.")

        print(f"Processed Document. Mode: {mode}. Content Size: {len(content)}")

        # 2. Run Multi-Agent Graph
        from agent_graph import app_graph
        try:
            # If mode is text, content is String. If mode is image, content is List[String]
            # We pass it as 'original_text' (misnomer, but state key)
            inputs = {"original_text": content, "chunks": [], "partial_cards": [], "final_cards": []}
            result = app_graph.invoke(inputs)
            cards_data = result.get("final_cards", [])
            
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
        deck_name = file.filename.replace(".pdf", "")
        output_file = create_anki_deck(cards, deck_name=deck_name)
        
        # 4. Return Output
        return {
            "status": "success",
            "deck_name": deck_name,
            "cards": cards,
            "download_path": output_file
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
