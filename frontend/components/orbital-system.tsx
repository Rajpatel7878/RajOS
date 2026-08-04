'use client';

import { motion } from 'framer-motion';
import { Brain, Cpu, Database, Workflow, Zap, Shield } from 'lucide-react';

const orbits = [
  {
    radius: 90,
    duration: 20,
    nodes: [
      { icon: Cpu, color: 'text-sky-400', bg: 'from-sky-500/20 to-blue-500/5' },
      { icon: Database, color: 'text-cyan-400', bg: 'from-cyan-500/20 to-teal-500/5' },
    ],
  },
  {
    radius: 150,
    duration: 30,
    nodes: [
      { icon: Workflow, color: 'text-emerald-400', bg: 'from-emerald-500/20 to-green-500/5' },
      { icon: Zap, color: 'text-amber-400', bg: 'from-amber-500/20 to-orange-500/5' },
    ],
  },
  {
    radius: 210,
    duration: 40,
    nodes: [
      { icon: Shield, color: 'text-rose-400', bg: 'from-rose-500/20 to-pink-500/5' },
      { icon: Brain, color: 'text-violet-400', bg: 'from-violet-500/20 to-purple-500/5' },
    ],
  },
];

function OrbitalNode({
  icon: Icon,
  color,
  bg,
  angle,
  radius,
  duration,
  reverse,
}: {
  icon: typeof Cpu;
  color: string;
  bg: string;
  angle: number;
  radius: number;
  duration: number;
  reverse?: boolean;
}) {
  return (
    <div
      className="absolute left-1/2 top-1/2"
      style={{ transform: `rotate(${angle}deg) translateX(${radius}px)` }}
    >
      <motion.div
        animate={{ rotate: reverse ? duration : -duration }}
        transition={{ duration, repeat: Infinity, ease: 'linear' }}
        style={{ transformOrigin: 'center' }}
      >
        <motion.div
          animate={{ rotate: reverse ? -duration : duration }}
          transition={{ duration, repeat: Infinity, ease: 'linear' }}
        >
          <div
            className={`flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-gradient-to-br ${bg} backdrop-blur-md`}
            style={{ transform: `translate(-50%, -50%)` }}
          >
            <Icon className={`h-5 w-5 ${color}`} />
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

export function OrbitalSystem({ className }: { className?: string }) {
  return (
    <div className={className} aria-hidden>
      {/* Glow */}
      <div className="absolute left-1/2 top-1/2 h-32 w-32 -translate-x-1/2 -translate-y-1/2 rounded-full bg-sky-500/30 blur-[80px]" />
      <div className="absolute left-1/2 top-1/2 h-20 w-20 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/20 blur-[50px]" />

      {/* Orbital rings */}
      {orbits.map((orbit) => (
        <div
          key={orbit.radius}
          className="absolute left-1/2 top-1/2 rounded-full border border-white/[0.06]"
          style={{
            width: orbit.radius * 2,
            height: orbit.radius * 2,
            transform: 'translate(-50%, -50%)',
          }}
        />
      ))}

      {/* Orbiting nodes */}
      {orbits.map((orbit) =>
        orbit.nodes.map((node, ni) => (
          <motion.div
            key={`${orbit.radius}-${ni}`}
            className="absolute left-1/2 top-1/2"
            animate={{ rotate: ni === 0 ? 360 : -360 }}
            transition={{
              duration: orbit.duration,
              repeat: Infinity,
              ease: 'linear',
            }}
            style={{ transformOrigin: 'center' }}
          >
            <OrbitalNode
              icon={node.icon}
              color={node.color}
              bg={node.bg}
              angle={ni === 0 ? 0 : 180}
              radius={orbit.radius}
              duration={orbit.duration}
              reverse={ni === 0}
            />
          </motion.div>
        ))
      )}

      {/* Central core */}
      <motion.div
        className="absolute left-1/2 top-1/2"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        style={{ transform: 'translate(-50%, -50%)' }}
      >
        <div className="relative flex h-20 w-20 items-center justify-center">
          {/* Pulse rings */}
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="absolute inset-0 rounded-full border border-sky-400/30"
              animate={{ scale: [1, 2], opacity: [0.5, 0] }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'easeOut',
                delay: i,
              }}
            />
          ))}
          {/* Core */}
          <div className="relative flex h-20 w-20 items-center justify-center rounded-2xl border border-sky-400/20 bg-gradient-to-br from-sky-500/30 via-cyan-500/20 to-blue-600/10 backdrop-blur-xl">
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-sky-400/20 to-transparent" />
            <Brain className="relative h-9 w-9 text-white drop-shadow-[0_0_8px_rgba(56,189,248,0.8)]" />
          </div>
        </div>
      </motion.div>

      {/* Data flow lines — animated dashes */}
      <svg className="absolute inset-0 h-full w-full" style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id="flow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#38bdf8" stopOpacity="0" />
            <stop offset="50%" stopColor="#22d3ee" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
          </linearGradient>
        </defs>
        {orbits.map((orbit) => (
          <motion.circle
            key={`dash-${orbit.radius}`}
            cx="50%"
            cy="50%"
            r={orbit.radius}
            fill="none"
            stroke="url(#flow-grad)"
            strokeWidth={1}
            strokeDasharray="4 12"
            animate={{ strokeDashoffset: [0, -32] }}
            transition={{
              duration: orbit.duration / 3,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        ))}
      </svg>
    </div>
  );
}
