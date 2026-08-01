'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  Zap,
  Check,
  Circle,
  Clock,
  Loader2,
  Wrench,
  Target,
  TrendingUp,
  Play,
  Pause,
  Plus,
  Activity,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { agents } from '@/lib/data';
import type { Agent, AgentStatus } from '@/lib/types';

const statusConfig: Record<AgentStatus, { color: string; dot: string; label: string }> = {
  Active: { color: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300', dot: 'bg-emerald-400', label: 'Active' },
  Executing: { color: 'border-sky-400/30 bg-sky-400/10 text-sky-300', dot: 'bg-sky-400', label: 'Executing' },
  Planning: { color: 'border-amber-400/30 bg-amber-400/10 text-amber-300', dot: 'bg-amber-400', label: 'Planning' },
  Idle: { color: 'border-white/15 bg-white/5 text-muted-foreground', dot: 'bg-white/30', label: 'Idle' },
  Paused: { color: 'border-white/15 bg-white/5 text-muted-foreground', dot: 'bg-white/20', label: 'Paused' },
};

const stepIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  done: Check,
  active: Loader2,
  pending: Circle,
};

export default function AgentsPage() {
  const [selectedAgent, setSelectedAgent] = useState<Agent>(agents[0]);

  const activeCount = agents.filter((a) => a.status === 'Active' || a.status === 'Executing').length;
  const totalTasks = agents.reduce((sum, a) => sum + a.tasksCompleted, 0);
  const avgSuccess = (agents.reduce((sum, a) => sum + a.successRate, 0) / agents.length).toFixed(1);

  return (
    <AppShell>
      {/* Stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Agents', value: String(agents.length), icon: Bot, color: 'text-sky-400' },
          { label: 'Active Now', value: String(activeCount), icon: Activity, color: 'text-emerald-400' },
          { label: 'Tasks Completed', value: totalTasks.toLocaleString(), icon: Check, color: 'text-cyan-400' },
          { label: 'Avg Success Rate', value: `${avgSuccess}%`, icon: TrendingUp, color: 'text-amber-400' },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.06} className="p-5">
            <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]', stat.color)}>
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
            <Button size="sm" className="gap-2 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">
              <Plus className="h-3.5 w-3.5" />
              Deploy
            </Button>
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
                  onClick={() => setSelectedAgent(agent)}
                  className={cn(
                    'group relative w-full overflow-hidden rounded-2xl border p-4 text-left transition-all',
                    isSelected
                      ? 'border-sky-400/30 bg-gradient-to-b from-sky-500/10 to-cyan-500/[0.02]'
                      : 'border-white/[0.08] bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.04]'
                  )}
                >
                  {isSelected && (
                    <motion.div
                      layoutId="agent-active"
                      className="absolute left-0 top-1/2 h-12 w-[3px] -translate-y-1/2 rounded-full bg-gradient-to-b from-sky-400 to-cyan-400"
                    />
                  )}
                  <div className="flex items-center gap-3">
                    <div className="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-sky-500 text-sm font-bold text-white">
                      {agent.avatar}
                      <span className={cn('absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full ring-2 ring-black/50', status.dot)}>
                        {(agent.status === 'Active' || agent.status === 'Executing') && (
                          <span className={cn('absolute inset-0 animate-ping rounded-full opacity-60', status.dot)} />
                        )}
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="truncate font-semibold text-white">{agent.name}</h4>
                        <span className={cn('shrink-0 rounded-full border px-1.5 py-0.5 text-[9px] font-semibold', status.color)}>
                          {status.label}
                        </span>
                      </div>
                      <p className="truncate text-xs text-muted-foreground">{agent.currentTask ?? agent.description}</p>
                    </div>
                  </div>
                  <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><Target className="h-3 w-3" /> {agent.tasksCompleted.toLocaleString()} tasks</span>
                    <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> {agent.successRate}%</span>
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
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -16 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Agent header */}
              <GlassCard hover={false} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-sky-500 text-xl font-bold text-white">
                      {selectedAgent.avatar}
                      <div className="absolute inset-0 rounded-2xl bg-cyan-400/20 blur-xl" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">{selectedAgent.name}</h2>
                      <p className="mt-0.5 text-sm text-muted-foreground">{selectedAgent.description}</p>
                      <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {selectedAgent.lastActive}</span>
                        <span className={cn('flex items-center gap-1 rounded-full border px-2 py-0.5 font-semibold', statusConfig[selectedAgent.status].color)}>
                          {selectedAgent.status}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="gap-2 border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]">
                      {selectedAgent.status === 'Paused' ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                      {selectedAgent.status === 'Paused' ? 'Resume' : 'Pause'}
                    </Button>
                  </div>
                </div>

                {/* Metrics */}
                <div className="mt-6 grid grid-cols-3 gap-4">
                  {[
                    { label: 'Tasks Completed', value: selectedAgent.tasksCompleted.toLocaleString() },
                    { label: 'Success Rate', value: `${selectedAgent.successRate}%` },
                    { label: 'Tools Available', value: String(selectedAgent.tools.length) },
                  ].map((m) => (
                    <div key={m.label} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                      <p className="text-xl font-bold text-white">{m.value}</p>
                      <p className="text-xs text-muted-foreground">{m.label}</p>
                    </div>
                  ))}
                </div>

                {/* Tools */}
                <div className="mt-6">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Available Tools</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedAgent.tools.map((tool) => (
                      <span key={tool} className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-white/80">
                        <Wrench className="h-3 w-3 text-sky-400" />
                        {tool}
                      </span>
                    ))}
                  </div>
                </div>
              </GlassCard>

              {/* Current task + execution timeline */}
              {selectedAgent.currentTask && (
                <GlassCard hover={false} className="p-6">
                  <div className="mb-1 flex items-center gap-2">
                    <Zap className="h-4 w-4 text-sky-400" />
                    <h3 className="font-semibold text-white">Current Task</h3>
                  </div>
                  <p className="text-sm text-white/80">{selectedAgent.currentTask}</p>

                  {selectedAgent.steps && (
                    <div className="mt-6">
                      <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Execution Plan</p>
                      <div className="relative">
                        <div className="absolute left-[15px] top-2 bottom-2 w-px bg-gradient-to-b from-sky-400/40 via-white/10 to-transparent" />
                        <div className="space-y-4">
                          {selectedAgent.steps.map((step, i) => {
                            const Icon = stepIcons[step.status] ?? Circle;
                            return (
                              <motion.div
                                key={step.id}
                                initial={{ opacity: 0, x: -12 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.08 }}
                                className="relative flex items-start gap-4"
                              >
                                <div className={cn(
                                  'relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2',
                                  step.status === 'done' && 'border-emerald-400/40 bg-emerald-400/10',
                                  step.status === 'active' && 'border-sky-400/40 bg-sky-400/10',
                                  step.status === 'pending' && 'border-white/10 bg-white/[0.02]'
                                )}>
                                  <Icon
                                    className={cn(
                                      'h-4 w-4',
                                      step.status === 'done' && 'text-emerald-400',
                                      step.status === 'active' && 'text-sky-400 animate-spin',
                                      step.status === 'pending' && 'text-muted-foreground'
                                    )}
                                  />
                                </div>
                                <div className="flex-1 pt-1">
                                  <div className="flex items-center gap-2">
                                    <h4 className={cn(
                                      'text-sm font-medium',
                                      step.status === 'pending' ? 'text-muted-foreground' : 'text-white'
                                    )}>
                                      {step.label}
                                    </h4>
                                    {step.tool && (
                                      <span className="rounded bg-white/5 px-1.5 py-0.5 text-[10px] font-mono text-sky-300">
                                        {step.tool}
                                      </span>
                                    )}
                                  </div>
                                  {step.detail && (
                                    <p className="mt-0.5 text-xs text-muted-foreground">{step.detail}</p>
                                  )}
                                </div>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  )}
                </GlassCard>
              )}

              {/* Performance chart */}
              <GlassCard hover={false} className="p-6">
                <h3 className="mb-4 font-semibold text-white">Performance Metrics</h3>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                  {[
                    { label: 'Avg Duration', value: '2.4s', color: 'text-sky-400' },
                    { label: 'Token Usage', value: '1.2K', color: 'text-cyan-400' },
                    { label: 'Tool Calls', value: '847', color: 'text-emerald-400' },
                    { label: 'Errors', value: '3', color: 'text-amber-400' },
                  ].map((m) => (
                    <div key={m.label} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                      <p className={cn('text-xl font-bold', m.color)}>{m.value}</p>
                      <p className="text-xs text-muted-foreground">{m.label}</p>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </AppShell>
  );
}
