import { Hero } from '../components/ui/hero'
import { Sparkles, Zap, Brain, Upload } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-[#191919] text-gray-200 font-sans flex flex-col">
            {/* Navbar */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-[#191919]/80 backdrop-blur-md border-b border-white/5 h-16 flex items-center">
                <div className="mx-auto w-full max-w-7xl px-6 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="bg-white/10 p-1.5 rounded-md">
                            <Zap size={18} className="text-orange-400" fill="currentColor" />
                        </div>
                        <span className="font-bold text-lg text-white tracking-tight">FlashDeck AI</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Link to="/app">
                            <Button className="bg-white text-black hover:bg-gray-200">
                                Launch App
                            </Button>
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <div className="flex-1 flex flex-col items-center justify-center pt-20">
                <Hero
                    title="Master your notes. In seconds."
                    subtitle="Transform your PDFs, slides, and handwritten notes into active recall flashcards. Now with AI Chat and Visual Concept Maps."
                    actions={[
                        { label: "Get Started Free", href: "/app", variant: "default" },
                        { label: "View Components", href: "#features", variant: "outline" } // Adjusted href
                    ]}
                />
            </div>

            {/* Features Grid */}
            <div id="features" className="py-24 bg-[#111]">
                <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-12">
                    <FeatureCard
                        icon={<Upload className="text-blue-400" />}
                        title="Multi-File Upload"
                        desc="Drop in your entire semester's slide decks. We process them in parallel."
                    />
                    <FeatureCard
                        icon={<Brain className="text-orange-400" />}
                        title="RAG Chatbot"
                        desc="Ask questions to your documents. Our AI cites sources from your uploaded files."
                    />
                    <FeatureCard
                        icon={<Sparkles className="text-purple-400" />}
                        title="Visual Learning"
                        desc="Automatically generate flowcharts and diagrams to visualize complex topics."
                    />
                </div>
            </div>
        </div>
    )
}

function FeatureCard({ icon, title, desc }) {
    return (
        <div className="p-6 rounded-2xl bg-[#191919] border border-white/5 hover:border-white/10 transition-colors">
            <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center mb-4">
                {icon}
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
            <p className="text-gray-400 leading-relaxed">{desc}</p>
        </div>
    )
}
