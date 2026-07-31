"use client";

import { BrainCircuit, Sparkles } from "lucide-react";
import FloatingCards from "./FloatingCards";
import GlassCards from "./GlassCards";

export default function HeroVisual() {
  return (
    <div className="relative flex h-[500px] w-full items-center justify-center">

      <FloatingCards />

      <GlassCards />

      <div className="absolute h-80 w-80 rounded-full bg-gradient-to-r from-indigo-500/30 via-violet-500/30 to-cyan-500/30 blur-3xl animate-glow" />

      <div className="absolute h-72 w-72 rounded-full border border-cyan-400/20 animate-spin [animation-duration:20s]" />

      <div className="relative flex h-64 w-64 items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl shadow-2xl glow animate-float">

        <div className="absolute -top-4 -right-4 rounded-full bg-cyan-400/20 p-3 backdrop-blur-xl">
          <Sparkles className="h-5 w-5 text-cyan-300" />
        </div>

        <BrainCircuit className="h-28 w-28 text-cyan-300" />

      </div>

    </div>
  );
}
