"use client";

import { useRef, useCallback, useState, type ReactNode } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export function GlassCard({
  children,
  className,
  hover = true,
  delay = 0,
  glow = true,
  gradient,
}: {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  delay?: number;
  glow?: boolean;
  gradient?: "sky" | "cyan" | "violet" | "emerald" | "indigo" | "amber" | "rose";
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState<{ x: number; y: number }>({ x: 50, y: 50 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const el = cardRef.current;
      if (!el || !hover) return;
      const rect = el.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;

      // 3D Tilt angles (max 6 degrees for subtle premium feel)
      const rotY = (x - 0.5) * 8;
      const rotX = (y - 0.5) * -8;

      el.style.setProperty("--rot-x", `${rotX}deg`);
      el.style.setProperty("--rot-y", `${rotY}deg`);
      el.style.setProperty("--mouse-x", `${x * 100}%`);
      el.style.setProperty("--mouse-y", `${y * 100}%`);

      setCoords({ x: x * 100, y: y * 100 });
      setIsHovered(true);
    },
    [hover]
  );

  const handleMouseLeave = useCallback(() => {
    const el = cardRef.current;
    if (!el) return;
    el.style.setProperty("--rot-x", "0deg");
    el.style.setProperty("--rot-y", "0deg");
    setIsHovered(false);
  }, []);

  const gradientMap: Record<string, string> = {
    sky: "from-sky-500/[0.08] via-sky-500/[0.02] to-transparent",
    cyan: "from-cyan-400/[0.08] via-cyan-400/[0.02] to-transparent",
    violet: "from-violet-500/[0.08] via-violet-500/[0.02] to-transparent",
    emerald: "from-emerald-400/[0.08] via-emerald-400/[0.02] to-transparent",
    indigo: "from-indigo-500/[0.08] via-indigo-500/[0.02] to-transparent",
    amber: "from-amber-500/[0.08] via-amber-500/[0.02] to-transparent",
    rose: "from-rose-500/[0.08] via-rose-500/[0.02] to-transparent",
  };

  const glowMap: Record<string, string> = {
    sky: "glow-sky",
    cyan: "glow-cyan",
    violet: "glow-violet",
    emerald: "glow-emerald",
    indigo: "glow-violet",
    amber: "glow-amber",
    rose: "glow-violet",
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="card-3d relative"
      style={{ perspective: "1000px" }}
    >
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay, ease: [0.16, 1, 0.3, 1] }}
        style={{
          transform: hover
            ? "rotateX(var(--rot-x, 0deg)) rotateY(var(--rot-y, 0deg))"
            : undefined,
          transformStyle: "preserve-3d",
          transition: "transform 0.16s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.3s ease, border-color 0.3s ease",
        }}
        className={cn(
          "group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-black/40 backdrop-blur-2xl",
          gradient
            ? `bg-gradient-to-br ${gradientMap[gradient]}`
            : "bg-gradient-to-b from-white/[0.05] via-white/[0.02] to-black/30",
          glow && gradient && glowMap[gradient],
          hover &&
            "hover:border-white/20 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7),0_0_25px_rgba(56,189,248,0.12)]",
          className
        )}
      >
        {/* ── Real-time Specular Light Sheen (Follows Mouse Cursor) ── */}
        {hover && (
          <div
            className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100 z-10"
            style={{
              background: `radial-gradient(450px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255, 255, 255, 0.08), transparent 70%)`,
            }}
          />
        )}

        {/* ── Top edge high-light beam ── */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />

        {/* ── Inner content with subtle 3D pop ── */}
        <div
          className="relative z-20"
          style={{ transform: hover && isHovered ? "translateZ(8px)" : "translateZ(0px)", transition: "transform 0.2s ease" }}
        >
          {children}
        </div>
      </motion.div>
    </div>
  );
}
