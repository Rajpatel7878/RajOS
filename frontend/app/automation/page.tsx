'use client';

import { motion } from 'framer-motion';
import {
  Workflow,
  Plus,
  Zap,
  Clock,
  CheckCircle2,
  Pause,
  ArrowRight,
  Bot,
  BrainCircuit,
  Mail,
  Database,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';

const automations = [
  {
    id: 1,
    name: 'Daily digest email',
    description: 'Summarize yesterday\'s AI activity and send to raj@rajos.ai every morning at 8 AM.',
    trigger: 'Schedule — 8:00 AM daily',
    steps: [
      { icon: Clock, label: 'Schedule trigger' },
      { icon: BrainCircuit, label: 'Generate summary' },
      { icon: Mail, label: 'Send email' },
    ],
    active: true,
    runs: 42,
    lastRun: '8 hours ago',
  },
  {
    id: 2,
    name: 'Auto-index new documents',
    description: 'When a file is uploaded, chunk it, generate embeddings, and add to the knowledge base.',
    trigger: 'Event — New document uploaded',
    steps: [
      { icon: Database, label: 'File upload detected' },
      { icon: BrainCircuit, label: 'Generate embeddings' },
      { icon: Database, label: 'Add to vector store' },
    ],
    active: true,
    runs: 218,
    lastRun: '2 hours ago',
  },
  {
    id: 3,
    name: 'Agent escalation',
    description: 'If a chat agent confidence drops below 70%, escalate to a more capable model automatically.',
    trigger: 'Condition — Confidence < 70%',
    steps: [
      { icon: Bot, label: 'Monitor agent' },
      { icon: Zap, label: 'Detect low confidence' },
      { icon: Bot, label: 'Escalate to GPT-4o' },
    ],
    active: false,
    runs: 15,
    lastRun: '3 days ago',
  },
];

export default function AutomationPage() {
  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Automation</h1>
          <p className="mt-1 text-sm text-muted-foreground">Build workflows that connect your AI modules and trigger actions automatically.</p>
        </div>
        <Button className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">
          <Plus className="h-4 w-4" />
          New Automation
        </Button>
      </div>

      <div className="space-y-4">
        {automations.map((auto, i) => (
          <motion.div
            key={auto.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <GlassCard hover={false} className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className={cn(
                    'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border',
                    auto.active
                      ? 'border-sky-400/20 bg-sky-400/[0.06]'
                      : 'border-white/10 bg-white/[0.02]'
                  )}>
                    <Workflow className={auto.active ? 'h-5 w-5 text-sky-400' : 'h-5 w-5 text-muted-foreground'} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white">{auto.name}</h3>
                      {auto.active ? (
                        <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400">
                          <CheckCircle2 className="h-2.5 w-2.5" /> Active
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 rounded-full bg-white/5 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                          <Pause className="h-2.5 w-2.5" /> Paused
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{auto.description}</p>
                  </div>
                </div>
                <Switch defaultChecked={auto.active} />
              </div>

              {/* Trigger */}
              <div className="mt-4 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2.5">
                <p className="text-xs text-muted-foreground">
                  <span className="font-medium text-white/70">Trigger:</span> {auto.trigger}
                </p>
              </div>

              {/* Flow steps */}
              <div className="mt-4 flex items-center gap-2 overflow-x-auto pb-1">
                {auto.steps.map((step, si) => (
                  <div key={si} className="flex items-center gap-2">
                    <div className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2">
                      <step.icon className="h-4 w-4 text-sky-400/70" />
                      <span className="whitespace-nowrap text-xs font-medium text-white/80">{step.label}</span>
                    </div>
                    {si < auto.steps.length - 1 && (
                      <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground/40" />
                    )}
                  </div>
                ))}
              </div>

              {/* Stats */}
              <div className="mt-4 flex items-center gap-6 text-xs text-muted-foreground">
                <span><strong className="text-white">{auto.runs}</strong> total runs</span>
                <span>Last run <strong className="text-white">{auto.lastRun}</strong></span>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </AppShell>
  );
}
