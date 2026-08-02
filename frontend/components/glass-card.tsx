'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

export function GlassCard({
  children,
  className,
  hover = true,
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={
        hover
          ? {
              y: -4,
              transition: { duration: 0.25, ease: 'easeOut' },
            }
          : undefined
      }
      className={cn(
        'group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.05] to-white/[0.01] backdrop-blur-xl',
        hover && 'transition-shadow hover:shadow-2xl hover:shadow-sky-500/5',
        className
      )}
    >
      {/* hover glow */}
      {hover && (
        <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-500 group-hover:opacity-100">
          <div className="absolute -top-1/2 left-1/2 h-full w-2/3 -translate-x-1/2 rounded-full bg-sky-500/10 blur-3xl" />
        </div>
      )}
      <div className="relative">{children}</div>
    </motion.div>
  );
}
