'use client';

import { motion } from 'framer-motion';
import * as Icons from 'lucide-react';
import { cn } from '@/lib/utils';
import { AnimatedCounter } from '@/components/animated-counter';
import type { StatCard as StatCardType } from '@/lib/types';

export function StatCard({ stat, delay = 0 }: { stat: StatCardType; delay?: number }) {
  const Icon = (Icons as Record<string, Icons.LucideIcon>)[stat.icon] ?? Icons.Activity;
  const numericValue = parseFloat(stat.value.replace(/[^0-9.]/g, ''));
  const hasDecimal = stat.value.includes('.');
  const prefix = stat.value.match(/^[^0-9]*/)?.[0] ?? '';
  const suffix = stat.value.match(/[^0-9.]*$/)?.[0] ?? '';

  const maxSpark = Math.max(...stat.sparkline);
  const points = stat.sparkline
    .map((v, i) => `${(i / (stat.sparkline.length - 1)) * 100},${30 - (v / maxSpark) * 26 - 2}`)
    .join(' ');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4, transition: { duration: 0.25 } }}
      className="group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.05] to-white/[0.01] p-5 backdrop-blur-xl transition-shadow hover:shadow-2xl hover:shadow-sky-500/5"
    >
      <div className="pointer-events-none absolute -top-12 right-0 h-32 w-32 rounded-full bg-sky-500/10 opacity-0 blur-3xl transition-opacity duration-500 group-hover:opacity-100" />
      <div className="relative flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-sky-400/20 bg-sky-400/10">
          <Icon className="h-5 w-5 text-sky-400" />
        </div>
        <div
          className={cn(
            'flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold',
            stat.trend === 'up'
              ? 'bg-emerald-500/10 text-emerald-400'
              : stat.trend === 'down'
                ? 'bg-red-500/10 text-red-400'
                : 'bg-white/5 text-muted-foreground'
          )}
        >
          {stat.trend === 'up' && <Icons.TrendingUp className="h-3 w-3" />}
          {stat.trend === 'down' && <Icons.TrendingDown className="h-3 w-3" />}
          {stat.change}
        </div>
      </div>
      <div className="relative mt-4">
        <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
        <p className="mt-1 text-2xl font-bold tracking-tight text-white">
          <AnimatedCounter
            value={numericValue}
            decimals={hasDecimal ? 1 : 0}
            prefix={prefix}
            suffix={suffix}
          />
        </p>
      </div>
      <div className="relative mt-3 h-8 w-full">
        <svg viewBox="0 0 100 30" preserveAspectRatio="none" className="h-full w-full">
          <defs>
            <linearGradient id={`spark-${stat.id}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(199 89% 56%)" stopOpacity="0.3" />
              <stop offset="100%" stopColor="hsl(199 89% 56%)" stopOpacity="0" />
            </linearGradient>
          </defs>
          <polygon
            points={`0,30 ${points} 100,30`}
            fill={`url(#spark-${stat.id})`}
          />
          <motion.polyline
            points={points}
            fill="none"
            stroke="hsl(199 89% 56%)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, delay: delay + 0.3, ease: 'easeInOut' }}
          />
        </svg>
      </div>
    </motion.div>
  );
}
