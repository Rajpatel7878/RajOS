'use client';

import { motion } from 'framer-motion';

export function GradientMesh({ className }: { className?: string }) {
  return (
    <div className={className} aria-hidden>
      <div className="absolute inset-0 grid-bg opacity-[0.15]" />
      <motion.div
        className="absolute -top-1/4 left-1/4 h-[600px] w-[600px] rounded-full bg-sky-500/20 blur-[120px]"
        animate={{
          x: [0, 80, -40, 0],
          y: [0, 60, 30, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute top-1/3 -right-1/4 h-[500px] w-[500px] rounded-full bg-cyan-500/15 blur-[120px]"
        animate={{
          x: [0, -60, 40, 0],
          y: [0, 40, -50, 0],
          scale: [1, 0.9, 1.15, 1],
        }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-0 left-1/3 h-[400px] w-[400px] rounded-full bg-blue-600/10 blur-[100px]"
        animate={{
          x: [0, 50, -30, 0],
          y: [0, -40, 20, 0],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  );
}
