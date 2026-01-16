import os
import shutil
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# --- CONFIG ---
# Store ChromaDB in the parent folder or inside backend? Inside backend is fine.
CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

# Load Env if not loaded (safe check)
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_embeddings():
    """
    Returns the embedding function. 
    Using OpenRouter compatible endpoint or defaulting to a lightweight local one if needed.
    We'll try OpenRouter's text-embedding-3-small alias.
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=OPENROUTER_API_KEY,
        check_embedding_ctx_length=False 
    )

def get_vectorstore():
    """
    Returns the persistent Chroma VectorStore.
    """
    return Chroma(
        collection_name="flashdeck_knowledge",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )

def index_content(text_chunks: List[str], deck_id: str, source_file: str):
    """
    Indexes a list of text chunks associated with a specific deck/session.
    """
    if not text_chunks:
        return
        
    print(f"--- RAG: Indexing {len(text_chunks)} chunks for Deck {deck_id} ---")
    
    vs = get_vectorstore()
    
    documents = []
    for i, chunk in enumerate(text_chunks):
        docs = Document(
            page_content=chunk,
            metadata={
                "deck_id": deck_id, 
                "source": source_file,
                "chunk_index": i
            }
        )
        documents.append(docs)
        
    # Batch add
    vs.add_documents(documents)
    print("--- RAG: Indexing Complete ---")

def query_vector_db(query: str, deck_id: Optional[str] = None, k: int = 4):
    """
    Queries the knowledge base.
    """
    vs = get_vectorstore()
    
    # Filter by deck_id if provided
    filter_criteria = {"deck_id": deck_id} if deck_id else None
    
    results = vs.similarity_search(query, k=k, filter=filter_criteria)
    return results

def check_health():
    """
    Checks if ChromaDB is responding.
    """
    try:
        vs = get_vectorstore()
        # Perform a dummy heartbeat
        # vs.as_retriever().invoke("ping") # Retriver invoke might be expensive or syntax specific
        # Just getting collection count is enough
        count = vs._collection.count()
        return True
    except Exception as e:
        print(f"RAG Health Check Failed: {e}")
        return False

def clear_deck_data(deck_id: str):
    """
    Removes data for a specific deck (Cleanup).
    """
    # Chroma Basic Delete is tricky by metadata, but we can try.
    pass

# --- STARTUP MESSAGE ---
print("---------------------------------------------------------------")
print(f"✅ ChromaDB RAG Engine Configured")
print(f"📂 Storage Path: {CHROMA_DIR}")
print(f"🔗 Embeddings: OpenAI (text-embedding-3-small via OpenRouter)")
print("---------------------------------------------------------------")
