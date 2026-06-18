// TODO Phase 5 — implement full chat interface
// Flow: user types mood → POST /api/recommend → stream back emotion + 3 songs
// Each song shows: track name, artist, emotion label, valence/energy, Spotify link

export default function ChatInterface() {
  return (
    <div className="w-full max-w-2xl flex flex-col gap-4">
      <header className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight">🎵 Music Mood Therapy</h1>
        <p className="text-gray-400 text-sm mt-1">Tell me how you feel. I'll find your path.</p>
      </header>

      {/* Placeholder — Phase 5 */}
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-6 text-gray-500 text-sm text-center">
        Frontend coming in Phase 5 — run the CLI first
      </div>
    </div>
  )
}
