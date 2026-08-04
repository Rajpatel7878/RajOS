'use client';

import { motion } from 'framer-motion';
import { CheckSquare, Plus, Filter, Calendar, Flag, Circle } from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';

const sampleTasks = [
  { id: 1, title: 'Review Q3 agent performance report', priority: 'High', due: 'Today', status: 'In Progress' },
  { id: 2, title: 'Train memory model on new knowledge base', priority: 'Medium', due: 'Tomorrow', status: 'Pending' },
  { id: 3, title: 'Deploy customer support automation', priority: 'High', due: 'Aug 6', status: 'Pending' },
  { id: 4, title: 'Audit API key permissions', priority: 'Low', due: 'Aug 8', status: 'Pending' },
  { id: 5, title: 'Schedule weekly analytics digest', priority: 'Medium', due: 'Aug 10', status: 'Completed' },
];

const priorityColors: Record<string, string> = {
  High: 'text-rose-400 bg-rose-500/10',
  Medium: 'text-amber-400 bg-amber-500/10',
  Low: 'text-sky-400 bg-sky-500/10',
};

const statusIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  'In Progress': Circle,
  Pending: Circle,
  Completed: CheckSquare,
};

export default function TasksPage() {
  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Tasks</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage and track AI-assisted tasks and to-dos.</p>
        </div>
        <Button className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">
          <Plus className="h-4 w-4" />
          New Task
        </Button>
      </div>

      <div className="mb-4 flex items-center gap-2">
        <Button variant="outline" size="sm" className="gap-2 border-white/10 bg-white/[0.03] text-muted-foreground hover:text-white">
          <Filter className="h-3.5 w-3.5" />
          All
        </Button>
        <Button variant="outline" size="sm" className="gap-2 border-white/10 bg-white/[0.03] text-muted-foreground hover:text-white">
          <Calendar className="h-3.5 w-3.5" />
          Due Date
        </Button>
        <Button variant="outline" size="sm" className="gap-2 border-white/10 bg-white/[0.03] text-muted-foreground hover:text-white">
          <Flag className="h-3.5 w-3.5" />
          Priority
        </Button>
      </div>

      <div className="space-y-3">
        {sampleTasks.map((task, i) => {
          const StatusIcon = statusIcons[task.status] ?? Circle;
          return (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
            >
              <GlassCard hover className="flex items-center gap-4 p-4">
                <button className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md border border-white/15 transition-colors hover:border-sky-400">
                  {task.status === 'Completed' && <CheckSquare className="h-3.5 w-3.5 text-emerald-400" />}
                </button>
                <div className="flex-1">
                  <p className={task.status === 'Completed' ? 'text-sm text-muted-foreground line-through' : 'text-sm font-medium text-white'}>
                    {task.title}
                  </p>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <StatusIcon className="h-3 w-3" />
                      {task.status}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {task.due}
                    </span>
                  </div>
                </div>
                <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${priorityColors[task.priority]}`}>
                  {task.priority}
                </span>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>
    </AppShell>
  );
}
