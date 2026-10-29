'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Workflow,
  Plus,
  Zap,
  Clock,
  CheckCircle2,
  Pause,
  ArrowRight,
  Play,
  Trash2,
  Loader2,
  X,
  AlertTriangle,
  Calendar,
  Timer,
  Radio,
  Target,
  History,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Pencil,
  Eye,
  Ban,
  Save,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';
import {
  listAutomations,
  createAutomation,
  updateAutomation,
  deleteAutomation,
  enableAutomation,
  disableAutomation,
  runAutomation,
  cancelAutomation,
  getAutomationRuns,
  previewDraftAutomation,
  type Automation,
  type AutomationCreate,
  type AutomationRun,
  type ActionStep,
  type DraftPreview,
} from '@/services/api/automation';

// ── Trigger type helpers ────────────────────────────────────────────────────

const TRIGGER_TYPES = [
  { value: 'schedule', label: 'Schedule', icon: Calendar, color: 'sky' },
  { value: 'interval', label: 'Interval', icon: Timer, color: 'cyan' },
  { value: 'event', label: 'Event', icon: Radio, color: 'violet' },
  { value: 'condition', label: 'Condition', icon: Target, color: 'amber' },
  { value: 'onetime', label: 'One-Time', icon: Zap, color: 'emerald' },
] as const;

function describeTrigger(triggerType: string, tc?: TriggerConfigLike): string {
  switch (triggerType) {
    case 'schedule': {
      const time = tc?.time || '??:??';
      const days = tc?.days;
      if (days && days.length > 0 && days.length < 7) return `Daily at ${time} (${days.join(', ')})`;
      return `Daily at ${time}`;
    }
    case 'interval':
      return `Every ${tc?.interval_minutes || '??'} minutes`;
    case 'event':
      return `On event: ${tc?.event_type || 'unknown'}`;
    case 'condition':
      return 'When conditions met';
    case 'deadline':
      return `Reminder ${tc?.deadline_hours ?? 24}h before a task is due`;
    case 'onetime':
      return `One-time: ${tc?.run_at ? new Date(tc.run_at).toLocaleString() : 'not set'}`;
    default:
      return triggerType || 'Unknown';
  }
}

interface TriggerConfigLike {
  time?: string;
  days?: string[];
  interval_minutes?: number;
  event_type?: string;
  deadline_hours?: number;
  run_at?: string;
}

function triggerLabel(auto: Automation): string {
  const label = describeTrigger(auto.trigger_type, auto.trigger_config);
  if (label && label !== 'Unknown') return label;
  return auto.trigger || auto.trigger_type || 'Unknown';
}

const TRIGGER_FILTERS: Record<string, (a: Automation) => boolean> = {
  overdue: a => (a.conditions || []).some(
    (c: any) => c?.field === 'overdue_tasks'
  ),
  agent: a => (a.actions || []).some(s => s.tool_name === 'run_agent'),
  notify: a => (a.actions || []).some(s => s.tool_name === 'send_notification'),
};

/** Human-readable summary of a trigger, used across the list and the preview. */
function conditionSummary(node: any): string {
  if (!node) return '';
  if (node.op) {
    const joiner = node.op === 'and' ? ' AND ' : node.op === 'or' ? ' OR ' : ' NOT ';
    const inner = (node.rules || []).map(conditionSummary).filter(Boolean).join(joiner);
    return node.op === 'not' ? `NOT(${inner})` : `(${inner})`;
  }
  if (!node.field) return '';
  return `${node.field} ${node.operator} ${JSON.stringify(node.value)}`;
}

function runStatusStyle(status: string): { icon: string; className: string } {
  switch (status) {
    case 'completed':
      return { icon: '✓', className: 'bg-emerald-500/10 text-emerald-400' };
    case 'failed':
      return { icon: '✕', className: 'bg-red-500/10 text-red-400' };
    case 'running':
      return { icon: '\u27f3', className: 'bg-sky-500/10 text-sky-400' };
    case 'partial':
      return { icon: '!', className: 'bg-amber-500/10 text-amber-400' };
    case 'cancelled':
      return { icon: '⊘', className: 'bg-orange-500/10 text-orange-400' };
    default:
      return { icon: '~', className: 'bg-white/5 text-white/50' };
  }
}

