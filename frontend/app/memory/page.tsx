"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  BrainCircuit,
  Plus,
  Filter,
  Sparkles,
  Trash2,
  Loader2,
  X,
  Database,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  getMemories,
  createMemory,
  deleteMemory,
  type Memory,
} from "@/services/api/memory";

export default function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [creating, setCreating] = useState(false);

  const loadMemories = async () => {
    try {
      setLoading(true);
      const data = await getMemories();
      setMemories(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load memories");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, []);

  const handleCreate = async () => {
    if (!newKey.trim() || !newValue.trim()) return;
    setCreating(true);
    try {
      await createMemory({ key: newKey.trim(), value: newValue.trim() });
      setNewKey("");
      setNewValue("");
      setShowForm(false);
      await loadMemories();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save memory");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (memoryId: number) => {
    try {
      await deleteMemory(memoryId);
      setMemories((prev) => prev.filter((m) => m.id !== memoryId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete memory");
    }
  };

  const filtered = useMemo(
    () =>
      memories.filter(
        (m) =>
          !search ||
          m.key.toLowerCase().includes(search.toLowerCase()) ||
          m.value.toLowerCase().includes(search.toLowerCase())
      ),
    [memories, search]
  );

  return (
    <AppShell>
      {/* Stats row */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[
          {
            label: "Total Memories",
            value: memories.length,
            icon: BrainCircuit,
            color: "text-sky-400",
          },
          {
            label: "Filtered",
            value: filtered.length,
            icon: Filter,
            color: "text-violet-400",
          },
          {
            label: "Memory Store",
            value: "SQLite",
            icon: Database,
            color: "text-emerald-400",
          },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.06} className="p-5">
            <div className="flex items-center justify-between">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]",
                  stat.color
                )}
              >
                <stat.icon className="h-5 w-5" />
              </div>
            </div>
            <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-sm text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search memories..."
              className="w-full bg-transparent text-sm text-white placeholder:text-muted-foreground focus:outline-none lg:w-48"
            />
          </div>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
        >
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showForm ? "Cancel" : "Add Memory"}
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
              placeholder="Memory key (e.g. favorite_language)..."
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
              className="border-white/[0.08] bg-white/[0.02] text-white placeholder:text-muted-foreground/60"
            />
            <textarea
              placeholder="Memory value (e.g. Python)..."
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 py-2 text-sm text-white placeholder:text-muted-foreground/60 focus:outline-none focus:border-sky-400/50 resize-none"
            />
            <Button
              onClick={handleCreate}
              disabled={creating || !newKey.trim() || !newValue.trim()}
              className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
            >
              {creating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              Save Memory
            </Button>
          </GlassCard>
        </motion.div>
      )}

      {error && (
        <div className="mb-4 rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Memory cards */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <AnimatePresence mode="popLayout">
            {filtered.map((item, i) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, delay: i * 0.04 }}
              >
                <GlassCard className="group h-full p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <BrainCircuit className="h-4 w-4 text-sky-400/70 shrink-0" />
                      <span className="text-xs font-semibold uppercase tracking-wider text-sky-400 truncate">
                        {item.key}
                      </span>
                    </div>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="opacity-0 group-hover:opacity-100 shrink-0 rounded-lg p-1 text-muted-foreground transition-all hover:bg-rose-500/10 hover:text-rose-400"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <p className="mt-3 text-sm leading-relaxed text-white">
                    {item.value}
                  </p>

                  <div className="mt-4 flex items-center justify-between border-t border-white/[0.06] pt-3">
                    <span className="text-xs text-muted-foreground">
                      ID #{item.id}
                    </span>
                    <span className="rounded-full border border-sky-400/30 bg-sky-400/10 px-2 py-0.5 text-[10px] font-semibold text-sky-300">
                      Memory
                    </span>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02]">
            <Search className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold text-white">No memories found</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {search
              ? "Try adjusting your search."
              : "Add your first memory above."}
          </p>
        </div>
      )}
    </AppShell>
  );
}
