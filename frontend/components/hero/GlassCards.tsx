"use client";

import { FileText, CheckCircle, Brain } from "lucide-react";

export default function GlassCards() {
  return (
    <div className="absolute inset-0 pointer-events-none">

      <div className="absolute -left-8 top-1/2 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl shadow-xl">
        <FileText className="mb-2 h-6 w-6 text-cyan-300" />
        <p className="text-sm font-semibold text-white">
          Smart Notes
        </p>
        <p className="text-xs text-slate-400">
          AI organized
        </p>
      </div>

      <div className="absolute -right-8 bottom-1/3 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl shadow-xl">
        <CheckCircle className="mb-2 h-6 w-6 text-green-400" />
        <p className="text-sm font-semibold text-white">
          Tasks Done
        </p>
        <p className="text-xs text-slate-400">
          Productivity boosted
        </p>
      </div>

      <div className="absolute right-12 top-10 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl shadow-xl">
        <Brain className="mb-2 h-6 w-6 text-violet-400" />
        <p className="text-sm font-semibold text-white">
          AI Memory
        </p>
        <p className="text-xs text-slate-400">
          Learns your habits
        </p>
      </div>

    </div>
  );
}