function triggerIcon(type: string) {
  const found = TRIGGER_TYPES.find(t => t.value === type);
  return found?.icon || Workflow;
}

function triggerColor(type: string) {
  const found = TRIGGER_TYPES.find(t => t.value === type);
  return found?.color || 'sky';
}

function relativeTime(dateStr?: string | null): string {
  if (!dateStr) return 'Never';
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDays = Math.floor(diffHr / 24);
  return `${diffDays}d ago`;
}

// ── Main Page ───────────────────────────────────────────────────────────────

export default function AutomationPage() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [runs, setRuns] = useState<Record<number, AutomationRun[]>>({});
  const [runningIds, setRunningIds] = useState<Set<number>>(new Set());
  const [togglingIds, setTogglingIds] = useState<Set<number>>(new Set());

  // Create form state
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newTriggerType, setNewTriggerType] = useState('schedule');
  const [newTime, setNewTime] = useState('08:00');
  const [newIntervalMin, setNewIntervalMin] = useState('60');
  const [newEventType, setNewEventType] = useState('task.completed');
  const [newOneTime, setNewOneTime] = useState('');
  const [newDeadlineHours, setNewDeadlineHours] = useState('24');
  const [newTimezone, setNewTimezone] = useState('Asia/Kolkata');
  const [newActionTool, setNewActionTool] = useState('send_notification');
  const [newActionArgs, setNewActionArgs] = useState('{}');
  const [creating, setCreating] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [draft, setDraft] = useState<DraftPreview | null>(null);

  // Run cancellation + inline editing
  const [cancellingIds, setCancellingIds] = useState<Set<number>>(new Set());
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const [editTime, setEditTime] = useState('08:00');
  const [editTimezone, setEditTimezone] = useState('Asia/Kolkata');
  const [savingEdit, setSavingEdit] = useState(false);

  // ── Load automations ──────────────────────────────────────────────────

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await listAutomations();
      setAutomations(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load automations');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── Toggle enable / disable ───────────────────────────────────────────

  const handleToggle = async (auto: Automation) => {
    setTogglingIds(prev => new Set(prev).add(auto.id));
    try {
      const updated = auto.enabled
        ? await disableAutomation(auto.id)
        : await enableAutomation(auto.id);
      setAutomations(prev => prev.map(a => a.id === auto.id ? updated : a));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setTogglingIds(prev => { const s = new Set(prev); s.delete(auto.id); return s; });
    }
  };

  // ── Manual run ────────────────────────────────────────────────────────

  const handleRun = async (id: number) => {
    setRunningIds(prev => new Set(prev).add(id));
    try {
      await runAutomation(id);
      await load(); // refresh to get last_run_at update
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRunningIds(prev => { const s = new Set(prev); s.delete(id); return s; });
    }
  };

  // ── Delete ────────────────────────────────────────────────────────────

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this automation?')) return;
    try {
      await deleteAutomation(id);
      setAutomations(prev => prev.filter(a => a.id !== id));
    } catch (e: any) {
      setError(e.message);
    }
  };

  // ── Expand to show run history ────────────────────────────────────────

  const handleExpand = async (id: number) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!runs[id]) {
      try {
        const r = await getAutomationRuns(id);
        setRuns(prev => ({ ...prev, [id]: r }));
      } catch { /* ignore */ }
    }
  };

  // ── Cancel an in-flight run ───────────────────────────────────────────

  const handleCancelRun = async (id: number) => {
    setCancellingIds(prev => new Set(prev).add(id));
    try {
      await cancelAutomation(id);
      const r = await getAutomationRuns(id);
      setRuns(prev => ({ ...prev, [id]: r }));
      await load();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setCancellingIds(prev => { const s = new Set(prev); s.delete(id); return s; });
    }
  };

  // ── Create automation (preview → confirm) ─────────────────────────────

  const buildPayload = (): AutomationCreate => {
    let parsedArgs: Record<string, unknown> = {};
    try { parsedArgs = JSON.parse(newActionArgs || '{}'); } catch { /* use empty */ }

    const triggerConfig: Record<string, unknown> = {};
    if (newTriggerType === 'schedule') triggerConfig.time = newTime;
    if (newTriggerType === 'interval') triggerConfig.interval_minutes = parseInt(newIntervalMin) || 60;
    if (newTriggerType === 'event') triggerConfig.event_type = newEventType;
    if (newTriggerType === 'onetime') triggerConfig.run_at = newOneTime;
    if (newTriggerType === 'deadline') triggerConfig.deadline_hours = parseInt(newDeadlineHours) || 24;

    return {
      name: newName.trim(),
      description: newDesc.trim() || undefined,
      trigger_type: newTriggerType,
      trigger_config: triggerConfig,
      timezone: newTimezone.trim() || 'Asia/Kolkata',
      actions: [{ tool_name: newActionTool, arguments: parsedArgs }],
    };
  };

  const resetCreateForm = () => {
    setDraft(null);
    setNewName('');
    setNewDesc('');
    setNewActionTool('send_notification');
    setNewActionArgs('{}');
    setNewOneTime('');
  };

  const handlePreview = async () => {
    if (!newName.trim()) return;
    setPreviewing(true);
    try {
      setDraft(await previewDraftAutomation(buildPayload()));
    } catch (e: any) {
      setDraft(null);
      setError(e.message);
    } finally {
      setPreviewing(false);
    }
  };

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      // The backend re-validates everything; the preview is only a heads-up.
      const created = await createAutomation(buildPayload());
      setAutomations(prev => [created, ...prev]);
      setShowCreate(false);
      resetCreateForm();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  };

  // ── Inline edit ───────────────────────────────────────────────────────

  const startEdit = (auto: Automation) => {
    setEditingId(auto.id);
    setEditName(auto.name);
    setEditTime(auto.trigger_config?.time || '08:00');
    setEditTimezone(auto.timezone || 'Asia/Kolkata');
    setError('');
  };

  const handleSaveEdit = async (auto: Automation) => {
    setSavingEdit(true);
    try {
      const updated = await updateAutomation(auto.id, {
        name: editName.trim() || auto.name,
        timezone: editTimezone.trim(),
        ...(auto.trigger_type === 'schedule'
          ? { trigger_config: { ...(auto.trigger_config || {}), time: editTime } }
          : {}),
      });
      setAutomations(prev => prev.map(a => (a.id === auto.id ? updated : a)));
      setEditingId(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSavingEdit(false);
    }
  };

  // ── Stats ─────────────────────────────────────────────────────────────

  const total = automations.length;
  const active = automations.filter(a => a.enabled).length;
  const paused = total - active;

  // ── Render ────────────────────────────────────────────────────────────

  return (
    <AppShell>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Automation Engine</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Create workflows that trigger actions automatically based on schedules, events, and conditions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={load}
            className="gap-1.5 border-white/10 bg-white/5 text-white/70 hover:bg-white/10"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
          <Button
            onClick={() => setShowCreate(s => !s)}
            className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
          >
            <Plus className="h-4 w-4" />
            New Automation
          </Button>
        </div>
      </div>

      {/* Error toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-4 flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400"
          >
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
            <button onClick={() => setError('')} className="ml-auto">
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats row */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        {[
          { label: 'Total', value: total, color: 'text-white', icon: Workflow },
          { label: 'Active', value: active, color: 'text-emerald-400', icon: CheckCircle2 },
          { label: 'Paused', value: paused, color: 'text-amber-400', icon: Pause },
        ].map((s, i) => (
          <GlassCard key={i} hover={false} className="px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
                <s.icon className={cn('h-4 w-4', s.color)} />
              </div>
              <div>
                <p className={cn('text-lg font-bold', s.color)}>{s.value}</p>
                <p className="text-xs text-muted-foreground">{s.label}</p>
              </div>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Create form */}
      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6 overflow-hidden"
          >
            <GlassCard hover={false} className="p-6">
              <h3 className="mb-4 text-sm font-semibold text-white">Create Automation</h3>

              <div className="space-y-4">
                <Input
                  placeholder="Automation name..."
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  className="border-white/10 bg-white/5"
                />
                <Input
                  placeholder="Description (optional)..."
                  value={newDesc}
                  onChange={e => setNewDesc(e.target.value)}
                  className="border-white/10 bg-white/5"
                />

                {/* Trigger type pills */}
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">TRIGGER TYPE</p>
                  <div className="flex flex-wrap gap-2">
                    {TRIGGER_TYPES.map(t => {
                      const Icon = t.icon;
                      return (
                        <button
                          key={t.value}
                          onClick={() => setNewTriggerType(t.value)}
                          className={cn(
                            'flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all',
                            newTriggerType === t.value
                              ? 'border-sky-500/30 bg-sky-500/10 text-sky-400'
                              : 'border-white/10 bg-white/5 text-white/60 hover:bg-white/10'
                          )}
                        >
                          <Icon className="h-3 w-3" />
                          {t.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Trigger config */}
                {newTriggerType === 'schedule' && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Time (24h)</p>
                    <Input
                      type="time"
                      value={newTime}
                      onChange={e => setNewTime(e.target.value)}
                      className="w-40 border-white/10 bg-white/5"
                    />
                  </div>
                )}
                {newTriggerType === 'interval' && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Interval (minutes)</p>
                    <Input
                      type="number"
                      value={newIntervalMin}
                      onChange={e => setNewIntervalMin(e.target.value)}
                      className="w-40 border-white/10 bg-white/5"
                      min="1"
                    />
                  </div>
                )}
                {newTriggerType === 'event' && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Event type</p>
                    <Input
                      value={newEventType}
                      onChange={e => setNewEventType(e.target.value)}
                      placeholder="e.g. task.completed"
                      className="w-64 border-white/10 bg-white/5"
                    />
                  </div>
                )}
                {newTriggerType === 'onetime' && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Run at</p>
                    <Input
                      type="datetime-local"
                      value={newOneTime}
                      onChange={e => setNewOneTime(e.target.value)}
                      className="w-64 border-white/10 bg-white/5"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      Interpreted in the automation timezone below.
                    </p>
                  </div>
                )}
                {newTriggerType === 'deadline' && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Hours before a task is due</p>
                    <Input
                      type="number"
                      value={newDeadlineHours}
                      onChange={e => setNewDeadlineHours(e.target.value)}
                      className="w-40 border-white/10 bg-white/5"
                      min="1"
                    />
                  </div>
                )}
                {newTriggerType === 'condition' && (
                  <p className="text-xs text-muted-foreground">
                    Conditions are checked on a polling schedule before the actions run.
                  </p>
                )}

                {/* Timezone */}
                <div>
                  <p className="mb-1 text-xs text-muted-foreground">Timezone</p>
                  <Input
                    value={newTimezone}
                    onChange={e => setNewTimezone(e.target.value)}
                    placeholder="e.g. Asia/Kolkata"
                    className="w-64 border-white/10 bg-white/5"
                  />
                </div>

                {/* Action */}
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">ACTION</p>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="mb-1 text-xs text-muted-foreground">Tool name</p>
                      <Input
                        value={newActionTool}
                        onChange={e => setNewActionTool(e.target.value)}
                        placeholder="send_notification"
                        className="border-white/10 bg-white/5"
                      />
                    </div>
                    <div>
                      <p className="mb-1 text-xs text-muted-foreground">Arguments (JSON)</p>
                      <Input
                        value={newActionArgs}
                        onChange={e => setNewActionArgs(e.target.value)}
                        placeholder='{"message": "Hello"}'
                        className="border-white/10 bg-white/5"
                      />
                    </div>
                  </div>
                </div>

                {/* Structured preview + confirmation */}
                {draft && (
                  <div className="rounded-xl border border-sky-500/20 bg-sky-500/[0.04] p-4">
                    <p className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-sky-400">
                      <Eye className="h-3.5 w-3.5" />
                      Automation preview
                    </p>
                    <dl className="space-y-2 text-xs">
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-muted-foreground">Name</dt>
                        <dd className="text-white">{draft.name}</dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-muted-foreground">Trigger</dt>
                        <dd className="text-white">
                          {describeTrigger(draft.trigger_type, draft.trigger_config)}
                        </dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-muted-foreground">Timezone</dt>
                        <dd className="text-white">{draft.timezone}</dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-muted-foreground">Actions</dt>
                        <dd className="text-white">
                          {draft.actions.map((a, i) => (
                            <span key={i} className="block">
                              {i + 1}. {a.description || a.tool_name}
                            </span>
                          ))}
                        </dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-muted-foreground">Next run</dt>
                        <dd className="text-white">
                          {draft.next_run_at
                            ? new Date(draft.next_run_at).toLocaleString()
                            : 'Fires on trigger only'}
                        </dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 shrink-0 text-muted-foreground">On failure</dt>
                        <dd className="text-white">{draft.failure_policy}</dd>
                      </div>
                    </dl>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  {draft ? (
                    <Button
                      onClick={handleCreate}
                      disabled={creating}
                      className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
                    >
                      {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                      Create automation
                    </Button>
                  ) : (
                    <Button
                      onClick={handlePreview}
                      disabled={previewing || !newName.trim()}
                      className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
                    >
                      {previewing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Eye className="h-4 w-4" />}
                      Review &amp; create
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    onClick={() => { setShowCreate(false); resetCreateForm(); }}
                    className="border-white/10 text-white/70"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-36 animate-pulse rounded-2xl bg-white/5" />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && automations.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-sky-500/10">
            <Workflow className="h-8 w-8 text-sky-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">No automations yet</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first automation to start triggering actions automatically.
          </p>
          <Button
            onClick={() => setShowCreate(true)}
            className="mt-4 gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
          >
            <Plus className="h-4 w-4" />
            Create Automation
          </Button>
        </div>
      )}

      {/* Automation list */}
      {!loading && (
        <div className="space-y-4">
          {automations.map((auto, i) => {
            const TriggerIcon = triggerIcon(auto.trigger_type);
            const color = triggerColor(auto.trigger_type);
            const isExpanded = expandedId === auto.id;
            const isRunning = runningIds.has(auto.id);
            const isToggling = togglingIds.has(auto.id);
            const autoRuns = runs[auto.id] || [];

            return (
              <motion.div
                key={auto.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <GlassCard hover={false} className="p-6">
                  {/* Top row */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={cn(
                        'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border',
                        auto.enabled
                          ? `border-${color}-400/20 bg-${color}-400/[0.06]`
                          : 'border-white/10 bg-white/[0.02]'
                      )}>
                        <TriggerIcon className={cn(
                          'h-5 w-5',
                          auto.enabled ? `text-${color}-400` : 'text-muted-foreground'
                        )} />
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-white">{auto.name}</h3>
                          {auto.enabled ? (
                            <span className="flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-400">
                              <CheckCircle2 className="h-2.5 w-2.5" /> Active
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 rounded-full bg-white/5 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                              <Pause className="h-2.5 w-2.5" /> Paused
                            </span>
                          )}
                          <span className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] font-medium text-white/50">
                            {auto.trigger_type}
                          </span>
                        </div>
                        {auto.description && (
                          <p className="mt-1 text-sm text-muted-foreground">{auto.description}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {isToggling ? (
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      ) : (
                        <Switch
                          checked={auto.enabled}
                          onCheckedChange={() => handleToggle(auto)}
                        />
                      )}
                    </div>
                  </div>

                  {/* Trigger info */}
                  <div className="mt-4 space-y-1 rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-2.5">
                    <p className="text-xs text-muted-foreground">
                      <span className="font-medium text-white/70">Trigger:</span>{' '}
                      {triggerLabel(auto)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <span className="font-medium text-white/70">Timezone:</span>{' '}
                      {auto.timezone}
                    </p>
                    {(auto.conditions?.length ?? 0) > 0 && (
                      <p className="text-xs text-muted-foreground">
                        <span className="font-medium text-white/70">Runs only if:</span>{' '}
                        {(auto.conditions || []).map(conditionSummary).filter(Boolean).join(' AND ')}
                      </p>
                    )}
                  </div>

                  {/* Inline edit */}
                  <AnimatePresence>
                    {editingId === auto.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-4 space-y-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                          <div className="grid gap-3 sm:grid-cols-3">
                            <div>
                              <p className="mb-1 text-xs text-muted-foreground">Name</p>
                              <Input
                                value={editName}
                                onChange={e => setEditName(e.target.value)}
                                className="border-white/10 bg-white/5"
                              />
                            </div>
                            {auto.trigger_type === 'schedule' && (
                              <div>
                                <p className="mb-1 text-xs text-muted-foreground">Time</p>
                                <Input
                                  type="time"
                                  value={editTime}
                                  onChange={e => setEditTime(e.target.value)}
                                  className="border-white/10 bg-white/5"
                                />
                              </div>
                            )}
                            <div>
                              <p className="mb-1 text-xs text-muted-foreground">Timezone</p>
                              <Input
                                value={editTimezone}
                                onChange={e => setEditTimezone(e.target.value)}
                                className="border-white/10 bg-white/5"
                              />
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleSaveEdit(auto)}
                              disabled={savingEdit}
                              className="gap-1.5 bg-gradient-to-r from-sky-500 to-cyan-500 text-xs text-white"
                            >
                              {savingEdit ? (
                                <Loader2 className="h-3 w-3 animate-spin" />
                              ) : (
                                <Save className="h-3 w-3" />
                              )}
                              Save
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setEditingId(null)}
                              className="border-white/10 bg-white/5 text-xs text-white/70"
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Actions list */}
                  {auto.actions && auto.actions.length > 0 && (
                    <div className="mt-4 flex items-center gap-2 overflow-x-auto pb-1">
                      {auto.actions.map((action: ActionStep, si: number) => (
                        <div key={si} className="flex items-center gap-2">
                          <div className="flex items-center gap-2 rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2">
                            <Zap className="h-4 w-4 text-sky-400/70" />
                            <span className="whitespace-nowrap text-xs font-medium text-white/80">
                              {action.description || action.tool_name}
                            </span>
                          </div>
                          {si < auto.actions!.length - 1 && (
                            <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground/40" />
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Bottom row: stats + actions */}
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-6 text-xs text-muted-foreground">
                      {auto.next_run_at && (
                        <span>
                          Next run:{' '}
                          <strong className="text-white">
                            {new Date(auto.next_run_at).toLocaleString()}
                          </strong>
                        </span>
                      )}
                      <span>
                        Last run:{' '}
                        <strong className="text-white">{relativeTime(auto.last_run_at)}</strong>
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleExpand(auto.id)}
                        className="gap-1 border-white/10 bg-white/5 text-xs text-white/70 hover:bg-white/10"
                      >
                        <History className="h-3 w-3" />
                        Runs
                        {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                      </Button>
                      {isRunning ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCancelRun(auto.id)}
                          disabled={cancellingIds.has(auto.id)}
                          className="gap-1 border-orange-500/20 bg-orange-500/5 text-xs text-orange-400 hover:bg-orange-500/10"
                        >
                          {cancellingIds.has(auto.id) ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <Ban className="h-3 w-3" />
                          )}
                          Cancel
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRun(auto.id)}
                          className="gap-1 border-white/10 bg-white/5 text-xs text-white/70 hover:bg-white/10"
                        >
                          <Play className="h-3 w-3" />
                          Run Now
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => editingId === auto.id ? setEditingId(null) : startEdit(auto)}
                        className="gap-1 border-white/10 bg-white/5 text-xs text-white/70 hover:bg-white/10"
                      >
                        <Pencil className="h-3 w-3" />
                        Edit
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(auto.id)}
                        className="gap-1 border-red-500/20 bg-red-500/5 text-xs text-red-400 hover:bg-red-500/10"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>

                  {/* Expanded: run history */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-4 border-t border-white/[0.06] pt-4">
                          <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                            Execution History
                          </p>
                          {autoRuns.length === 0 ? (
                            <p className="text-xs text-muted-foreground">No runs yet.</p>
                          ) : (
                            <div className="space-y-2">
                              {autoRuns.slice(0, 10).map(run => (
                                <div
                                  key={run.id}
                                  className="flex items-center justify-between rounded-lg border border-white/[0.04] bg-white/[0.02] px-3 py-2"
                                >
                                  <div className="flex items-center gap-3">
                                    <span className={cn(
                                      'flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold',
                                      runStatusStyle(run.status).className
                                    )}>
                                      {runStatusStyle(run.status).icon}
                                    </span>
                                    <div>
                                      <p className="text-xs text-white">
                                        {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                                        <span className="ml-2 text-muted-foreground">
                                          {run.actions_completed}/{run.actions_attempted} actions
                                        </span>
                                      </p>
                                      {run.error_message && (
                                        <p className={cn(
                                          'mt-0.5 text-[10px]',
                                          run.status === 'failed' ? 'text-red-400' : 'text-muted-foreground'
                                        )}>
                                          {run.error_message}
                                        </p>
                                      )}
                                      {run.trigger_source && (
                                        <p className="mt-0.5 text-[10px] text-muted-foreground/70">
                                          via {run.trigger_source}
                                        </p>
                                      )}
                                    </div>
                                  </div>
                                  <span className="text-[10px] text-muted-foreground">
                                    {relativeTime(run.started_at)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
