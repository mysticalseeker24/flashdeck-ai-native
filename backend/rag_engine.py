import os
import shutil
import pickle
from typing import List, Optional
from uuid import uuid4

# LangChain Imports
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_classic.retrievers import ParentDocumentRetriever
# from langchain.retrievers import ParentDocumentRetriever # Fallback failed
from langchain_classic.storage import LocalFileStore
# from langchain.storage import LocalFileStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.storage import LocalFileStore # Explicit import if needed

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")
DOC_STORE_DIR = os.path.join(BASE_DIR, "doc_store") # For Parent Docs

# Ensure directories exist
os.makedirs(DOC_STORE_DIR, exist_ok=True)

# Load Env
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_embeddings():
    """
    Returns the embedding function. 
    Using OpenRouter compatible endpoint (text-embedding-3-small).
    """
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=OPENROUTER_API_KEY,
        check_embedding_ctx_length=False 
    )

def get_vectorstore():
    """
    Returns the persistent Chroma VectorStore (Child Docs).
    """
    return Chroma(
        collection_name="flashdeck_knowledge_child", # New collection for v4 logic
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )

def get_docstore():
    """
    Returns the LocalFileStore for Parent Docs (blob storage).
    """
    return LocalFileStore(DOC_STORE_DIR)

def get_retriever():
    """
    Constructs the ParentDocumentRetriever.
    """
    vectorstore = get_vectorstore()
    store = get_docstore()
    
    # 1. Child Splitter: Small chunks for vector search
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    
    # 2. Parent Splitter: Large chunks (or None to use full docs) for LLM context
    # If the input docs are already "Pages", we might not need to split parents further.
    # But let's set a safe large limit (e.g. 2000 chars) in case we get raw text.
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    return retriever

def index_content(text_chunks: List[str], deck_id: str, source_file: str):
    """
    Indexes content using the Advanced RAG (Parent-Child) strategy.
    
    Args:
        text_chunks: List of strings. In v3/v4 logic, these are usually full Pages (transcribed or extracted).
    """
    if not text_chunks:
        return
        
    print(f"--- RAG (Advanced): Indexing {len(text_chunks)} Parent Chunks for Deck {deck_id} ---")
    
    # Convert strings to Documents
    documents = []
    for i, chunk in enumerate(text_chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "deck_id": deck_id, 
                "source": source_file,
                "page_number": i + 1
            }
        )
        documents.append(doc)
    
    # Use the Retriever to add docs. 
    # It will automatically:
    # 1. Split these 'parents' into 'children'
    # 2. Embed children -> Chroma
    # 3. Store parents -> LocalFileStore
    retriever = get_retriever()
    retriever.add_documents(documents)
    
    print("--- RAG: Indexing Complete ---")

def query_vector_db(query: str, deck_id: Optional[str] = None, k: int = 4):
    """
    Queries the knowledge base using the Parent Document Retriever.
    """
    retriever = get_retriever()
    
    # Note: ParentDocumentRetriever search_kwargs are for the underlying vectorstore search
    # We want to filter by deck_id.
    if deck_id:
        retriever.search_kwargs = {
            "filter": {"deck_id": deck_id},
            "k": k
        }
    else:
        retriever.search_kwargs = {"k": k}

    print(f"🔍 RAG Query: '{query}' (Deck: {deck_id})")
    results = retriever.invoke(query)
    
    # Results are the PARENT documents (large context).
    return results

def check_health():
    """
    Checks if ChromaDB is responding.
    """
    try:
        vs = get_vectorstore()
        count = vs._collection.count()
        return True
    except Exception as e:
        print(f"RAG Health Check Failed: {e}")
        return False

def clear_deck_data(deck_id: str):
    """
    Removes data for a specific deck.
    TODO: This is harder with ParentDocumentRetriever as it manages keys. 
    For now, we might skip deletion or implement a scan-and-delete if critical.
    """
    pass

# --- STARTUP MESSAGE ---
print("---------------------------------------------------------------")
print(f"✅ Advanced RAG Engine (Parent Doc Retriever) Configured")
print(f"📂 Vector Store: {CHROMA_DIR}")
print(f"📂 Parent Store: {DOC_STORE_DIR}")
print("---------------------------------------------------------------")
