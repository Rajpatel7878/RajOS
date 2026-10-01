"use client";

import { useEffect, useState } from "react";
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
} from "recharts";
import {
  Activity,
  BrainCircuit,
  Database,
  Zap,
  Clock,
  Target,
  Award,
  Cpu,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { AnimatedCounter } from "@/components/animated-counter";
import { cn } from "@/lib/utils";
import { getWorkload, getTrends, getWeeklySummary, WorkloadAnalysis, ProductivityTrends, WeeklySummary } from "@/services/api/productivity";

export default function AnalyticsPage() {
  const [workload, setWorkload] = useState<WorkloadAnalysis | null>(null);
  const [trends, setTrends] = useState<ProductivityTrends | null>(null);
  const [weekly, setWeekly] = useState<WeeklySummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getWorkload(), getTrends(), getWeeklySummary()])
      .then(([w, t, wk]) => {
        setWorkload(w);
        setTrends(t);
        setWeekly(wk);
      })
      .catch((err) => console.error("Error loading analytics data:", err))
      .finally(() => setLoading(false));
  }, []);

  const summaryStats = [
    { label: "Pending Workload", value: workload?.total_pending ?? 0, suffix: " tasks", icon: Activity, color: "text-sky-400", gradient: "sky" },
    { label: "Completed Tasks", value: workload?.total_completed ?? 0, suffix: " tasks", icon: CheckCircle2, color: "text-emerald-400", gradient: "emerald" },
    { label: "Completion Rate", value: weekly?.completion_rate ?? 0, suffix: "%", icon: Target, color: "text-cyan-400", gradient: "cyan" },
    { label: "Est. Workload", value: workload?.total_estimated_workload_minutes ?? 0, suffix: " mins", icon: Clock, color: "text-amber-400", gradient: "amber" },
  ];

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
              Productivity Intelligence & System Telemetry
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Workload <span className="text-gradient-cyan">Analytics & Trends</span>
            </h1>
            <p className="mt-2 text-sm text-muted-foreground max-w-xl leading-relaxed">
              Real-time task velocity, priority distribution, and weekly completion metrics calculated strictly from your authenticated workspace.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 backdrop-blur-xl">
              <div className="text-xs text-muted-foreground">Productivity Engine</div>
              <div className="mt-1 flex items-center gap-2 text-base font-bold text-emerald-400">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative h-2.5 w-2.5 rounded-full bg-emerald-400" />
                </span>
                Active & Synced
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Summary Stat Cards ── */}
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
          </GlassCard>
        ))}
      </div>

      {/* ── Main Charts Grid ── */}
      <div className="grid gap-6 lg:grid-cols-2 mb-8">
        {/* Task Velocity Trend Chart */}
        <GlassCard hover={false} delay={0.2} className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-white">Task Completion Trend</h3>
              <p className="text-xs text-muted-foreground">Daily task creation vs completion activity</p>
            </div>
            <div className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] text-sky-400">
              <Activity className="h-3 w-3" /> Real Data
            </div>
          </div>

          {trends && !trends.has_sufficient_data ? (
            <div className="flex h-[280px] w-full flex-col items-center justify-center rounded-xl border border-dashed border-white/10 p-6 text-center">
              <AlertCircle className="mb-2 h-8 w-8 text-amber-400" />
              <h4 className="font-semibold text-white">Insufficient Trend Data</h4>
              <p className="mt-1 text-xs text-muted-foreground max-w-sm">
                {trends.message}
              </p>
            </div>
          ) : (
            <div className="h-[280px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends?.daily_data || []} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="anCreated" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="anCompleted" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#34d399" stopOpacity={0.4} />
                      <stop offset="100%" stopColor="#34d399" stopOpacity={0} />
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
                  <Area type="monotone" dataKey="tasks_created" stroke="#38bdf8" strokeWidth={2} fill="url(#anCreated)" name="Created" />
                  <Area type="monotone" dataKey="tasks_completed" stroke="#34d399" strokeWidth={2} fill="url(#anCompleted)" name="Completed" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </GlassCard>

        {/* Priority & Category Distribution */}
        <GlassCard hover={false} delay={0.25} className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-white">Workload Priority Breakdown</h3>
              <p className="text-xs text-muted-foreground">Pending tasks by priority classification</p>
            </div>
          </div>

          <div className="space-y-4 pt-2">
            {[
              { name: "High / Urgent", count: workload?.priority_distribution?.high ?? 0, color: "bg-rose-500" },
              { name: "Normal Priority", count: workload?.priority_distribution?.normal ?? 0, color: "bg-sky-500" },
              { name: "Low Priority", count: workload?.priority_distribution?.low ?? 0, color: "bg-emerald-500" },
            ].map((p) => {
              const total = workload?.total_pending || 1;
              const pct = Math.round((p.count / total) * 100);
              return (
                <div key={p.name} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-white flex items-center gap-2">
                      <span className={`h-2.5 w-2.5 rounded-full ${p.color}`} />
                      {p.name}
                    </span>
                    <span className="text-muted-foreground font-mono">{p.count} tasks ({pct}%)</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-white/[0.08]">
                    <div className={`h-full rounded-full ${p.color}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-8 border-t border-white/[0.08] pt-4">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Top Workload Categories</h4>
            {workload?.category_distribution && Object.keys(workload.category_distribution).length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(workload.category_distribution).map(([cat, count]) => (
                  <div key={cat} className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white">
                    <span className="font-medium">{cat}</span>
                    <span className="rounded-full bg-sky-500/20 px-2 py-0.5 text-[10px] font-bold text-sky-400">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No categories assigned to pending tasks yet.</p>
            )}
          </div>
        </GlassCard>
      </div>
    </AppShell>
  );
}
