"use client";

import { motion } from "framer-motion";
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
} from "recharts";
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
  Sparkles,
  Layers,
  ArrowUpRight,
  ShieldCheck,
  Radio,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { AnimatedCounter } from "@/components/animated-counter";
import { cn } from "@/lib/utils";
import {
  usageChart,
  memoryGrowthChart,
  knowledgeGrowthChart,
  productivityChart,
  interactionHistory,
  llmDistribution,
} from "@/lib/data";

const summaryStats = [
  { label: "Total Interactions", value: 94521, suffix: "", change: "+31.5%", trend: "up", icon: Activity, color: "text-sky-400", gradient: "sky" },
  { label: "Memory Items", value: 8206, suffix: "", change: "+12.4%", trend: "up", icon: BrainCircuit, color: "text-cyan-400", gradient: "cyan" },
  { label: "Knowledge Docs", value: 2318, suffix: "", change: "+8.1%", trend: "up", icon: Database, color: "text-emerald-400", gradient: "emerald" },
  { label: "Tasks Automated", value: 5885, suffix: "", change: "+24.6%", trend: "up", icon: Zap, color: "text-amber-400", gradient: "amber" },
];

const topMetrics = [
  { label: "Productivity Score", value: 94.2, suffix: "/100", icon: Award, color: "text-sky-400", pct: 94 },
  { label: "Task Accuracy", value: 97.4, suffix: "%", icon: Target, color: "text-emerald-400", pct: 97 },
  { label: "Avg Response Time", value: 1.2, suffix: "s", icon: Clock, color: "text-cyan-400", pct: 88 },
  { label: "LLM Efficiency", value: 89.6, suffix: "%", icon: Cpu, color: "text-violet-400", pct: 90 },
];

export default function AnalyticsPage() {
  return (
    <AppShell>
      {/* ── 3D Hero Analytics Banner ── */}
      <div className="relative mb-8 overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-br from-black/80 via-black/50 to-sky-950/25 p-6 sm:p-8 backdrop-blur-2xl shadow-[0_20px_50px_-12px_rgba(0,0,0,0.8)]">
        <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-sky-500/15 blur-3xl" />
        <div className="pointer-events-none absolute -right-20 -bottom-20 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="pointer-events-none absolute inset-0 scanlines opacity-30" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-400/10 px-3.5 py-1 text-xs font-semibold text-sky-300">
              <Sparkles className="h-3.5 w-3.5" />
              Spatial Intelligence & System Telemetry
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              System <span className="text-gradient-cyan">Analytics & Intelligence</span>
            </h1>
            <p className="mt-2 text-sm text-muted-foreground max-w-xl leading-relaxed">
              Real-time computational throughput, memory index velocity, and multi-agent execution analytics across the entire RajOS cluster.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 backdrop-blur-xl">
              <div className="text-xs text-muted-foreground">Cluster Health</div>
              <div className="mt-1 flex items-center gap-2 text-base font-bold text-emerald-400">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative h-2.5 w-2.5 rounded-full bg-emerald-400" />
                </span>
                99.98% Optimal
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── 3D Interactive Summary Stat Cards ── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {summaryStats.map((stat, i) => (
          <GlassCard
            key={stat.label}
            hover={true}
            gradient={stat.gradient as any}
            delay={i * 0.05}
            className="p-5"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {stat.label}
              </span>
              <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/5">
                <stat.icon className={cn("h-4.5 w-4.5", stat.color)} />
              </div>
            </div>
            <div className="mt-3 text-3xl font-extrabold tracking-tight text-white">
              <AnimatedCounter value={stat.value} suffix={stat.suffix} />
            </div>
            <div className="mt-1.5 flex items-center gap-1.5 text-xs text-muted-foreground">
              <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">{stat.change}</span>
              <span>vs last cycle</span>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* ── Top Efficiency Metrics Bar ── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {topMetrics.map((m, i) => (
          <GlassCard key={m.label} hover={true} delay={0.15 + i * 0.05} className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground">{m.label}</span>
              <m.icon className={cn("h-4 w-4", m.color)} />
            </div>
            <div className="mt-2 text-2xl font-bold text-white">
              {m.value}
              <span className="text-sm font-normal text-muted-foreground ml-1">{m.suffix}</span>
            </div>
            <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.08]">
              <div
                className="h-full rounded-full bg-gradient-to-r from-sky-400 to-cyan-400"
                style={{ width: `${m.pct}%` }}
              />
            </div>
          </GlassCard>
        ))}
      </div>

      {/* ── Main Charts Grid ── */}
      <div className="grid gap-6 lg:grid-cols-2 mb-8">
        {/* Interaction Velocity Chart */}
        <GlassCard hover={false} delay={0.2} className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-white">Computational Velocity</h3>
              <p className="text-xs text-muted-foreground">Daily request volume across agents and memory</p>
            </div>
            <div className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] text-sky-400">
              <Activity className="h-3 w-3" /> Live
            </div>
          </div>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={usageChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="anChat" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="anAgents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(10, 15, 26, 0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "12px",
                    fontSize: "12px",
                  }}
                />
                <Area type="monotone" dataKey="chat" stroke="#38bdf8" strokeWidth={2} fill="url(#anChat)" />
                <Area type="monotone" dataKey="agents" stroke="#22d3ee" strokeWidth={2} fill="url(#anAgents)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Memory & Knowledge Growth */}
        <GlassCard hover={false} delay={0.25} className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-white">Memory Index Expansion</h3>
              <p className="text-xs text-muted-foreground">Cumulative long-term vector storage</p>
            </div>
            <span className="text-xs text-emerald-400 font-semibold">+18% Monthly</span>
          </div>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={memoryGrowthChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="anMem" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(10, 15, 26, 0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "12px",
                    fontSize: "12px",
                  }}
                />
                <Area type="monotone" dataKey="items" stroke="#a78bfa" strokeWidth={2} fill="url(#anMem)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* ── Productivity & Model Allocation ── */}
      <div className="grid gap-6 lg:grid-cols-3">
        <GlassCard hover={false} delay={0.3} className="lg:col-span-2 p-6">
          <h3 className="font-bold text-white mb-1">Productivity Score Index</h3>
          <p className="text-xs text-muted-foreground mb-4">Automated execution efficiency across weeks</p>
          <div className="h-[240px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={productivityChart} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
                <XAxis dataKey="week" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} domain={[80, 100]} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(10, 15, 26, 0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "12px",
                    fontSize: "12px",
                  }}
                />
                <Line type="monotone" dataKey="score" stroke="#34d399" strokeWidth={3} dot={{ fill: "#34d399", r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard hover={false} delay={0.35} className="p-6">
          <h3 className="font-bold text-white mb-1">Multi-LLM Dispatch</h3>
          <p className="text-xs text-muted-foreground mb-4">Routed token allocation</p>
          <div className="space-y-4 pt-2">
            {llmDistribution.map((item) => (
              <div key={item.name} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-white flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ background: item.color }} />
                    {item.name}
                  </span>
                  <span className="text-muted-foreground font-mono">{item.value}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.08]">
                  <div className="h-full rounded-full" style={{ width: `${item.value}%`, background: item.color }} />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </AppShell>
  );
}
