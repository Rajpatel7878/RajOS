"use client";

import { Bot, Send } from "lucide-react";

export default function AIChatPanel() {
  return (
    <div className="rounded-2xl border border-white/10 hover-glow transition-all duration-300 bg-white/5 p-5 backdrop-blur-xl">

      <div className="mb-4 flex items-center gap-3">
        <Bot className="h-6 w-6 text-cyan-400" />

        <h3 className="font-semibold text-white">
          AI Assistant
        </h3>
      </div>


      <div className="space-y-3">

        <div className="rounded-xl bg-black/30 p-3 text-sm text-slate-300">
          Hello Raj 👋 How can I help today?
        </div>


        <div className="rounded-xl bg-cyan-500/10 p-3 text-sm text-cyan-200">
          Create a productivity plan for me.
        </div>


        <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-black/20 p-3">
          <span className="flex-1 text-sm text-slate-500">
            Ask AI anything...
          </span>

          <Send className="h-5 w-5 text-cyan-400" />
        </div>

      </div>

    </div>
  );
}
