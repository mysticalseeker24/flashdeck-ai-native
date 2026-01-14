# 🧠 FlashDeck AI - Backend Layer

The brain of the operation. This directory contains the **FastAPI** server and the **LangGraph** agent definitions.

## 📂 Structure
-   `main.py`: Entry point. Handles API requests, PDF text extraction, and invokes the Agent Graph.
-   `agent_graph.py`: **The Core**. Defines the `StateGraph` workflow, nodes (Chunker, Generator, Refiner), and LLM configurations.
-   `deck_builder.py`: Utility to generate `.apkg` files (using `genanki`).
-   `ai_engine.py`: (Legacy) Simple generation logic, kept for reference or utility functions.

## 🤖 The Multi-Agent System
We use **LangGraph** to model the flashcard generation process as a state machine.

### State Schema
```python
class DeckState(TypedDict):
    original_text: str       # Full PDF text
    chunks: List[str]        # Split segments
    partial_cards: List[Dict]# Raw output from Generator
    final_cards: List[Dict]  # Deduplicated deck
```

### Nodes
1.  **`chunk_document`**: Uses `RecursiveCharacterTextSplitter` to create manageable chunks (4000 chars).
2.  **`generate_cards_node`**: Iterates through chunks. Uses `ChatOpenAI` (Gemini 3 Pro) to extract Q&A pairs. Enforces rigid JSON output (`q`, `a`).
3.  **`refine_deck`**: Aggregates results. Handles key normalization (`question` vs `q`, `front` vs `q`) and deduplicates based on the Question text.

## 🛠️ Configuration
The system uses `python-dotenv` to load secrets from a `.env` file located in the project root (`flashdeck-ai/.env`).

### Required Variables
Copy `.env.example` to `.env` and populate:

```ini
# LangSmith (Tracing)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...

# AI Provider
OPENROUTER_API_KEY=...
```

## 📦 Dependencies
-   `fastapi`, `uvicorn`: Web Server.
-   `langchain`, `langgraph`: Agent Framework.
-   `langchain-openai`: LLM Interface (compatible with OpenRouter).
-   `pypdf`: PDF Text Extraction.
-   `genanki`: Anki file generation.
