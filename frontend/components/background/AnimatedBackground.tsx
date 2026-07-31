"use client";

import FloatingParticles from "./FloatingParticles";

export default function AnimatedBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">

      <FloatingParticles />

      <div className="absolute left-1/4 top-20 h-96 w-96 rounded-full bg-indigo-500/20 blur-3xl animate-pulse" />

      <div className="absolute right-1/4 top-1/3 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl animate-glow" />

      <div className="absolute bottom-20 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-violet-500/20 blur-3xl animate-float" />

    </div>
  );
}
