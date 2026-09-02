'use client';

import { useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

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
  gradient?: 'sky' | 'cyan' | 'violet' | 'emerald' | 'indigo';
}) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = cardRef.current;
    if (!el || !hover) return;
    const rect = el.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    el.style.setProperty('--tx', `${x * 4}deg`);
    el.style.setProperty('--ty', `${y * -4}deg`);
  }, [hover]);

  const handleMouseLeave = useCallback(() => {
    const el = cardRef.current;
    if (!el) return;
    el.style.setProperty('--tx', '0deg');
    el.style.setProperty('--ty', '0deg');
  }, []);

  const gradientMap: Record<string, string> = {
    sky: 'from-sky-500/[0.07] via-transparent to-transparent',
    cyan: 'from-cyan-400/[0.07] via-transparent to-transparent',
    violet: 'from-violet-500/[0.07] via-transparent to-transparent',
    emerald: 'from-emerald-400/[0.07] via-transparent to-transparent',
    indigo: 'from-indigo-500/[0.07] via-transparent to-transparent',
  };

  const glowMap: Record<string, string> = {
    sky: 'glow-sky',
    cyan: 'glow-cyan',
    violet: 'glow-violet',
    emerald: 'glow-emerald',
    indigo: 'glow-violet',
  };

  return (
    <div
      className="card-3d"
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
        style={
          {
            '--tx': '0deg',
            '--ty': '0deg',
            transform: hover
              ? 'perspective(1200px) rotateX(var(--ty)) rotateY(var(--tx))'
              : undefined,
            transition: 'transform 0.15s ease, box-shadow 0.25s ease',
          } as React.CSSProperties
        }
        className={cn(
          'group card-3d-inner relative overflow-hidden rounded-2xl border border-white/[0.08] backdrop-blur-xl',
          gradient
            ? `bg-gradient-to-br ${gradientMap[gradient]}`
            : 'bg-gradient-to-b from-white/[0.05] to-white/[0.01]',
          glow && gradient && glowMap[gradient],
          hover && 'transition-shadow hover:shadow-2xl hover:shadow-sky-500/10 hover:-translate-y-1',
          className
        )}
      >
        {/* Hover glow overlay */}
        {hover && (
          <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100">
            <div className="absolute -top-1/2 left-1/2 h-full w-2/3 -translate-x-1/2 rounded-full bg-sky-500/10 blur-3xl" />
          </div>
        )}
        {/* Gradient tint overlay */}
        {gradient && (
          <div
            className={cn(
              'pointer-events-none absolute inset-0 rounded-2xl opacity-60',
              `bg-gradient-to-br ${gradientMap[gradient]}`
            )}
          />
        )}
        <div className="relative">{children}</div>
      </motion.div>
    </div>
  );
}
