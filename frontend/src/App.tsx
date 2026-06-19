import { useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import MoodInput from './components/MoodInput'
import ResultsPanel from './components/ResultsPanel'
import { useRecommend } from './hooks/useRecommend'
import { emotionColor, emotionBg, DEFAULT_ACCENT } from './lib/emotions'

function Header() {
  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs font-mono tracking-[0.25em] uppercase text-slate-400">
        Music Mood Therapy
      </span>
      <h1 className="font-display text-4xl text-slate-900 leading-tight">
        Tell me how you feel.
      </h1>
      <p className="text-base text-slate-500 font-sans mt-1 leading-relaxed">
        I'll map three songs that move you from where you are
        toward a better place.
      </p>
    </div>
  )
}

export default function App() {
  const { result, loading, error, recommend, reset } = useRecommend()
  const resultsRef = useRef<HTMLDivElement>(null)

  const accent = result ? emotionColor(result.emotion) : DEFAULT_ACCENT
  const pageBg  = result ? emotionBg(result.emotion)   : 'transparent'

  // Scroll results into view smoothly
  useEffect(() => {
    if (result && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [result])

  return (
    // Very soft page tint shifts when emotion is detected
    <div
      className="min-h-screen transition-colors duration-700"
      style={{ background: `linear-gradient(160deg, #fdfcff 0%, ${pageBg === 'transparent' ? '#f3f0fb' : pageBg} 100%)` }}
    >
      {/* Subtle decorative top stripe in accent colour */}
      <div
        className="h-1 w-full transition-colors duration-700"
        style={{ backgroundColor: accent }}
      />

      <main className="max-w-xl mx-auto px-5 py-14 flex flex-col gap-10">
        <Header />

        <MoodInput onSubmit={recommend} loading={loading} accentColor={accent} />

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="text-sm font-sans text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {result && (
            <div ref={resultsRef}>
              <ResultsPanel result={result} onReset={reset} />
            </div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="text-center pb-10">
        <p className="text-xs text-slate-300 font-mono">
          ISO Principle · Russell's Circumplex · GPT-4o-mini
        </p>
      </footer>
    </div>
  )
}
