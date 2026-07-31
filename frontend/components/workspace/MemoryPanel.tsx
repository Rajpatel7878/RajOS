"use client";

import { Brain, User, Sparkles } from "lucide-react";

export default function MemoryPanel() {
  return (
    <div className="rounded-2xl border border-white/10 hover-glow transition-all duration-300 bg-white/5 p-5 backdrop-blur-xl">

      <div className="mb-5 flex items-center gap-3">
        <Brain className="h-6 w-6 text-violet-400" />

        <h3 className="font-semibold text-white">
          AI Memory
        </h3>
      </div>


      <div className="space-y-4">

        <div className="flex items-center gap-3 rounded-xl bg-black/20 p-3">
          <User className="text-cyan-400" />

          <div>
            <p className="text-sm text-white">
              Raj prefers short answers
            </p>
            <p className="text-xs text-slate-500">
              User preference
            </p>
          </div>
        </div>


        <div className="flex items-center gap-3 rounded-xl bg-black/20 p-3">
          <Sparkles className="text-violet-400" />

          <div>
            <p className="text-sm text-white">
              Python + FastAPI
            </p>
            <p className="text-xs text-slate-500">
              Favorite technology
            </p>
          </div>
        </div>


      </div>

    </div>
  );
}
