"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bot,
  Zap,
  Check,
  Circle,
  Loader2,
  Wrench,
  Target,
  TrendingUp,
  Play,
  Plus,
  Activity,
  RefreshCw,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { agents as localAgents } from "@/lib/data";
import type { Agent, AgentStatus } from "@/lib/types";
import { getAgents, runAgent, type AgentInfo } from "@/services/api/agents";

const statusConfig: Record<AgentStatus, { color: string; dot: string; label: string }> = {
  Active: { color: "border-emerald-400/30 bg-emerald-400/10 text-emerald-300", dot: "bg-emerald-400", label: "Active" },
  Executing: { color: "border-sky-400/30 bg-sky-400/10 text-sky-300", dot: "bg-sky-400", label: "Executing" },
  Planning: { color: "border-amber-400/30 bg-amber-400/10 text-amber-300", dot: "bg-amber-400", label: "Planning" },
  Idle: { color: "border-white/15 bg-white/5 text-muted-foreground", dot: "bg-white/30", label: "Idle" },
  Paused: { color: "border-white/15 bg-white/5 text-muted-foreground", dot: "bg-white/20", label: "Paused" },
};

const stepIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  done: Check,
  active: Loader2,
  pending: Circle,
};

// Merge backend agent info (status/tasksCompleted) with local data (steps/details)
function mergeAgents(localData: Agent[], backendData: AgentInfo[]): Agent[] {
  return localData.map((local) => {
    const backend = backendData.find((b) => b.id === local.id);
    if (!backend) return local;
    return {
      ...local,
      status: backend.status,
      description: backend.description,
      tools: backend.tools,
    };
  });
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>(localAgents);
  const [selectedAgent, setSelectedAgent] = useState<Agent>(localAgents[0]);
  const [loading, setLoading] = useState(false);
  const [runningAgent, setRunningAgent] = useState<string | null>(null);
  const [runPrompt, setRunPrompt] = useState("");
  const [runResult, setRunResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadBackendAgents = async () => {
    try {
      setLoading(true);
      const backendData = await getAgents();
      const merged = mergeAgents(localAgents, backendData);
      setAgents(merged);
      setSelectedAgent(merged.find((a) => a.id === selectedAgent.id) ?? merged[0]);
    } catch {
      // Backend not running — keep local data, no error shown
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBackendAgents();
  }, []);

  const handleRunAgent = async () => {
    if (!runPrompt.trim() || runningAgent) return;
    setRunningAgent(selectedAgent.id);
    setRunResult(null);
    setError(null);
    try {
      const result = await runAgent(selectedAgent.id, { prompt: runPrompt });
      setRunResult(result.response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent run failed");
    } finally {
      setRunningAgent(null);
    }
  };

  const activeCount = agents.filter(
    (a) => a.status === "Active" || a.status === "Executing"
  ).length;
  const totalTasks = agents.reduce((sum, a) => sum + a.tasksCompleted, 0);
  const avgSuccess = (
    agents.reduce((sum, a) => sum + a.successRate, 0) / agents.length
  ).toFixed(1);

  return (
    <AppShell>
      {/* Stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Agents", value: String(agents.length), icon: Bot, color: "text-sky-400" },
          { label: "Active Now", value: String(activeCount), icon: Activity, color: "text-emerald-400" },
          { label: "Tasks Completed", value: totalTasks.toLocaleString(), icon: Check, color: "text-cyan-400" },
          { label: "Avg Success Rate", value: `${avgSuccess}%`, icon: TrendingUp, color: "text-amber-400" },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.06} className="p-5">
            <div className={cn("flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]", stat.color)}>
              <stat.icon className="h-5 w-5" />
            </div>
            <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-sm text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Agent list */}
        <div className="space-y-6 lg:col-span-1">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-white">Your Agents</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={loadBackendAgents}
                className="rounded-lg p-1.5 text-muted-foreground hover:text-white transition-colors"
                title="Refresh from backend"
              >
                <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
              </button>
              <Button
                size="sm"
                className="gap-2 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
              >
                <Plus className="h-3.5 w-3.5" />
                Deploy
              </Button>
            </div>
          </div>

          <div className="space-y-3">
            {agents.map((agent, i) => {
              const status = statusConfig[agent.status];
              const isSelected = selectedAgent.id === agent.id;
              return (
                <motion.button
                  key={agent.id}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  onClick={() => {
                    setSelectedAgent(agent);
                    setRunResult(null);
                    setError(null);
                  }}
                  className={cn(
                    "group relative w-full overflow-hidden rounded-2xl border p-4 text-left transition-all",
                    isSelected
                      ? "border-sky-400/30 bg-gradient-to-b from-sky-500/10 to-cyan-500/[0.02]"
                      : "border-white/[0.08] bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.04]"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-sky-500 text-sm font-bold text-white">
                      {agent.avatar}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{agent.name}</span>
                        <span className={cn("flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-medium", status.color)}>
                          <span className={cn("h-1.5 w-1.5 rounded-full", status.dot)} />
                          {status.label}
                        </span>
                      </div>
                      <p className="mt-1 text-xs leading-relaxed text-muted-foreground line-clamp-2">
                        {agent.description}
                      </p>
                    </div>
                  </div>
                </motion.button>
              );
            })}
          </div>
        </div>

        {/* Agent detail */}
        <div className="lg:col-span-2">
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedAgent.id}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <GlassCard className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-sky-500 text-xl font-bold text-white">
                    {selectedAgent.avatar}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h2 className="text-xl font-bold text-white">{selectedAgent.name}</h2>
                      <Badge
                        className={cn(
                          "border px-2 py-0.5 text-xs font-medium",
                          statusConfig[selectedAgent.status].color
                        )}
                      >
                        {selectedAgent.status}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{selectedAgent.description}</p>
                    <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1.5">
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                        {selectedAgent.tasksCompleted.toLocaleString()} tasks
                      </span>
                      <span className="flex items-center gap-1.5">
                        <TrendingUp className="h-3.5 w-3.5 text-amber-400" />
                        {selectedAgent.successRate}% success
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Zap className="h-3.5 w-3.5 text-sky-400" />
                        {selectedAgent.lastActive}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Tools */}
                <div className="mt-5">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Tools
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {selectedAgent.tools.map((tool) => (
                      <span
                        key={tool}
                        className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.02] px-2.5 py-1.5 text-xs text-muted-foreground"
                      >
                        <Wrench className="h-3 w-3 text-sky-400/60" />
                        {tool}
                      </span>
                    ))}
                  </div>
                </div>
              </GlassCard>

              {/* Run Agent */}
              <GlassCard className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Play className="h-4 w-4 text-emerald-400" />
                  <h3 className="font-semibold text-white">Run {selectedAgent.name}</h3>
                </div>
                <div className="space-y-3">
                  <textarea
                    value={runPrompt}
                    onChange={(e) => setRunPrompt(e.target.value)}
                    placeholder={`Give ${selectedAgent.name} a task...`}
                    rows={3}
                    className="w-full rounded-xl border border-white/[0.08] bg-white/[0.02] px-3 py-2 text-sm text-white placeholder:text-muted-foreground/60 focus:outline-none focus:border-sky-400/50 resize-none"
                  />
                  <Button
                    onClick={handleRunAgent}
                    disabled={!runPrompt.trim() || !!runningAgent}
                    className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
                  >
                    {runningAgent === selectedAgent.id ? (
                      <><Loader2 className="h-4 w-4 animate-spin" /> Running...</>
                    ) : (
                      <><Play className="h-4 w-4" /> Run Agent</>
                    )}
                  </Button>

                  {error && (
                    <div className="rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
                      {error}
                    </div>
                  )}

                  {runResult && (
                    <motion.div
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="rounded-xl border border-emerald-400/20 bg-emerald-400/[0.05] p-4"
                    >
                      <p className="text-xs font-semibold text-emerald-400 mb-2">
                        {selectedAgent.name} Response
                      </p>
                      <p className="text-sm text-white/90 leading-relaxed whitespace-pre-wrap">
                        {runResult}
                      </p>
                    </motion.div>
                  )}
                </div>
              </GlassCard>

              {/* Steps */}
              {selectedAgent.steps && selectedAgent.steps.length > 0 && (
                <GlassCard className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Target className="h-4 w-4 text-sky-400" />
                    <h3 className="font-semibold text-white">Execution Steps</h3>
                  </div>
                  <div className="space-y-3">
                    {selectedAgent.steps.map((step, i) => {
                      const StepIcon = stepIcons[step.status] ?? Circle;
                      return (
                        <motion.div
                          key={step.id}
                          initial={{ opacity: 0, x: 8 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.05 }}
                          className="flex items-start gap-3"
                        >
                          <div className={cn(
                            "mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full",
                            step.status === "done" ? "bg-emerald-500/20 text-emerald-400" :
                            step.status === "active" ? "bg-sky-500/20 text-sky-400" :
                            "bg-white/5 text-muted-foreground"
                          )}>
                            <StepIcon className={cn("h-3 w-3", step.status === "active" && "animate-spin")} />
                          </div>
                          <div className="flex-1">
                            <p className={cn(
                              "text-sm",
                              step.status === "done" ? "text-white" :
                              step.status === "active" ? "font-medium text-sky-300" :
                              "text-muted-foreground"
                            )}>
                              {step.label}
                            </p>
                            {step.tool && (
                              <p className="mt-0.5 text-xs text-muted-foreground/60">{step.tool}</p>
                            )}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </GlassCard>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </AppShell>
  );
}
