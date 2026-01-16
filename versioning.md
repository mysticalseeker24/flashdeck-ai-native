# Version History

## v3.1 - The "Polish" Update (Current)
*Released: 2026-01-17*

**UX & Usability:**
*   **Export Functionality**: Added "Export to PDF" button in the Top Deck view, allowing users to save specific topic decks.
*   **Navigation**: Added "Home" icon buttons to `Dashboard`, `MyDecks`, and `KnowledgeBase` headers for easier navigation.
*   **Cleanup**: Removed unused legacy components (`ChatSidebar`, `StickyTabs`) to reduce bundle size and maintenance overhead.

**Bug Fixes:**
*   Fixed a critical crash in generation where `{}` brackets in the prompt were misinterpreted by LangChain as missing variables.
*   Fixed "ChatSidebar module not found" build error.

---

## v3.0 - The "RAG & Vision" Overhaul
*Released: 2026-01-16*

**Core AI Improvements:**
*   **Vision RAG**: Implemented a "Transcription" step for image-based PDFs (scanned docs). The LLM now generates a text summary of every page, which is indexed into ChromaDB.
*   **Topic Aware**: Flashcards are now generated with a `topic` field, allowing for better organization.
*   **Thinking Logs**: The backend now logs "Thinking..." steps to the console during chat, improving transparency.

**UI Redesign:**
*   **Dashboard**: Completely removed the sidebar/tabbe interface in favor of a clean "Upload -> Action" flow.
*   **My Decks**: Introduced a Topic Grid view.
*   **Knowledge Base**: Introduced a professional 3-pane layout (Source List | Flowchart | Char).
*   **Flowcharts**: Moved flowcharts exclusively to the Knowledge Base for better visibility.

---

## v2.0 - The "Agentic" Shift
*   Migrated from simple chains to **LangGraph**.
*   Introduced `DeckState` for managing generation flow.
*   Added `refine_deck` node for deduplication.

### Prerequisites
*   Node.js (v18+)
*   Python (v3.9+)
*   OpenRouter API Key

### 1. Launch Backend
```bash
cd backend
# Setup env
echo "OPENROUTER_API_KEY=your_key_here" > .env
```

## v1.0 - MVP
*   Basic PDF text extraction.
*   Simple Q&A generation.
*   Basic Chat interface.
