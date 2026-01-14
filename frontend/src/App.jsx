import { useState, useEffect, useRef } from 'react'
import StickyTabs from './components/ui/sticky-section-tabs'
import { Upload, FileText, Zap, Brain, Check, Sparkles, BookOpen, X, Download, Image as ImageIcon, FileType } from 'lucide-react'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [showGuide, setShowGuide] = useState(false)
  const [cards, setCards] = useState([])
  const [deckName, setDeckName] = useState("")
  const [selectedCard, setSelectedCard] = useState(null)
  const cardsRef = useRef(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setUploadProgress(0);
      setShowGuide(false);

      let progress = 0;
      const interval = setInterval(() => {
        progress += 10;
        setUploadProgress(progress);
        if (progress >= 100) {
          clearInterval(interval);
          setShowGuide(true);
        }
      }, 100);
    }
  }

  const handleGenerate = async () => {
    if (!file) return;
    setLoading(true);
    setCards([]);
    setShowGuide(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8001/generate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("Generation failed");

      const data = await response.json();
      setCards(data.cards);
      setDeckName(data.deck_name);

      setTimeout(() => {
        document.getElementById('flashcards')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);

    } catch (error) {
      alert("Error: " + error);
    } finally {
      setLoading(false);
    }
  }

  const downloadPDF = async () => {
    if (!cardsRef.current || cards.length === 0) {
      alert("No cards to export!");
      return;
    }

    // Visual Feedback
    const btn = document.getElementById('btn-export-pdf');
    if (btn) btn.innerText = "Generating PDF...";

    try {
      const canvas = await html2canvas(cardsRef.current, {
        backgroundColor: '#191919',
        scale: 4, // Higher resolution (simulates ~300DPI)
        useCORS: true,
        logging: false
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      // If content is very long, we might need multiple pages, 
      // but for a simple grid image export, we'll fit width and let height expand/cutoff or multipage.
      // For simple "Download Image as PDF", a single page (custom height) or fit-to-page is common.
      // We'll stick to A4 fit width.

      if (pdfHeight > 297) {
        // If taller than A4, we need multiple pages or a custom page size. 
        // Simplest for "Visual Export" is to resize ONE LONG PAGE or Split.
        // Let's resize page to fit content to avoid cutting.
        pdf.deletePage(1);
        pdf.addPage([pdfWidth, pdfHeight + 20], 'p'); // Custom height page
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      } else {
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      }

      pdf.save(`flashdeck-${deckName || 'cards'}.pdf`);
    } catch (e) {
      console.error(e);
      alert("Export failed.");
    } finally {
      if (btn) btn.innerHTML = '<span class="flex items-center gap-2"><svg.../> PDF</span>'; // Basic revert or just...
      if (btn) btn.innerText = "Download PDF";
    }
  }

  const downloadImage = async (format = 'png') => {
    if (!cardsRef.current || cards.length === 0) {
      alert("No cards to export!");
      return;
    }

    try {
      const canvas = await html2canvas(cardsRef.current, {
        backgroundColor: '#191919',
        scale: 3, // High quality image
      });

      const link = document.createElement('a');
      link.download = `flashdeck-${deckName || 'cards'}.${format}`;
      link.href = canvas.toDataURL(`image/${format === 'jpg' ? 'jpeg' : 'png'}`);
      link.click();
    } catch (e) {
      alert("Export failed");
    }
  }

  return (
    <div className="min-h-screen bg-[#191919] text-gray-200 selection:bg-orange-500/30 font-sans">

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#191919]/80 backdrop-blur-md border-b border-white/5 h-14 flex items-center">
        <div className="mx-auto w-full max-w-5xl px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/10 p-1.5 rounded-md">
              <Zap size={16} className="text-orange-400" fill="currentColor" />
            </div>
            <span className="font-medium text-sm text-gray-200">FlashDeck AI</span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-white/5 text-gray-500 border border-white/5">BETA</span>
          </div>
          <div className="text-xs text-gray-500 font-mono">v1.1</div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="pt-24 pb-20">

        {/* Header Section */}
        <div className="mx-auto max-w-3xl px-6 mb-20 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-medium mb-6">
            <Sparkles size={12} />
            <span>AI-Powered Study Assistant</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-white mb-6">
            Master your notes. <br />
            <span className="text-gray-500">In seconds.</span>
          </h1>

          <p className="text-lg text-gray-400 max-w-lg mx-auto leading-relaxed">
            Drop your lecture slides, PDFs, or notes here. We'll turn them into spaced-repetition flashcards instantly.
          </p>
        </div>

        {/* Sticky Tabs Interface */}
        <div className="mx-auto max-w-5xl">
          <StickyTabs
            mainNavHeight="3.5rem"
            rootClassName="bg-transparent"
            navSpacerClassName="border-b border-white/5 bg-[#191919]/90 backdrop-blur-lg"
            sectionClassName="bg-transparent py-10"
            stickyHeaderContainerClassName="bg-[#191919]/95 backdrop-blur border-b border-white/5"
            titleClassName="text-sm font-medium text-gray-400 uppercase tracking-widest"
          >
            {/* STEP 1: UPLOAD */}
            <StickyTabs.Item title="Upload" id="upload">
              <div className="max-w-xl mx-auto">
                <div className="group relative transition-all duration-300 hover:scale-[1.01]">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500 to-purple-600 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>

                  <div className="relative bg-[#202020] rounded-xl border border-white/5 p-8 shadow-2xl">
                    <div className="flex flex-col items-center">
                      <div className="w-16 h-16 bg-[#2a2a2a] rounded-full flex items-center justify-center mb-6 shadow-inner ring-1 ring-white/5">
                        {file ? <FileText className="text-orange-400" /> : <Upload className="text-gray-500" />}
                      </div>

                      <h3 className="text-xl font-medium text-white mb-2">
                        {file ? file.name : "Upload PDF"}
                      </h3>

                      {/* Status / Progress */}
                      {file && uploadProgress < 100 ? (
                        <div className="w-full max-w-xs mt-2 mb-8">
                          <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Uploading...</span>
                            <span>{uploadProgress}%</span>
                          </div>
                          <div className="w-full bg-gray-700 h-1.5 rounded-full overflow-hidden">
                            <div
                              className="bg-orange-500 h-full transition-all duration-300 ease-out"
                              style={{ width: `${uploadProgress}%` }}
                            ></div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 text-center mb-8 max-w-xs">
                          {file ? "File ready. Click generate below." : "Drag and drop your lecture slides or click to browse files."}
                        </p>
                      )}

                      <div className="relative w-full">
                        <input
                          type="file"
                          accept=".pdf"
                          onChange={handleFileChange}
                          className={`absolute inset-0 w-full h-full opacity-0 z-20 ${file ? 'hidden' : 'cursor-pointer'}`}
                        />

                        {/* Main Action Button */}
                        <div className="relative">
                          {showGuide && (
                            <div className="absolute -top-14 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs font-bold px-3 py-1.5 rounded-full animate-bounce shadow-lg z-30 pointer-events-none">
                              Click Generate! 👇
                              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-indigo-600"></div>
                            </div>
                          )}

                          <button
                            disabled={!file || loading || uploadProgress < 100}
                            onClick={loading ? null : handleGenerate}
                            className={`w-full py-3 px-4 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2 relative z-10
                                ${file && uploadProgress === 100
                                ? 'bg-white text-black hover:bg-gray-100 shadow-[0_0_20px_rgba(255,255,255,0.3)] ring-2 ring-transparent hover:ring-indigo-500/50'
                                : 'bg-[#2a2a2a] text-gray-500 border border-white/5 hover:bg-[#333] cursor-pointer'}`}
                          >
                            {loading ? (
                              <span className="flex items-center gap-2">
                                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                                Processing...
                              </span>
                            ) : (
                              <span>{file ? "Generate Flashcards" : "Select File"}</span>
                            )}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </StickyTabs.Item>

            {/* STEP 2: FLASHCARDS */}
            <StickyTabs.Item title="Review" id="flashcards">
              {cards.length > 0 ? (
                <div>
                  <div ref={cardsRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 rounded-xl bg-[#191919]">
                    {cards.map((card, idx) => (
                      <div
                        key={idx}
                        onClick={() => setSelectedCard(card)}
                        className="group relative bg-[#202020] hover:bg-[#252525] border border-white/5 hover:border-orange-500/30 rounded-xl p-6 transition-all duration-200 cursor-pointer flex flex-col justify-between min-h-[220px] hover:-translate-y-1 hover:shadow-2xl"
                      >
                        <div>
                          <div className="flex items-center justify-between mb-4">
                            <span className="text-[10px] font-mono text-gray-600 border border-white/5 px-2 py-1 rounded-full tracking-wider">CARD {idx + 1}</span>
                            <div className="w-6 h-6 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-orange-500/20 transition-colors">
                              <Sparkles size={12} className="text-gray-600 group-hover:text-orange-400" />
                            </div>
                          </div>
                          <h3 className="text-base font-medium text-gray-100 leading-snug mb-3">
                            {card.q}
                          </h3>
                        </div>
                        <div className="relative mt-4 pt-4 border-t border-white/5">
                          <p className="text-sm text-gray-400/90 leading-relaxed select-none">
                            {card.a}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-24 text-gray-600">
                  <BookOpen size={48} className="mb-4 opacity-20" />
                  <p className="text-sm">No cards yet.</p>
                </div>
              )}
            </StickyTabs.Item>

            {/* STEP 3: EXPORT */}
            <StickyTabs.Item title="Export" id="export">
              <div className="pb-20">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-white mb-2">Export Your Deck</h2>
                  <p className="text-gray-500 text-sm">Choose a format to save your generated cards.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">

                  {/* Anki */}
                  <div className="bg-[#202020] border border-white/5 hover:border-blue-500/30 p-6 rounded-xl transition-all group hover:-translate-y-1">
                    <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4 text-blue-400">
                      <Download size={24} />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-2">Anki Package</h3>
                    <p className="text-xs text-gray-500 mb-6 min-h-[40px]">
                      Best for spaced repetition. Import directly into the Anki app.
                    </p>
                    <button className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors">
                      Download .apkg
                    </button>
                  </div>

                  {/* PDF */}
                  <div className="bg-[#202020] border border-white/5 hover:border-red-500/30 p-6 rounded-xl transition-all group hover:-translate-y-1">
                    <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center mb-4 text-red-400">
                      <FileText size={24} />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-2">Printable PDF</h3>
                    <p className="text-xs text-gray-500 mb-6 min-h-[40px]">
                      High-quality PDF for printing or reading on tablets.
                    </p>
                    <button
                      id="btn-export-pdf"
                      onClick={downloadPDF}
                      disabled={cards.length === 0}
                      className="w-full py-2 bg-[#2a2a2a] hover:bg-[#333] border border-white/10 text-gray-200 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Download PDF
                    </button>
                  </div>

                  {/* Image */}
                  <div className="bg-[#202020] border border-white/5 hover:border-purple-500/30 p-6 rounded-xl transition-all group hover:-translate-y-1">
                    <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4 text-purple-400">
                      <ImageIcon size={24} />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-2">Image Grid</h3>
                    <p className="text-xs text-gray-500 mb-6 min-h-[40px]">
                      Save as a high-res image (PNG) for quick sharing.
                    </p>
                    <button
                      onClick={() => downloadImage('png')}
                      disabled={cards.length === 0}
                      className="w-full py-2 bg-[#2a2a2a] hover:bg-[#333] border border-white/10 text-gray-200 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Download PNG
                    </button>
                  </div>

                </div>
              </div>
            </StickyTabs.Item>

          </StickyTabs>
        </div>
      </div>

      {/* MODAL OVERLAY (Same as before) -- Including full code to prevent truncation */}
      {selectedCard && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-[2px] animate-in fade-in duration-200"
          onClick={() => setSelectedCard(null)}
        >
          <div
            className="bg-[#1a1a1a] w-full max-w-2xl rounded-2xl border border-white/10 shadow-2xl p-0 overflow-hidden transform scale-100 opacity-100 transition-all"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between bg-[#202020]">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-orange-500/10 flex items-center justify-center">
                  <Brain size={16} className="text-orange-500" />
                </div>
                <span className="text-sm font-medium text-gray-300">Flashcard View</span>
              </div>
              <button onClick={() => setSelectedCard(null)} className="text-gray-500 hover:text-white transition-colors p-2 hover:bg-white/5 rounded-lg">
                <X size={20} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-10">
              <div className="mb-10">
                <span className="text-xs font-mono text-orange-400 mb-3 block tracking-widest uppercase">Question</span>
                <h2 className="text-2xl md:text-3xl font-bold text-white leading-tight">{selectedCard.q}</h2>
              </div>

              <div className="bg-[#252525] p-8 rounded-xl border border-white/5 relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-1 h-full bg-orange-500"></div>
                <span className="text-xs font-mono text-gray-500 mb-3 block tracking-widest uppercase">Answer</span>
                <p className="text-lg text-gray-300 leading-relaxed font-light">{selectedCard.a}</p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-8 py-4 bg-[#111] border-t border-white/5 flex justify-between items-center text-xs text-gray-600 font-mono">
              <span>Space Recall</span>
              <span>Press ESC to close</span>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}

export default App
