# FlashDeck AI Frontend ⚡

A modern, immersive web application for studying and visualizing your notes.

## 🌟 New in v3.1

*   **Zero-Distraction Dashboard**: Clean upload interface with vibrant animations.
*   **Topic-Based Decks**: Flashcards are intelligently grouped by topic (e.g., "Introduction", "Advanced Concepts").
*   **Knowledge Base**: A professional 3-pane interface for deep diving:
    *   **Source View**: See your uploaded files.
    *   **Visual Canvas**: Zoomable Mermaid.js interactive flowcharts.
    *   **AI Assistant**: Chat with your documents in real-time.
*   **Export**: Download specific topic decks as high-quality PDFs.

## 🛠️ Stack

*   **Framework**: React (Vite)
*   **Styling**: Tailwind CSS + Shadcn UI (Radix Primitives)
*   **Icons**: Lucide React
*   **Visuals**: Mermaid.js (Diagrams), Framer Motion (Animations)
*   **Export**: html2canvas, jsPDF

## 🏃‍♂️ Setup & Run

1.  **Install Dependencies**:
    ```bash
    npm install
    ```

2.  **Start Dev Server**:
    ```bash
    npm run dev
    ```
    *   Access at: `http://localhost:5173`

3.  **Build for Production**:
    ```bash
    npm run build
    ```

## 📂 Key Components

*   `pages/Dashboard.jsx`: Main entry, upload handling, and navigation hub.
*   `pages/MyDecks.jsx`: Topic grid and flashcard review interface with export.
*   `pages/KnowledgeBase.jsx`: integrated 3-pane study environment.
*   `components/FlowchartView.jsx`: Renders Mermaid.js diagrams.
