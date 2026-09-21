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
  Tag,
  ShieldAlert,
  Zap,
  Bot,
  User,
  Edit2,
  Check,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  getMemories,
  createMemory,
  updateMemory,
  deleteMemory,
  processExplicitMemory,
  getMemoryStats,
  type Memory,
  type MemoryStats,
} from "@/services/api/memory";

const CATEGORIES = [
  { id: "all", label: "All" },
  { id: "preference", label: "Preferences" },
  { id: "goal", label: "Goals" },
  { id: "project", label: "Projects" },
  { id: "instruction", label: "Instructions" },
  { id: "fact", label: "Facts" },
];

export default function MemoryPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const [showForm, setShowForm] = useState(false);
  const [editingMemory, setEditingMemory] = useState<Memory | null>(null);

  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [content, setContent] = useState("");
  const [memoryType, setMemoryType] = useState("preference");
  const [importance, setImportance] = useState("medium");
  const [submitting, setSubmitting] = useState(false);

  const [naturalIntent, setNaturalIntent] = useState("");
  const [processingIntent, setProcessingIntent] = useState(false);
  const [intentMessage, setIntentMessage] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [mList, mStats] = await Promise.all([
        getMemories(selectedCategory, search),
        getMemoryStats().catch(() => null),
      ]);
      setMemories(mList);
      if (mStats) setStats(mStats);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load memory workspace");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleSave = async () => {
    if (!key.trim() || !value.trim()) return;
    setSubmitting(true);
    try {
      if (editingMemory) {
        await updateMemory(editingMemory.id, {
          key: key.trim(),
          value: value.trim(),
          content: content.trim() || undefined,
          memory_type: memoryType,
          importance,
        });
      } else {
        await createMemory({
          key: key.trim(),
          value: value.trim(),
          content: content.trim() || undefined,
          memory_type: memoryType,
          importance,
          source: "explicit_user",
        });
      }
      resetForm();
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save memory");
    } finally {
      setSubmitting(false);
    }
  };

  const handleNaturalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!naturalIntent.trim()) return;
    setProcessingIntent(true);
    setIntentMessage(null);
    try {
      const res = await processExplicitMemory(naturalIntent.trim());
      setIntentMessage(res.message);
      setNaturalIntent("");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process memory command");
    } finally {
      setProcessingIntent(false);
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

  const openEdit = (mem: Memory) => {
    setEditingMemory(mem);
    setKey(mem.key);
    setValue(mem.value);
    setContent(mem.content || "");
    setMemoryType(mem.memory_type || "preference");
    setImportance(mem.importance || "medium");
    setShowForm(true);
  };

  const resetForm = () => {
    setEditingMemory(null);
    setKey("");
    setValue("");
    setContent("");
    setMemoryType("preference");
    setImportance("medium");
    setShowForm(false);
  };

  const filtered = useMemo(() => {
    return memories.filter((m) => {
      const matchesSearch =
        !search ||
        m.key.toLowerCase().includes(search.toLowerCase()) ||
        m.value.toLowerCase().includes(search.toLowerCase()) ||
        (m.content && m.content.toLowerCase().includes(search.toLowerCase()));
      return matchesSearch;
    });
  }, [memories, search]);

  return (
    <AppShell>
      {/* Hero / Natural Command Box */}
      <div className="mb-6">
        <GlassCard className="p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-sky-500/10 via-purple-500/5 to-cyan-500/10 opacity-70 pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-sky-400 text-xs font-semibold uppercase tracking-wider mb-1">
                <BrainCircuit className="h-4 w-4" />
                <span>RajOS Memory 2.0 Engine</span>
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Long-Term Memory Workspace</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Hybrid vector semantic retrieval, explicit user rules, and intelligent conflict deduplication.
              </p>
            </div>

            <form onSubmit={handleNaturalSubmit} className="flex items-center gap-2 w-full md:w-auto">
              <div className="relative flex-1 md:w-80">
                <Sparkles className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-sky-400" />
                <input
                  type="text"
                  placeholder="e.g., Remember that I build with Python..."
                  value={naturalIntent}
                  onChange={(e) => setNaturalIntent(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-white/[0.04] pl-9 pr-4 py-2.5 text-sm text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50 focus:outline-none"
                />
              </div>
              <Button
                type="submit"
                disabled={processingIntent || !naturalIntent.trim()}
                className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
              >
                {processingIntent ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                Teach AI
              </Button>
            </form>
          </div>

          {intentMessage && (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/[0.08] px-4 py-2.5 text-xs text-emerald-300 flex items-center justify-between"
            >
              <span>{intentMessage}</span>
              <button onClick={() => setIntentMessage(null)} className="text-emerald-400 hover:text-emerald-200">
                <X className="h-3.5 w-3.5" />
              </button>
            </motion.div>
          )}
        </GlassCard>
      </div>

      {/* Stats row */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            label: "Total Memories",
            value: stats ? stats.active_memories : memories.length,
            icon: BrainCircuit,
            color: "text-sky-400",
          },
          {
            label: "Explicit User Facts",
            value: stats ? stats.by_source?.explicit_user || 0 : memories.filter((m) => m.source === "explicit_user").length,
            icon: User,
            color: "text-emerald-400",
          },
          {
            label: "AI Inferred Memories",
            value: stats ? stats.by_source?.inferred_llm || 0 : memories.filter((m) => m.source === "inferred_llm").length,
            icon: Bot,
            color: "text-violet-400",
          },
          {
            label: "Vector Store",
            value: "ChromaDB",
            icon: Database,
            color: "text-cyan-400",
          },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.05} className="p-5">
            <div className="flex items-center justify-between">
              <div className={cn("flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]", stat.color)}>
                <stat.icon className="h-5 w-5" />
              </div>
            </div>
            <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-xs text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Filter Tabs & Search Controls */}
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-1 overflow-x-auto pb-1 lg:pb-0 no-scrollbar">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={cn(
                "rounded-xl px-3.5 py-1.5 text-xs font-medium transition-all whitespace-nowrap",
                selectedCategory === cat.id
                  ? "bg-sky-500/20 border border-sky-400/30 text-sky-300"
                  : "bg-white/[0.02] border border-white/[0.06] text-muted-foreground hover:bg-white/[0.05] hover:text-white"
              )}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.02] px-3 py-1.5">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search memory graph..."
              className="w-full bg-transparent text-xs text-white placeholder:text-muted-foreground focus:outline-none lg:w-48"
            />
          </form>
          <Button
            onClick={() => {
              if (showForm) resetForm();
              else setShowForm(true);
            }}
            className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400 text-xs"
          >
            {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            {showForm ? "Cancel" : "Add Memory"}
          </Button>
        </div>
      </div>

      {/* Create / Edit Form */}
      {showForm && (
        <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
          <GlassCard className="p-5 space-y-4 border-sky-500/30">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <BrainCircuit className="h-4 w-4 text-sky-400" />
                {editingMemory ? "Edit Memory Node" : "New Memory Node"}
              </h3>
              <button onClick={resetForm} className="text-muted-foreground hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Memory Key</label>
                <Input
                  placeholder="e.g. Favorite Language"
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                  className="border-white/[0.08] bg-white/[0.02] text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Category Type</label>
                <select
                  value={memoryType}
                  onChange={(e) => setMemoryType(e.target.value)}
                  className="w-full rounded-md border border-white/[0.08] bg-black/60 px-3 py-2 text-xs text-white focus:outline-none"
                >
                  <option value="preference">Preference</option>
                  <option value="goal">Goal</option>
                  <option value="project">Project</option>
                  <option value="instruction">Instruction</option>
                  <option value="fact">Fact</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Memory Value / Statement</label>
              <textarea
                placeholder="e.g. Python & TypeScript"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                rows={2}
                className="w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 py-2 text-xs text-white placeholder:text-muted-foreground/60 focus:outline-none focus:border-sky-400/50 resize-none"
              />
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Detailed Context (Optional)</label>
              <textarea
                placeholder="Additional notes or background..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={2}
                className="w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 py-2 text-xs text-white placeholder:text-muted-foreground/60 focus:outline-none focus:border-sky-400/50 resize-none"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <Button type="button" onClick={resetForm} variant="outline" className="text-xs border-white/10">
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={submitting || !key.trim() || !value.trim()}
                className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white text-xs"
              >
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                {editingMemory ? "Update Memory" : "Save Memory"}
              </Button>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {error && (
        <div className="mb-4 rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Memory Cards Grid */}
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
                transition={{ duration: 0.25, delay: i * 0.03 }}
              >
                <GlassCard className="group h-full p-5 flex flex-col justify-between hover:border-sky-500/40 transition-all">
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-2 overflow-hidden">
                        <Tag className="h-3.5 w-3.5 text-sky-400 shrink-0" />
                        <span className="text-xs font-bold uppercase tracking-wider text-sky-300 truncate">
                          {item.key}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => openEdit(item)}
                          className="rounded-lg p-1 text-muted-foreground hover:bg-white/10 hover:text-white"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="rounded-lg p-1 text-muted-foreground hover:bg-rose-500/10 hover:text-rose-400"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>

                    <p className="mt-3 text-sm font-medium text-white leading-relaxed">{item.value}</p>

                    {item.content && item.content !== item.value && (
                      <p className="mt-2 text-xs text-muted-foreground line-clamp-2">{item.content}</p>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <span className="rounded-full border border-sky-400/20 bg-sky-400/10 px-2 py-0.5 text-[10px] font-semibold text-sky-300 capitalize">
                        {item.memory_type || "preference"}
                      </span>
                      <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[10px] capitalize">
                        {item.source === "inferred_llm" ? "AI Inferred" : "User Explicit"}
                      </span>
                    </div>

                    <span className="text-[10px] opacity-60">Hits: {item.access_count || 0}</span>
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
            {search ? "Try adjusting your search criteria." : "Teach RajOS your preferences and facts above."}
          </p>
        </div>
      )}
    </AppShell>
  );
}
