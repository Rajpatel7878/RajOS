"use client";

import {
  Bot,
  Sparkles,
  Brain,
} from "lucide-react";

export default function AIDemoSection() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">

      <div className="text-center">

        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
          AI ENGINE
        </p>

        <h2 className="text-gradient text-4xl font-bold md:text-6xl">
          Experience The Intelligence Behind RajOS
        </h2>

      </div>


      <div className="mt-16 grid gap-8 md:grid-cols-3">

        <div className="glass rounded-3xl p-8 hover-glow">
          <Bot className="mb-5 h-10 w-10 text-cyan-400" />

          <h3 className="text-xl font-bold text-white">
            AI Assistant
          </h3>

          <p className="mt-3 text-slate-400">
            Chat, plan and automate your daily workflow.
          </p>
        </div>


        <div className="glass rounded-3xl p-8 hover-glow">
          <Brain className="mb-5 h-10 w-10 text-violet-400" />

          <h3 className="text-xl font-bold text-white">
            AI Memory
          </h3>

          <p className="mt-3 text-slate-400">
            RajOS learns your preferences over time.
          </p>
        </div>


        <div className="glass rounded-3xl p-8 hover-glow">
          <Sparkles className="mb-5 h-10 w-10 text-cyan-300" />

          <h3 className="text-xl font-bold text-white">
            Smart Automation
          </h3>

          <p className="mt-3 text-slate-400">
            Turn repetitive tasks into intelligent workflows.
          </p>
        </div>


      </div>

    </section>
  );
}
