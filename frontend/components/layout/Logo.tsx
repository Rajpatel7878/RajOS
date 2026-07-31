"use client";

import Link from "next/link";
import { BrainCircuit } from "lucide-react";

export default function Logo() {
  return (
    <Link
      href="/"
      className="flex items-center gap-3 transition-all duration-300 hover:scale-105"
    >
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 via-violet-600 to-cyan-500 shadow-lg shadow-cyan-500/30 glow">
        <BrainCircuit className="h-6 w-6 text-white" />
      </div>

      <div>
        <h2 className="text-xl font-bold text-white">RajOS</h2>
        <p className="text-xs text-slate-400">
          AI Productivity Workspace
        </p>
      </div>
    </Link>
  );
}
