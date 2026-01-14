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
        # 1. Extract Text
        # Ensure regex start
        await file.seek(0)
        try:
            text = extract_text(file.file)
        except Exception as e:
            print(f"Extraction Error: {e}")
            raise HTTPException(status_code=400, detail=f"PDF Read Failed: {e}")
            
        if not text:
             print("Text empty.")
             raise HTTPException(status_code=400, detail="Could not extract text (scanned PDF?).")

        print(f"Extracted {len(text)} chars. Running Agents...")

        # 2. Run Multi-Agent Graph
        from agent_graph import app_graph
        try:
            inputs = {"original_text": text, "chunks": [], "partial_cards": [], "final_cards": []}
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
