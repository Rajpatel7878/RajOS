'use client';

import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BrainCircuit,
  Database,
  Zap,
  Clock,
  Target,
  Award,
  Cpu,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { AnimatedCounter } from '@/components/animated-counter';
import { cn } from '@/lib/utils';
import {
  usageChart,
  memoryGrowthChart,
  knowledgeGrowthChart,
  productivityChart,
  interactionHistory,
  llmDistribution,
} from '@/lib/data';

const summaryStats = [
  { label: 'Total Interactions', value: 94521, suffix: '', change: '+31.5%', trend: 'up', icon: Activity, color: 'text-sky-400' },
  { label: 'Memory Items', value: 8206, suffix: '', change: '+12.4%', trend: 'up', icon: BrainCircuit, color: 'text-cyan-400' },
  { label: 'Knowledge Docs', value: 2318, suffix: '', change: '+8.1%', trend: 'up', icon: Database, color: 'text-emerald-400' },
  { label: 'Tasks Automated', value: 5885, suffix: '', change: '+24.6%', trend: 'up', icon: Zap, color: 'text-amber-400' },
];

const topMetrics = [
  { label: 'Productivity Score', value: 94.2, suffix: '/100', icon: Award, color: 'text-sky-400', pct: 94 },
  { label: 'Task Accuracy', value: 97.4, suffix: '%', icon: Target, color: 'text-emerald-400', pct: 97 },
  { label: 'Avg Response Time', value: 1.2, suffix: 's', icon: Clock, color: 'text-cyan-400', pct: 88 },
  { label: 'LLM Efficiency', value: 89.6, suffix: '%', icon: Cpu, color: 'text-violet-400', pct: 90 },
];

export default function AnalyticsPage() {
  return (
    <AppShell>
      {/* Summary stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {summaryStats.map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.06} className="p-5">
            <div className="flex items-center justify-between">
              <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]', stat.color)}>
                <stat.icon className="h-5 w-5" />
              </div>
              <span className={cn(
                'flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold',
                stat.trend === 'up' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
              )}>
                {stat.trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                {stat.change}
              </span>
            </div>
            <p className="mt-4 text-2xl font-bold text-white">
              <AnimatedCounter value={stat.value} suffix={stat.suffix} />
            </p>
            <p className="text-sm text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Top metrics with radial */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {topMetrics.map((m, i) => (
          <GlassCard key={m.label} delay={i * 0.06} className="flex items-center gap-4 p-5">
            <div className="relative h-16 w-16 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  innerRadius="70%"
                  outerRadius="100%"
                  data={[{ value: m.pct }]}
                  startAngle={90}
                  endAngle={-270}
                >
                  <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                  <RadialBar
                    dataKey="value"
                    cornerRadius={8}
                    fill={`hsl(${199 - i * 10} 89% 56%)`}
                    background={{ fill: 'hsl(222 18% 12%)' }}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex items-center justify-center">
                <m.icon className={cn('h-5 w-5', m.color)} />
              </div>
            </div>
            <div>
              <p className="text-xl font-bold text-white">
                {m.value}
                <span className="text-sm font-normal text-muted-foreground">{m.suffix}</span>
              </p>
              <p className="text-xs text-muted-foreground">{m.label}</p>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Growth charts */}
      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <GlassCard hover={false} delay={0.1}>
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">Memory Growth</h3>
            <p className="text-sm text-muted-foreground">Long-term memory items over time</p>
          </div>
          <div className="h-[240px] w-full p-4 pl-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={memoryGrowthChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="gMemory" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(280 83% 62%)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="hsl(280 83% 62%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 18% 16%)" vertical={false} />
                <XAxis dataKey="month" stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: 'hsl(222 24% 6%)', border: '1px solid hsl(222 18% 16%)', borderRadius: '12px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="items" stroke="hsl(280 83% 62%)" strokeWidth={2} fill="url(#gMemory)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard hover={false} delay={0.15}>
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">Knowledge Expansion</h3>
            <p className="text-sm text-muted-foreground">Indexed documents over time</p>
          </div>
          <div className="h-[240px] w-full p-4 pl-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={knowledgeGrowthChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="gKnowledge" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(142 71% 45%)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="hsl(142 71% 45%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 18% 16%)" vertical={false} />
                <XAxis dataKey="month" stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: 'hsl(222 24% 6%)', border: '1px solid hsl(222 18% 16%)', borderRadius: '12px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="docs" stroke="hsl(142 71% 45%)" strokeWidth={2} fill="url(#gKnowledge)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Usage + productivity */}
      <div className="mb-6 grid gap-6 lg:grid-cols-3">
        <GlassCard hover={false} delay={0.2} className="lg:col-span-2">
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">Weekly Usage Breakdown</h3>
            <p className="text-sm text-muted-foreground">AI interactions by type across the week</p>
          </div>
          <div className="h-[280px] w-full p-4 pl-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={usageChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 18% 16%)" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: 'hsl(222 24% 6%)', border: '1px solid hsl(222 18% 16%)', borderRadius: '12px', fontSize: '12px' }}
                  cursor={{ fill: 'hsl(222 18% 16% / 0.3)' }}
                />
                <Bar dataKey="chat" stackId="a" fill="hsl(199 89% 56%)" radius={[0, 0, 0, 0]} />
                <Bar dataKey="agents" stackId="a" fill="hsl(189 94% 50%)" radius={[0, 0, 0, 0]} />
                <Bar dataKey="memory" stackId="a" fill="hsl(280 83% 62%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard hover={false} delay={0.25}>
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">Productivity Trend</h3>
            <p className="text-sm text-muted-foreground">8-week rolling score</p>
          </div>
          <div className="h-[280px] w-full p-4 pl-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={productivityChart} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 18% 16%)" vertical={false} />
                <XAxis dataKey="week" stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} domain={[60, 100]} />
                <Tooltip
                  contentStyle={{ background: 'hsl(222 24% 6%)', border: '1px solid hsl(222 18% 16%)', borderRadius: '12px', fontSize: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="hsl(199 89% 56%)"
                  strokeWidth={2.5}
                  dot={{ fill: 'hsl(199 89% 56%)', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Interaction history + LLM usage */}
      <div className="grid gap-6 lg:grid-cols-3">
        <GlassCard hover={false} delay={0.3} className="lg:col-span-2">
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">AI Interaction History</h3>
            <p className="text-sm text-muted-foreground">Hourly interaction volume (last 24h)</p>
          </div>
          <div className="h-[240px] w-full p-4 pl-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={interactionHistory} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="gInteract" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(38 92% 56%)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="hsl(38 92% 56%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 18% 16%)" vertical={false} />
                <XAxis dataKey="hour" stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{ background: 'hsl(222 24% 6%)', border: '1px solid hsl(222 18% 16%)', borderRadius: '12px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="interactions" stroke="hsl(38 92% 56%)" strokeWidth={2} fill="url(#gInteract)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard hover={false} delay={0.35}>
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">LLM Provider Usage</h3>
            <p className="text-sm text-muted-foreground">Cost distribution by model</p>
          </div>
          <div className="space-y-3 p-6 pt-2">
            {llmDistribution.map((m, i) => (
              <motion.div
                key={m.name}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.06 }}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-2 text-white/80">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ background: m.color }} />
                    {m.name}
                  </span>
                  <span className="font-semibold text-white">{m.value}%</span>
                </div>
                <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-white/5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${m.value}%` }}
                    transition={{ duration: 1, delay: 0.5 + i * 0.06, ease: 'easeOut' }}
                    className="h-full rounded-full"
                    style={{ background: m.color }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </GlassCard>
      </div>
    </AppShell>
  );
}
