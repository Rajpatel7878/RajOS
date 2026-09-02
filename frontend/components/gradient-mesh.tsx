"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

interface MousePos { x: number; y: number }

export function GradientMesh({ className }: { className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [mouse, setMouse] = useState<MousePos>({ x: 0.5, y: 0.5 });

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      setMouse({
        x: (e.clientX - rect.left) / rect.width,
        y: (e.clientY - rect.top) / rect.height,
      });
    };
    window.addEventListener("mousemove", handleMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMove);
  }, []);

  const rotX = (mouse.y - 0.5) * -6;
  const rotY = (mouse.x - 0.5) * 6;

  return (
    <div
      ref={ref}
      className={className}
      aria-hidden
      style={{ perspective: "1200px" }}
    >
      {/* Deep background layer */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(14,165,233,0.12),transparent)]" />

      {/* 3D-reactive grid */}
      <div
        className="absolute inset-0 grid-bg opacity-[0.12]"
        style={{
          transform: `rotateX(${rotX * 0.3}deg) rotateY(${rotY * 0.3}deg)`,
          transition: "transform 0.3s ease-out",
        }}
      />

      {/* Orb 1 — Sky */}
      <motion.div
        className="absolute -top-1/4 left-1/4 h-[700px] w-[700px] rounded-full bg-sky-500/[0.18] blur-[140px]"
        animate={{ x: [0, 80, -40, 0], y: [0, 60, 30, 0], scale: [1, 1.1, 0.95, 1] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
        style={{
          transform: `translateX(${(mouse.x - 0.5) * -20}px) translateY(${(mouse.y - 0.5) * -20}px)`,
        }}
      />

      {/* Orb 2 — Cyan */}
      <motion.div
        className="absolute top-1/3 -right-1/4 h-[600px] w-[600px] rounded-full bg-cyan-500/[0.14] blur-[130px]"
        animate={{ x: [0, -60, 40, 0], y: [0, 40, -50, 0], scale: [1, 0.9, 1.15, 1] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
        style={{
          transform: `translateX(${(mouse.x - 0.5) * 25}px) translateY(${(mouse.y - 0.5) * 15}px)`,
        }}
      />

      {/* Orb 3 — Violet */}
      <motion.div
        className="absolute bottom-0 -left-1/4 h-[500px] w-[500px] rounded-full bg-violet-600/[0.1] blur-[120px]"
        animate={{ x: [0, 50, -30, 0], y: [0, -40, 20, 0] }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Orb 4 — Indigo (center depth) */}
      <motion.div
        className="absolute left-1/3 top-2/3 h-[350px] w-[350px] rounded-full bg-indigo-500/[0.08] blur-[100px]"
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Orb 5 — Emerald accent */}
      <motion.div
        className="absolute right-1/4 top-1/4 h-[200px] w-[200px] rounded-full bg-emerald-500/[0.07] blur-[80px]"
        animate={{ x: [0, -30, 30, 0], y: [0, 20, -20, 0] }}
        transition={{ duration: 15, repeat: Infinity, ease: "easeInOut", delay: 3 }}
      />

      {/* Aurora horizontal band */}
      <motion.div
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-sky-400/20 to-transparent"
        style={{ top: "30%" }}
        animate={{ opacity: [0, 0.6, 0], scaleX: [0.5, 1, 0.5] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-400/15 to-transparent"
        style={{ top: "60%" }}
        animate={{ opacity: [0, 0.4, 0], scaleX: [0.3, 1, 0.3] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      />

      {/* Bottom vignette */}
      <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/40 to-transparent pointer-events-none" />
    </div>
  );
}
