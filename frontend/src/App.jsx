import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import MyDecks from './pages/MyDecks'
import KnowledgeBase from './pages/KnowledgeBase'
import './App.css'

function App() {
  // Global State lifted from Dashboard
  const [files, setFiles] = useState([])
  const [cards, setCards] = useState([])
  const [flowcharts, setFlowcharts] = useState([])
  const [deckName, setDeckName] = useState("")
  const [deckId, setDeckId] = useState(null)

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route
          path="/app"
          element={
            <Dashboard
              files={files}
              setFiles={setFiles}
              setCards={setCards}
              setFlowcharts={setFlowcharts}
              setDeckName={setDeckName}
              setDeckId={setDeckId}
              deckId={deckId}
            />
          }
        />

        <Route
          path="/my-decks"
          element={
            <MyDecks
              cards={cards}
              deckName={deckName}
            />
          }
        />

        <Route
          path="/knowledge-base"
          element={
            <KnowledgeBase
              files={files}
              flowcharts={flowcharts}
              deckId={deckId}
            />
          }
        />

        {/* Redirect unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
