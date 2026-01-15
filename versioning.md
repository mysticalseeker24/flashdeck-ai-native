# 📜 Version History

Track the evolution of FlashDeck AI.

---

## v2.0.0 "Turbo" 🚀 (Current)
**Released**: Jan 2026
**Focus**: Speed, Vision, and Parallelism.

### ✨ Major Features
-   **Map-Reduce Architecture**: Moved from sequential processing to **Parallel Async Workers** using LangGraph `Send` API.
-   **Vision Support**: Integrated `vision_engine` (PyMuPDF) to handle **Scanned PDFs** and **Handwriting**.
-   **Batching Optimization**: Batched 5 pages per prompt, increasing throughput by 5x and prompt density.
-   **Model Upgrade**: Switched to `Gemini 3 Flash` for sub-second latent reasoning.

### 🔧 Tech Changes
-   Refactored `agent_graph.py` to use `batches` state and `map_jobs` edge.
-   Added `pymupdf` dependency.
-   Optimized prompts for "High Yield" (15-20 cards/batch).

---

## v1.0.0 "Genesis" 🌱
**Released**: Jan 2026
**Focus**: Initial MVP and Agentic Basics.

### ✨ Features
-   **Multi-Agent Graph**: Creating the Chunker -> Generator -> Refiner pipeline.
-   **Linear Processing**: Sequential processing of document chunks.
-   **Notion UI**: Dark mode, sticky tabs, and clean typography.
-   **Anki Export**: Backend generation of `.apkg` files.

### 🔧 Tech Stack
-   FastAPI + React + LangGraph.
-   Model: `Gemini 3 Pro Preview`.
