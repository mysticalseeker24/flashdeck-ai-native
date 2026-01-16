# FlashDeck AI ⚡

> **Transform your chaotic notes and lecture slides into structured, interactive study materials.**

FlashDeck AI is a powerful study companion that uses advanced LLMs and multimodal RAG (Retrieval-Augmented Generation) to analyze your PDFs—whether they are digital text or scanned images—and generate high-quality flashcards, knowledge graphs, and an interactive AI tutor.

---

## 🎯 What It Does

1.  **Smart Flashcards**: Automatically generates QA pairs from your documents, grouped by topic.
2.  **Visual Knowledge Maps**: Creates interactive Mermaid.js flowcharts to visualize concepts and hierarchies.
3.  **Chat with your Docs**: A RAG-powered assistant that can answer questions based *only* on your uploaded content, complete with source tracking.
4.  **Vision Capable**: Can read and transcribe scanned PDFs, handwritten notes, and image-heavy slides.

## 🏗️ Architecture

The project is split into two core components:

*   **Backend (`/backend`)**: A FastAPI service orchestrating LangGraph agents. It handles OCR, embedding generation (ChromaDB), and LLM interactions (OpenRouter / Google Gemini 3 Flash Preview).
*   **Frontend (`/frontend`)**: A sleek React application (Vite + Tailwind) offering a distraction-free study environment, 3-pane knowledge base, and PDF export tools.

## 🚀 Quick Start

### Prerequisites
*   Node.js (v18+)
*   Python (v3.9+)
*   OpenRouter API Key

### 1. Launch Backend
```bash
cd backend
# Setup env
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Virtual Environment
python -m venv venv
.\venv\Scripts\activate # Windows
# source venv/bin/activate # Mac/Linux

pip install -r requirements.txt
python -m uvicorn main:app --port 8001 --reload
```

### 2. Launch Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173** and start learning!

## 📜 Versioning

See [versioning.md](versioning.md) for a detailed changelog.
Latest Version: **v3.1 (RAG Fixes & UI Overhaul)**

## 📄 License

MIT License. Built for the Native AI Workshop.
