"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckSquare,
  Plus,
  Filter,
  Calendar,
  Flag,
  Circle,
  CheckCircle2,
  Trash2,
  Loader2,
  X,
  AlertTriangle,
  Clock,
  Sparkles,
  Layers,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { DailyRoutineCreator } from "@/components/daily-routine-creator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  getTasks,
  createTask,
  completeTask,
  deleteTask,
  type Task,
} from "@/services/api/tasks";

const priorityConfig: Record<string, { label: string; color: string; badge: string; border: string }> = {
  high:   { label: "High",   color: "text-rose-400",   badge: "bg-rose-500/10 text-rose-300 border-rose-500/30",   border: "bg-rose-500" },
  normal: { label: "Normal", color: "text-amber-400",  badge: "bg-amber-500/10 text-amber-300 border-amber-500/30", border: "bg-amber-400" },
  low:    { label: "Low",    color: "text-sky-400",    badge: "bg-sky-500/10 text-sky-300 border-sky-500/30",       border: "bg-sky-400" },
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showRoutineModal, setShowRoutineModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [priority, setPriority] = useState<"high" | "normal" | "low">("normal");
  const [dueDate, setDueDate] = useState("");
  const [creating, setCreating] = useState(false);
  const [filter, setFilter] = useState<"All" | "Pending" | "Completed" | "High">("All");

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await getTasks();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim() || creating) return;
    setCreating(true);
    try {
      await createTask({
        title: newTitle.trim(),
        description: newDesc.trim() || undefined,
        priority,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
      });
      setNewTitle("");
      setNewDesc("");
      setDueDate("");
      setPriority("normal");
      setShowForm(false);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setCreating(false);
    }
  };

  const handleComplete = async (taskId: number) => {
    try {
      await completeTask(taskId);
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, completed: true } : t))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to complete task");
    }
  };

  const handleDelete = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.length - completedCount;
  const now = new Date();
  const overdueCount = tasks.filter(
    (t) => !t.completed && t.due_date && new Date(t.due_date) < now
  ).length;

  const filteredTasks = tasks.filter((t) => {
    if (filter === "Pending") return !t.completed;
    if (filter === "Completed") return t.completed;
    if (filter === "High") return t.priority === "high";
    return true;
  });

  return (
    <AppShell>
      {/* ── Header & Action Bar ── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <div className="flex items-center gap-2">
            <CheckSquare className="h-6 w-6 text-sky-400" />
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Task Command Center
            </h1>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Track, prioritize, and trigger autonomous execution on your objectives.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Button
            type="button"
            onClick={() => setShowRoutineModal(true)}
            variant="outline"
            className="gap-2 rounded-xl border-sky-400/40 bg-sky-400/10 px-4 py-2.5 text-xs font-semibold text-sky-300 hover:bg-sky-400/20 hover:text-white transition-all shadow-[0_0_15px_rgba(56,189,248,0.2)]"
          >
            <Sparkles className="h-3.5 w-3.5" />
            ⚡ Daily Routine (Pushups & Study)
          </Button>

          <Button
            onClick={() => setShowForm(!showForm)}
            className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-400 px-5 py-2.5 text-xs font-semibold text-white shadow-lg shadow-sky-500/25 hover:from-sky-400 hover:to-cyan-300 hover:shadow-sky-500/40 transition-all duration-200"
          >
            {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showForm ? "Cancel" : "New Task"}
          </Button>
        </div>
      </div>

      {/* ── Daily Routine & Habit Creator Modal ── */}
      <DailyRoutineCreator
        isOpen={showRoutineModal}
        onClose={() => setShowRoutineModal(false)}
        onTasksCreated={loadTasks}
      />

      {/* ── 3D Task Overview Stats ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Tasks", value: tasks.length, icon: Layers, color: "text-sky-400", gradient: "sky" },
          { label: "Completed", value: completedCount, icon: CheckCircle2, color: "text-emerald-400", gradient: "emerald" },
          { label: "Pending", value: pendingCount, icon: Clock, color: "text-amber-400", gradient: "cyan" },
          { label: "Overdue", value: overdueCount, icon: AlertTriangle, color: "text-rose-400", gradient: "violet" },
        ].map((item, i) => (
          <GlassCard
            key={item.label}
            hover={true}
            gradient={item.gradient as any}
            delay={i * 0.05}
            className="p-4 flex items-center gap-3.5"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/5">
              <item.icon className={cn("h-5 w-5", item.color)} />
            </div>
            <div>
              <div className="text-2xl font-extrabold text-white leading-none">{item.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{item.label}</div>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* ── Expandable Creation Card ── */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0, y: -16, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, y: -16, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden mb-8"
          >
            <GlassCard hover={false} className="p-6 border-sky-400/30 shadow-[0_0_32px_rgba(56,189,248,0.15)]">
              <div className="flex items-center gap-2 mb-4 text-sm font-semibold text-white">
                <Sparkles className="h-4 w-4 text-sky-400" />
                Create New Objective
              </div>
              <div className="space-y-4">
                <Input
                  placeholder="Task title (e.g., Deploy RAG cluster to production)..."
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="bg-white/[0.03] border-white/[0.08] text-white placeholder:text-muted-foreground/60 h-11 focus:border-sky-400/50"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleCreate();
                    }
                  }}
                />
                <Input
                  placeholder="Optional details or context..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="bg-white/[0.03] border-white/[0.08] text-white placeholder:text-muted-foreground/60 h-11 focus:border-sky-400/50"
                />

                <div className="flex flex-wrap items-center gap-4 pt-2">
                  {/* Priority selector */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Priority:</span>
                    <div className="flex gap-1.5">
                      {(["low", "normal", "high"] as const).map((p) => (
                        <button
                          key={p}
                          type="button"
                          onClick={() => setPriority(p)}
                          className={cn(
                            "rounded-lg px-3 py-1.5 text-xs font-semibold uppercase tracking-wider transition-all",
                            priority === p
                              ? priorityConfig[p].badge + " shadow-sm scale-105"
                              : "border border-white/10 bg-white/5 text-muted-foreground hover:text-white"
                          )}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Due date input */}
                  <div className="flex items-center gap-2 ml-auto">
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5" /> Due:
                    </span>
                    <input
                      type="date"
                      value={dueDate}
                      onChange={(e) => setDueDate(e.target.value)}
                      className="rounded-lg border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-white focus:outline-none focus:border-sky-400/50"
                    />
                  </div>

                  <Button
                    onClick={handleCreate}
                    disabled={creating || !newTitle.trim()}
                    className="rounded-xl bg-gradient-to-r from-sky-500 to-cyan-400 px-5 text-xs font-semibold text-white shadow-md hover:from-sky-400 hover:to-cyan-300 disabled:opacity-50"
                  >
                    {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save Task"}
                  </Button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Filters Bar ── */}
      <div className="flex items-center gap-2 mb-6 border-b border-white/[0.06] pb-4">
        {(["All", "Pending", "Completed", "High"] as const).map((item) => (
          <button
            key={item}
            onClick={() => setFilter(item)}
            className={cn(
              "rounded-xl px-4 py-2 text-xs font-semibold transition-all duration-200",
              filter === item
                ? "bg-white/10 text-white shadow-sm border border-white/15"
                : "text-muted-foreground hover:text-white hover:bg-white/[0.04]"
            )}
          >
            {item}
            <span className="ml-1.5 text-[10px] opacity-70">
              {item === "All"
                ? tasks.length
                : item === "Pending"
                ? pendingCount
                : item === "Completed"
                ? completedCount
                : tasks.filter((t) => t.priority === "high").length}
            </span>
          </button>
        ))}
      </div>

      {/* ── Task Cards List ── */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
          <p className="mt-3 text-xs text-muted-foreground">Retrieving tasks...</p>
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-white/5 shadow-inner">
            <CheckSquare className="h-8 w-8 text-muted-foreground/50" />
          </div>
          <h3 className="mt-4 text-base font-semibold text-white">No tasks found</h3>
          <p className="mt-1 text-xs text-muted-foreground max-w-sm">
            You are all caught up! Create a new objective to keep your autonomous agents busy.
          </p>
        </div>
      ) : (
        <div className="grid gap-3">
          {filteredTasks.map((task, i) => {
            const pConfig = priorityConfig[task.priority?.toLowerCase() ?? "normal"] ?? priorityConfig.normal;
            const isOverdue = !task.completed && task.due_date && new Date(task.due_date) < now;

            return (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: i * 0.03 }}
                className={cn(
                  "group relative flex items-center gap-4 overflow-hidden rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4.5 backdrop-blur-xl transition-all duration-300 hover:-translate-y-0.5 hover:border-white/15 hover:bg-white/[0.05] hover:shadow-[0_12px_24px_-8px_rgba(0,0,0,0.5)]",
                  task.completed && "opacity-60 bg-transparent"
                )}
              >
                {/* 3D Priority side bar */}
                <div className={cn("absolute inset-y-0 left-0 w-1", pConfig.border)} />

                {/* Complete checkbox button */}
                <button
                  onClick={() => handleComplete(task.id)}
                  disabled={task.completed}
                  className={cn(
                    "flex h-6 w-6 shrink-0 items-center justify-center rounded-lg border transition-all duration-200 ml-1",
                    task.completed
                      ? "border-emerald-400 bg-emerald-500/20 text-emerald-400"
                      : "border-white/20 hover:border-emerald-400/50 hover:bg-emerald-400/10 text-transparent hover:text-emerald-400"
                  )}
                >
                  <CheckCircle2 className="h-4 w-4" />
                </button>

                {/* Task Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2.5">
                    <h3
                      className={cn(
                        "text-sm font-medium text-white truncate",
                        task.completed && "line-through text-muted-foreground"
                      )}
                    >
                      {task.title}
                    </h3>
                    <span className={cn("rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider", pConfig.badge)}>
                      {pConfig.label}
                    </span>
                    {isOverdue && (
                      <span className="flex items-center gap-1 rounded-md border border-rose-500/30 bg-rose-500/10 px-1.5 py-0.5 text-[10px] font-bold text-rose-300">
                        <AlertTriangle className="h-3 w-3" /> Overdue
                      </span>
                    )}
                  </div>

                  {task.description && (
                    <p className="mt-1 text-xs text-muted-foreground truncate max-w-xl">
                      {task.description}
                    </p>
                  )}

                  {task.due_date && (
                    <div className="mt-2 flex items-center gap-1.5 text-[11px] text-muted-foreground">
                      <Clock className="h-3 w-3 text-sky-400" />
                      Due: {new Date(task.due_date).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                    </div>
                  )}
                </div>

                {/* Delete button */}
                <button
                  onClick={() => handleDelete(task.id)}
                  className="opacity-0 group-hover:opacity-100 flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 text-muted-foreground hover:text-rose-400 hover:border-rose-400/30 hover:bg-rose-500/10 transition-all duration-200"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </motion.div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
