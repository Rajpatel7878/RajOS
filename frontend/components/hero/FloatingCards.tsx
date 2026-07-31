"use client";

export default function FloatingCards() {
  return (
    <>
      <div className="absolute left-10 top-24 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-xl animate-float">
        <p className="text-sm text-cyan-300">🧠 Memory</p>
        <p className="text-xs text-slate-400">AI remembers you</p>
      </div>

      <div className="absolute bottom-24 right-10 rounded-2xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-xl animate-float">
        <p className="text-sm text-indigo-300">⚡ Productivity</p>
        <p className="text-xs text-slate-400">Smart workflow</p>
      </div>
    </>
  );
}
