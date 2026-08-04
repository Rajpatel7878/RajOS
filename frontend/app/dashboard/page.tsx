'use client';

import { useEffect, useState } from 'react';
import { getDashboardStats, getDashboardActivity } from '@/services/api/dashboard';
import { motion } from 'framer-motion';
import {
  Activity,
  Bot,
  BrainCircuit,
  Database,
  Cpu,
  TrendingUp,
  Zap,
  Search,
  FileText,
  Workflow,
  ArrowUpRight,
  CircleDot,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { StatCard } from '@/components/stat-card';
import {
  activityTimeline,
  usageChart,
  llmDistribution,
} from '@/lib/data';
import { cn } from '@/lib/utils';

const activityIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  agent: Bot,
  memory: BrainCircuit,
  knowledge: Database,
  chat: Activity,
  automation: Workflow,
  system: Cpu,
};

const statusColors: Record<string, string> = {
  success: 'text-emerald-400 bg-emerald-500/10',
  running: 'text-sky-400 bg-sky-500/10',
  info: 'text-cyan-400 bg-cyan-500/10',
  warning: 'text-amber-400 bg-amber-500/10',
};

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [activity, setActivity] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([getDashboardStats(), getDashboardActivity()])
      .then(([s, a]) => {
        console.log("REAL DASHBOARD STATS:", s);
        console.log("REAL DASHBOARD ACTIVITY:", a);
        setStats(s);
        setActivity(a);
      })
      .catch(console.error);
  }, []);
  ;

  return (
    <AppShell>
      {/* Welcome banner */}
      <GlassCard hover={false} className="mb-6 overflow-hidden p-0">
        <div className="relative flex flex-col gap-6 p-6 sm:flex-row sm:items-center sm:justify-between lg:p-8">
          <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-sky-500/10 blur-3xl" />
          <div className="relative">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1 text-xs font-medium text-emerald-400">
              <span className="relative flex h-2 w-2">
                <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-60" />
                <span className="relative h-2 w-2 rounded-full bg-emerald-400" />
              </span>
              All systems operational
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">
              Welcome back, Raj
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Your AI workforce executed 312 tasks today — up 24% from yesterday.
            </p>
          </div>
          <div className="relative flex gap-3">
            <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] px-5 py-3">
              <div className="text-xs text-muted-foreground">Today&apos;s Tasks</div>
              <div className="mt-0.5 text-2xl font-bold text-white">312</div>
            </div>
            <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] px-5 py-3">
              <div className="text-xs text-muted-foreground">Avg Response</div>
              <div className="mt-0.5 text-2xl font-bold text-white">1.2s</div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {stats && [
          { id: "tasks", label: "Total Tasks", value: String(stats.tasks), change: "", trend: "up", icon: "CheckSquare", sparkline: [] },
          { id: "completed_tasks", label: "Completed Tasks", value: String(stats.completed_tasks), change: "", trend: "up", icon: "CheckCircle", sparkline: [] },
          { id: "notes", label: "Notes", value: String(stats.notes), change: "", trend: "up", icon: "FileText", sparkline: [] },
          { id: "memories", label: "Memories", value: String(stats.memories), change: "", trend: "up", icon: "BrainCircuit", sparkline: [] },
        ].map((stat, i) => (
          <StatCard key={stat.id} stat={stat} delay={i * 0.06} />
        ))}
      </div>

      {/* Charts row */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        {/* Usage chart */}
        <GlassCard hover={false} delay={0.1} className="lg:col-span-2">
          <div className="flex items-center justify-between p-6 pb-2">
            <div>
              <h3 className="font-semibold text-white">AI Usage This Week</h3>
              <p className="text-sm text-muted-foreground">Chat, agents, and memory interactions</p>
            </div>
            <div className="flex gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-sky-400" /> Chat
              </span>
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-cyan-400" /> Agents
              </span>
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-violet-400" /> Memory
              </span>
            </div>
          </div>
          <div className="h-[280px] w-full p-4 pl-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={usageChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="gChat" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(199 89% 56%)" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="hsl(199 89% 56%)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gAgents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(189 94% 50%)" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="hsl(189 94% 50%)" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gMemory" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(280 83% 62%)" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="hsl(280 83% 62%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 18% 16%)" vertical={false} />
                <XAxis dataKey="day" stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(215 16% 50%)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: 'hsl(222 24% 6%)',
                    border: '1px solid hsl(222 18% 16%)',
                    borderRadius: '12px',
                    fontSize: '12px',
                  }}
                  labelStyle={{ color: 'white' }}
                />
                <Area type="monotone" dataKey="chat" stroke="hsl(199 89% 56%)" strokeWidth={2} fill="url(#gChat)" />
                <Area type="monotone" dataKey="agents" stroke="hsl(189 94% 50%)" strokeWidth={2} fill="url(#gAgents)" />
                <Area type="monotone" dataKey="memory" stroke="hsl(280 83% 62%)" strokeWidth={2} fill="url(#gMemory)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* LLM distribution */}
        <GlassCard hover={false} delay={0.15}>
          <div className="p-6 pb-2">
            <h3 className="font-semibold text-white">LLM Distribution</h3>
            <p className="text-sm text-muted-foreground">Model usage breakdown</p>
          </div>
          <div className="flex flex-col items-center p-4">
            <div className="relative h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={llmDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                  >
                    {llmDistribution.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: 'hsl(222 24% 6%)',
                      border: '1px solid hsl(222 18% 16%)',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-bold text-white">94.5K</span>
                <span className="text-xs text-muted-foreground">Total calls</span>
              </div>
            </div>
            <div className="mt-4 w-full space-y-2">
              {llmDistribution.map((m) => (
                <div key={m.name} className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-2 text-muted-foreground">
                    <span className="h-2 w-2 rounded-full" style={{ background: m.color }} />
                    {m.name}
                  </span>
                  <span className="font-medium text-white">{m.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Activity timeline + quick actions */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <GlassCard hover={false} delay={0.2} className="lg:col-span-2">
          <div className="flex items-center justify-between p-6 pb-3">
            <h3 className="font-semibold text-white">Activity Timeline</h3>
            <button className="text-xs text-sky-400 hover:text-sky-300">View all</button>
          </div>
          <div className="relative px-6 pb-6">
            <div className="absolute left-[34px] top-2 bottom-2 w-px bg-gradient-to-b from-white/10 via-white/5 to-transparent" />
            <div className="space-y-1">
            {activityTimeline.map((item, i) => {
              const Icon = activityIcons[item.type] ?? Activity;
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.3 + i * 0.06 }}
                  className="group relative flex gap-4 rounded-xl p-3 transition-colors hover:bg-white/[0.03]"
                >
                  <div className={cn(
                    'relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-white/10',
                    statusColors[item.status]
                  )}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-sm font-medium text-white">{item.title}</h4>
                      <span className="shrink-0 text-xs text-muted-foreground">{item.timestamp}</span>
                    </div>
                    <p className="mt-0.5 text-xs text-muted-foreground">{item.description}</p>
                  </div>
                </motion.div>
              );
            })}
            </div>
          </div>
        </GlassCard>

        {/* Quick actions */}
        <div className="space-y-6">
          <GlassCard hover={false} delay={0.25}>
            <div className="p-6 pb-3">
              <h3 className="font-semibold text-white">Quick Actions</h3>
            </div>
            <div className="grid grid-cols-2 gap-3 p-6 pt-2">
              {[
                { icon: Activity, label: 'New Chat', href: '/chat', color: 'text-sky-400' },
                { icon: Bot, label: 'Deploy Agent', href: '/agents', color: 'text-cyan-400' },
                { icon: FileText, label: 'Upload Doc', href: '/knowledge', color: 'text-emerald-400' },
                { icon: Workflow, label: 'New Workflow', href: '/agents', color: 'text-amber-400' },
              ].map((action) => (
                <motion.a
                  key={action.label}
                  href={action.href}
                  whileHover={{ y: -3 }}
                  className="group flex flex-col gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 transition-all hover:border-sky-400/20 hover:bg-white/[0.04]"
                >
                  <action.icon className={`h-5 w-5 ${action.color}`} />
                  <span className="text-sm font-medium text-white">{action.label}</span>
                </motion.a>
              ))}
            </div>
          </GlassCard>

          <GlassCard hover={false} delay={0.3}>
            <div className="p-6 pb-3">
              <h3 className="font-semibold text-white">System Health</h3>
            </div>
            <div className="space-y-4 p-6 pt-2">
              {[
                { label: 'API Latency', value: '1.2s', pct: 92, color: 'from-sky-400 to-cyan-400' },
                { label: 'Memory Usage', value: '68%', pct: 68, color: 'from-emerald-400 to-teal-400' },
                { label: 'Vector Index', value: 'Ready', pct: 100, color: 'from-violet-400 to-purple-400' },
                { label: 'Agent Pool', value: '5/6 active', pct: 83, color: 'from-amber-400 to-orange-400' },
              ].map((m) => (
                <div key={m.label}>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{m.label}</span>
                    <span className="font-medium text-white">{m.value}</span>
                  </div>
                  <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${m.pct}%` }}
                      transition={{ duration: 1, delay: 0.4, ease: 'easeOut' }}
                      className={`h-full rounded-full bg-gradient-to-r ${m.color}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </AppShell>
  );
}
