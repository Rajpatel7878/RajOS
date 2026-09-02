"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
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
  CheckCircle2,
  Clock,
  Sparkles,
  Layers,
  ChevronRight,
  Play,
  Terminal,
} from "lucide-react";
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { StatCard } from "@/components/stat-card";
import {
  activityTimeline,
  usageChart,
  llmDistribution,
} from "@/lib/data";
import { cn } from "@/lib/utils";
import { getDashboardStats, getDashboardActivity } from "@/services/api/dashboard";

// Lazy-load 3D AI Core canvas to guarantee zero SSR issues
const AICore = dynamic(
  () => import("@/components/three/ai-core").then((m) => ({ default: m.AICore })),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-52 w-52 items-center justify-center">
        <div className="h-24 w-24 rounded-full border border-sky-400/20 bg-sky-500/10 animate-pulse" />
      </div>
    ),
  }
);

const activityIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  agent: Bot,
  memory: BrainCircuit,
  knowledge: Database,
  chat: Activity,
  automation: Workflow,
  system: Cpu,
};

const statusColors: Record<string, string> = {
  success: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  running: "text-sky-400 bg-sky-500/10 border-sky-500/20",
  info: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  warning: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

const agentCards = [
  { id: "atlas", name: "Atlas", role: "Orchestrator", color: "from-sky-400 to-blue-600", dot: "bg-sky-400" },
  { id: "nova",  name: "Nova",  role: "Research & Web", color: "from-violet-400 to-purple-600", dot: "bg-violet-400" },
  { id: "sage",  name: "Sage",  role: "Planning & Tasks", color: "from-emerald-400 to-teal-600", dot: "bg-emerald-400" },
  { id: "echo",  name: "Echo",  role: "Memory & Recall", color: "from-amber-400 to-orange-600", dot: "bg-amber-400" },
  { id: "pulse", name: "Pulse", role: "Analytics & Telemetry", color: "from-rose-400 to-pink-600", dot: "bg-rose-400" },
];

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [activity, setActivity] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([getDashboardStats(), getDashboardActivity()])
      .then(([s, a]) => {
        setStats(s);
        setActivity(a);
      })
      .catch((err) => console.error("Error loading dashboard data:", err));
  }, []);

  return (
    <AppShell>
      {/* ── 3D Hero Command Center Section ── */}
      <div className="relative mb-8 overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-br from-black/80 via-black/50 to-sky-950/20 p-6 sm:p-8 backdrop-blur-2xl shadow-[0_20px_50px_-12px_rgba(0,0,0,0.7)]">
        {/* Glow lights behind hero */}
        <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-sky-500/15 blur-3xl" />
        <div className="pointer-events-none absolute right-10 top-1/2 h-72 w-72 -translate-y-1/2 rounded-full bg-cyan-500/10 blur-[100px]" />
        <div className="pointer-events-none absolute inset-0 scanlines opacity-50" />

        <div className="relative z-10 flex flex-col items-center justify-between gap-8 lg:flex-row">
          {/* Left: Info & Telemetry */}
          <div className="max-w-2xl">
            {/* Status Pill */}
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3.5 py-1 text-xs font-semibold text-emerald-300 backdrop-blur-md shadow-[0_0_12px_rgba(52,211,153,0.2)]">
              <span className="relative flex h-2 w-2">
                <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative h-2 w-2 rounded-full bg-emerald-400" />
              </span>
              Neural Engine Online · 5 Specialists Active
            </div>

            <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl text-white">
              RajOS <span className="text-gradient-cyan">Command Center</span>
            </h1>
            <p className="mt-2 text-sm sm:text-base text-muted-foreground leading-relaxed">
              Your autonomous AI workforce is orchestrating tasks, indexing memory, and monitoring intelligence in real-time.
            </p>

            {/* Quick Metrics Pills */}
            <div className="mt-6 flex flex-wrap gap-3">
              <div className="flex items-center gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-2.5 backdrop-blur-md">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <div>
                  <div className="text-[11px] text-muted-foreground leading-none">Tasks Done</div>
                  <div className="text-base font-bold text-white leading-tight mt-0.5">
                    {stats?.completed_tasks ?? 24}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-2.5 backdrop-blur-md">
                <BrainCircuit className="h-4 w-4 text-violet-400" />
                <div>
                  <div className="text-[11px] text-muted-foreground leading-none">Memory Nodes</div>
                  <div className="text-base font-bold text-white leading-tight mt-0.5">
                    {stats?.memories ?? 142}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-2.5 backdrop-blur-md">
                <Zap className="h-4 w-4 text-sky-400" />
                <div>
                  <div className="text-[11px] text-muted-foreground leading-none">Avg Latency</div>
                  <div className="text-base font-bold text-white leading-tight mt-0.5">0.8s</div>
                </div>
              </div>

              {/* Action button */}
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-400 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-sky-500/25 hover:from-sky-400 hover:to-cyan-300 hover:shadow-sky-500/40 transition-all duration-200"
              >
                <Terminal className="h-4 w-4" />
                Launch Session
              </Link>
            </div>
          </div>

          {/* Right: Interactive 3D AI Core Canvas */}
          <div className="relative flex shrink-0 items-center justify-center">
            {/* Holographic Ring background */}
            <div className="absolute h-60 w-60 rounded-full border border-sky-400/20 bg-sky-500/[0.02] shadow-[0_0_40px_rgba(56,189,248,0.15)] animate-[spin-slow_24s_linear_infinite]" />
            <div className="relative h-56 w-56 sm:h-64 sm:w-64 cursor-grab active:cursor-grabbing">
              <AICore className="h-full w-full" />
            </div>
          </div>
        </div>
      </div>

      {/* ── 3D Stat Cards Row ── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            id: "tasks",
            label: "Total Tasks",
            value: String(stats?.tasks ?? 38),
            change: "+12% this week",
            trend: "up",
            icon: "CheckSquare",
            gradient: "sky",
          },
          {
            id: "completed",
            label: "Tasks Completed",
            value: String(stats?.completed_tasks ?? 24),
            change: "63% completion rate",
            trend: "up",
            icon: "CheckCircle",
            gradient: "emerald",
          },
          {
            id: "notes",
            label: "Knowledge Notes",
            value: String(stats?.notes ?? 19),
            change: "+4 added today",
            trend: "up",
            icon: "FileText",
            gradient: "cyan",
          },
          {
            id: "memories",
            label: "Active Memories",
            value: String(stats?.memories ?? 142),
            change: "Auto-synced",
            trend: "up",
            icon: "BrainCircuit",
            gradient: "violet",
          },
        ].map((stat, i) => (
          <GlassCard
            key={stat.id}
            hover={true}
            gradient={stat.gradient as any}
            delay={i * 0.05}
            className="p-5"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {stat.label}
              </span>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/5">
                <Sparkles className="h-4 w-4 text-sky-400" />
              </div>
            </div>
            <div className="mt-3 text-3xl font-extrabold tracking-tight text-white">
              {stat.value}
            </div>
            <div className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
              <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-medium">{stat.change}</span>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* ── Autonomous AI Specialists Center ── */}
      <div className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-sky-400" />
            <h2 className="text-sm font-semibold uppercase tracking-wider text-white">
              Agent Workforce Telemetry
            </h2>
          </div>
          <Link href="/agents" className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1">
            Manage Agents <ChevronRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
          {agentCards.map((agent, i) => (
            <Link
              key={agent.id}
              href={`/chat?agent=${agent.id}`}
              className="group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 transition-all duration-300 hover:-translate-y-1 hover:border-sky-400/40 hover:bg-white/[0.06] hover:shadow-[0_12px_24px_-8px_rgba(56,189,248,0.2)]"
            >
              <div className="flex items-center justify-between">
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${agent.color} font-bold text-white shadow-md`}>
                  {agent.name[0]}
                </div>
                <div className="flex items-center gap-1.5 rounded-full bg-black/40 border border-white/10 px-2 py-0.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${agent.dot} animate-pulse`} />
                  <span className="text-[10px] text-muted-foreground">Live</span>
                </div>
              </div>
              <div className="mt-3">
                <h3 className="font-semibold text-white group-hover:text-sky-400 transition-colors">
                  {agent.name}
                </h3>
                <p className="text-[11px] text-muted-foreground truncate">{agent.role}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── Charts & System Telemetry Grid ── */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        {/* Usage Area Chart (2 Cols) */}
        <GlassCard hover={false} delay={0.1} className="lg:col-span-2">
          <div className="flex items-center justify-between p-6 pb-2">
            <div>
              <h3 className="font-semibold text-white">AI Interaction Load</h3>
              <p className="text-sm text-muted-foreground">Weekly volume across Chat, Agents & Memory</p>
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
                    <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gAgents" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gMemory" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#a78bfa" stopOpacity={0} />
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
                    boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
                    fontSize: "12px",
                  }}
                  labelStyle={{ color: "white", fontWeight: "bold" }}
                />
                <Area type="monotone" dataKey="chat" stroke="#38bdf8" strokeWidth={2} fill="url(#gChat)" />
                <Area type="monotone" dataKey="agents" stroke="#22d3ee" strokeWidth={2} fill="url(#gAgents)" />
                <Area type="monotone" dataKey="memory" stroke="#a78bfa" strokeWidth={2} fill="url(#gMemory)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* LLM Distribution & Quick Actions (1 Col) */}
        <div className="space-y-6">
          <GlassCard hover={false} delay={0.15}>
            <div className="p-6 pb-2">
              <h3 className="font-semibold text-white">LLM Provider Share</h3>
              <p className="text-sm text-muted-foreground">Tokens routed by intelligence tier</p>
            </div>
            <div className="flex flex-col items-center p-4">
              <div className="relative h-[180px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={llmDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={52}
                      outerRadius={78}
                      paddingAngle={4}
                      dataKey="value"
                      stroke="none"
                    >
                      {llmDistribution.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "rgba(10, 15, 26, 0.95)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                        fontSize: "12px",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-bold text-white">Gemini</span>
                  <span className="text-[10px] uppercase tracking-wider text-sky-400">Default LLM</span>
                </div>
              </div>
              <div className="mt-3 w-full space-y-2">
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
      </div>

      {/* ── Activity Timeline & Quick Actions Row ── */}
      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        {/* Timeline */}
        <GlassCard hover={false} delay={0.2} className="lg:col-span-2">
          <div className="flex items-center justify-between p-6 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-sky-400" />
              <h3 className="font-semibold text-white">Live Activity Stream</h3>
            </div>
            <span className="text-[11px] text-muted-foreground">Real-time sync</span>
          </div>
          <div className="relative px-6 pb-6">
            <div className="absolute left-[35px] top-2 bottom-2 w-px bg-gradient-to-b from-sky-400/30 via-white/10 to-transparent" />
            <div className="space-y-2">
              {activityTimeline.slice(0, 5).map((item, i) => {
                const Icon = activityIcons[item.type] ?? Activity;
                return (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.35, delay: i * 0.05 }}
                    className="group relative flex gap-4 rounded-xl border border-transparent p-3 transition-colors hover:border-white/[0.06] hover:bg-white/[0.03]"
                  >
                    <div
                      className={cn(
                        "relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border",
                        statusColors[item.status]
                      )}
                    >
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

        {/* 3D Elevated Quick Action Tiles */}
        <div className="space-y-4">
          <GlassCard hover={false} delay={0.25} className="p-6">
            <h3 className="font-semibold text-white mb-4">Quick Command Center</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: Terminal, label: "AI Terminal", href: "/chat", color: "text-sky-400", bg: "hover:border-sky-400/40" },
                { icon: CheckCircle2, label: "New Task", href: "/tasks", color: "text-emerald-400", bg: "hover:border-emerald-400/40" },
                { icon: BrainCircuit, label: "Memory Log", href: "/memory", color: "text-violet-400", bg: "hover:border-violet-400/40" },
                { icon: Bot, label: "Agent Center", href: "/agents", color: "text-cyan-400", bg: "hover:border-cyan-400/40" },
              ].map((action) => (
                <Link
                  key={action.label}
                  href={action.href}
                  className={`group flex flex-col gap-3 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-4 transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.05] ${action.bg} shadow-[0_4px_16px_rgba(0,0,0,0.4)]`}
                >
                  <action.icon className={`h-6 w-6 ${action.color} transition-transform duration-300 group-hover:scale-110`} />
                  <span className="text-xs font-semibold text-white">{action.label}</span>
                </Link>
              ))}
            </div>
          </GlassCard>

          {/* Core Telemetry Health */}
          <GlassCard hover={false} delay={0.3} className="p-6">
            <h3 className="font-semibold text-white mb-3">Engine Telemetry</h3>
            <div className="space-y-3.5">
              {[
                { label: "Gemini 3.1 Pipeline", value: "Optimal", pct: 98, color: "from-sky-400 to-cyan-400" },
                { label: "Vector Search Memory", value: "Synchronized", pct: 100, color: "from-emerald-400 to-teal-400" },
                { label: "Push Notification Gateway", value: "Ready", pct: 100, color: "from-violet-400 to-purple-400" },
              ].map((item) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">{item.label}</span>
                    <span className="font-medium text-emerald-400">{item.value}</span>
                  </div>
                  <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
                    <div
                      className={`h-full rounded-full bg-gradient-to-r ${item.color}`}
                      style={{ width: `${item.pct}%` }}
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
