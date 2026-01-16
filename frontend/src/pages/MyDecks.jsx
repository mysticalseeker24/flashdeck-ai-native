import { useState, useRef } from 'react'
import { ArrowLeft, BookOpen, Sparkles, Filter, Download, Home, FileText, Image as ImageIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

export default function MyDecks({ cards, deckName }) {
    const [selectedTopic, setSelectedTopic] = useState(null)
    const cardsRef = useRef(null)

    // Group cards by topic
    const topics = selectedTopic ? [] : Array.from(new Set(cards.map(c => c.topic || "General"))).sort()

    const filteredCards = selectedTopic
        ? cards.filter(c => (c.topic || "General") === selectedTopic)
        : []

    if (!cards || cards.length === 0) {
        return (
            <div className="min-h-screen bg-[#191919] text-gray-200 flex flex-col items-center justify-center">
                <BookOpen size={64} className="text-gray-700 mb-6" />
                <h2 className="text-xl font-medium text-gray-400">No Flashcards Generated Yet</h2>
                <Link to="/app" className="mt-6 text-orange-400 hover:text-orange-300">
                    Go back to Dashboard
                </Link>
            </div>
        )
    }

    const downloadPDF = async () => {
        if (!cardsRef.current || filteredCards.length === 0) return;
        try {
            const canvas = await html2canvas(cardsRef.current, {
                backgroundColor: '#191919',
                scale: 2,
                logging: false
            });
            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

            if (pdfHeight > 297) {
                pdf.addPage();
                pdf.deletePage(1); // Clean slate
                pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            } else {
                pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            }
            pdf.save(`flashdeck-${selectedTopic || 'all'}.pdf`);
        } catch (e) {
            alert("Export failed");
        }
    }

    return (
        <div className="min-h-screen bg-[#191919] text-gray-200 font-sans p-6 md:p-12">
            {/* Header */}
            <div className="flex items-center justify-between mb-10">
                <div className="flex items-center gap-4">
                    <Link to="/app" className="p-2 bg-white/5 rounded-full hover:bg-white/10 transition-colors" title="Back to Dashboard">
                        <ArrowLeft size={20} />
                    </Link>
                    <Link to="/" className="p-2 bg-white/5 rounded-full hover:bg-white/10 transition-colors" title="Go Home">
                        <Home size={20} />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-white">{deckName || "Untitled Deck"}</h1>
                        <p className="text-sm text-gray-500">{selectedTopic ? `Topic: ${selectedTopic}` : `${cards.length} Cards Total`}</p>
                    </div>
                </div>

                {/* Export Controls for Topic View */}
                {selectedTopic && (
                    <div className="flex gap-2">
                        <button onClick={downloadPDF} className="flex items-center gap-2 px-3 py-2 bg-[#2a2a2a] hover:bg-[#333] rounded-lg text-sm border border-white/10 transition-colors">
                            <FileText size={16} /> PDF
                        </button>
                    </div>
                )}
            </div>

            {/* Content */}
            {!selectedTopic ? (
                // Topic Grid
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {topics.map(topic => {
                        const count = cards.filter(c => (c.topic || "General") === topic).length
                        return (
                            <div k={topic} onClick={() => setSelectedTopic(topic)} className="bg-[#202020] border border-white/5 p-8 rounded-2xl hover:border-orange-500/50 hover:bg-[#252525] transition-all cursor-pointer group">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="p-2 bg-orange-500/10 rounded-lg">
                                        <Filter size={20} className="text-orange-500" />
                                    </span>
                                    <span className="text-xs font-mono text-gray-500">{count} CARDS</span>
                                </div>
                                <h3 className="text-xl font-semibold text-white group-hover:text-orange-400 transition-colors">{topic}</h3>
                            </div>
                        )
                    })}
                </div>
            ) : (
                // Flashcards List
                <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {filteredCards.map((card, idx) => (
                        <FlashcardItem key={idx} card={card} />
                    ))}
                </div>
            )}
        </div>
    )
}

function FlashcardItem({ card }) {
    const [flipped, setFlipped] = useState(false)
    return (
        <div
            onClick={() => setFlipped(!flipped)}
            className="group relative bg-[#202020] hover:bg-[#252525] border border-white/5 rounded-xl p-8 min-h-[280px] cursor-pointer transition-all hover:-translate-y-1 hover:shadow-2xl flex flex-col justify-center items-center text-center preserve-3d"
        >
            {!flipped ? (
                <>
                    <span className="absolute top-4 left-4 text-[10px] font-mono text-gray-600 uppercase tracking-widest">Question</span>
                    <h3 className="text-lg font-medium text-white leading-relaxed">{card.q}</h3>
                    <div className="absolute bottom-4 text-gray-600 text-xs flex items-center gap-2">
                        <Sparkles size={12} /> Click to reveal
                    </div>
                </>
            ) : (
                <>
                    <span className="absolute top-4 left-4 text-[10px] font-mono text-orange-500 uppercase tracking-widest">Answer</span>
                    <p className="text-base text-gray-300 leading-relaxed">{card.a}</p>
                </>
            )}
        </div>
    )
}
