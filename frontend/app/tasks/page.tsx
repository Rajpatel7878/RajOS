"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  CheckSquare,
  Plus,
  Filter,
  Calendar,
  Flag,
  Circle,
  Trash2,
  Loader2,
  X,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  getTasks,
  createTask,
  completeTask,
  deleteTask,
  type Task,
} from "@/services/api/tasks";

const priorityColors: Record<string, string> = {
  High: "text-rose-400 bg-rose-500/10",
  Medium: "text-amber-400 bg-amber-500/10",
  Low: "text-sky-400 bg-sky-500/10",
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);
  const [filter, setFilter] = useState<"All" | "Pending" | "Completed">("All");

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
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      await createTask({ title: newTitle.trim(), description: newDesc.trim() });
      setNewTitle("");
      setNewDesc("");
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

  const filtered = tasks.filter((t) => {
    if (filter === "Pending") return !t.completed;
    if (filter === "Completed") return t.completed;
    return true;
  });

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Tasks</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {tasks.length} tasks · {tasks.filter((t) => t.completed).length} completed
          </p>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
        >
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showForm ? "Cancel" : "New Task"}
        </Button>
      </div>

      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <GlassCard className="p-5 space-y-3">
            <Input
              placeholder="Task title..."
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="border-white/[0.08] bg-white/[0.02] text-white placeholder:text-muted-foreground/60"
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
            <Input
              placeholder="Description (optional)..."
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              className="border-white/[0.08] bg-white/[0.02] text-white placeholder:text-muted-foreground/60"
            />
            <Button
              onClick={handleCreate}
              disabled={creating || !newTitle.trim()}
              className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
            >
              {creating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Create Task
            </Button>
          </GlassCard>
        </motion.div>
      )}

      {error && (
        <div className="mb-4 rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      <div className="mb-4 flex items-center gap-2">
        {(["All", "Pending", "Completed"] as const).map((f) => (
          <Button
            key={f}
            variant="outline"
            size="sm"
            onClick={() => setFilter(f)}
            className={`gap-2 border-white/10 ${
              filter === f
                ? "bg-sky-400/10 text-sky-300 border-sky-400/30"
                : "bg-white/[0.03] text-muted-foreground hover:text-white"
            }`}
          >
            {f === "All" && <Filter className="h-3.5 w-3.5" />}
            {f === "Pending" && <Circle className="h-3.5 w-3.5" />}
            {f === "Completed" && <CheckSquare className="h-3.5 w-3.5" />}
            {f}
          </Button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02]">
            <CheckSquare className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold text-white">No tasks found</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {filter === "All" ? "Create your first task above." : `No ${filter.toLowerCase()} tasks.`}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((task, i) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <GlassCard hover className="flex items-center gap-4 p-4">
                <button
                  onClick={() => !task.completed && handleComplete(task.id)}
                  className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md border border-white/15 transition-colors hover:border-sky-400"
                  disabled={task.completed}
                >
                  {task.completed && (
                    <CheckSquare className="h-3.5 w-3.5 text-emerald-400" />
                  )}
                </button>
                <div className="flex-1">
                  <p
                    className={
                      task.completed
                        ? "text-sm text-muted-foreground line-through"
                        : "text-sm font-medium text-white"
                    }
                  >
                    {task.title}
                  </p>
                  {task.description && (
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {task.description}
                    </p>
                  )}
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {task.completed ? "Completed" : "Pending"}
                    </span>
                  </div>
                </div>
                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                    task.completed
                      ? priorityColors["Low"]
                      : priorityColors["High"]
                  }`}
                >
                  {task.completed ? "Done" : "Active"}
                </span>
                <button
                  onClick={() => handleDelete(task.id)}
                  className="ml-1 rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-rose-500/10 hover:text-rose-400"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
