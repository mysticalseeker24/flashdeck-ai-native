# ⚡ FlashDeck AI: The Automated Study Agent

**Goal**: Build a full-stack web app where users upload PDFs/Text, and AI generates downloadable Anki Flashcards (`.apkg`).

## 🏗️ Tech Stack
*   **Frontend**: React (Vite) + TailwindCSS + ShadcnUI.
*   **Backend**: FastAPI + Python.
*   **AI**: Gemini Flash (via OpenRouter).
*   **Core Libraries**: `genanki` (Anki Deck creation), `pypdf` (PDF parsing).

---

## 📅 Development Phases

### Phase 1: Backend (The Core)
*   [ ] Setup `fastapi` project.
*   [ ] Implement **PDF Text Extraction** endpoint.
*   [ ] Implement **AI Generation Chain** (Chunking -> Q&A Generation).
*   [ ] Implement **.apkg Generator** using `genanki`.
*   [ ] Create API Endpoint: `POST /generate-deck` (Input: File -> Output: .apkg).

### Phase 2: Frontend (The Look)
*   [ ] Initialize `vite` project with React & TypeScript.
*   [ ] Configure **ShadcnUI** & Tailwind.
*   [ ] Build UI Components:
    *   File Uploader (Drag & Drop).
    *   "Generating..." Loading State (Progress Bar).
    *   Flashcard Preview (Carousel view before download).
    *   Download Button.

### Phase 3: Integration
*   [ ] Connect React to FastAPI.
*   [ ] Handle CORS.
*   [ ] Error Handling (e.g., "PDF too large").

---

## 📂 Project Structure
```
flashdeck-ai/
├── backend/
│   ├── main.py
│   ├── ai_engine.py
│   ├── deck_builder.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── App.tsx
    │   └── ...
    ├── package.json
    └── ...
```

## 🧠 Data Flow
1.  **User** uploads `lecture.pdf`.
2.  **Frontend** sends file to `POST /upload`.
3.  **Backend** extracts text -> Sends to **Gemini**.
4.  **Gemini** returns JSON: `[{ "q": "What is Mitochondria?", "a": "Powerhouse of cell" }]`.
5.  **Backend** converts JSON -> `anki_deck.apkg`.
6.  **Backend** returns the file stream.
7.  **User** downloads file.
