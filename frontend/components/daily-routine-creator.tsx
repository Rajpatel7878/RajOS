"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dumbbell,
  BookOpen,
  Sparkles,
  Check,
  Plus,
  Flame,
  Clock,
  CheckCircle2,
  Calendar,
  Layers,
  X,
  Target,
  Bell,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { createTask, type TaskCreate } from "@/services/api/tasks";
import { cn } from "@/lib/utils";

interface RoutinePreset {
  id: string;
  category: "fitness" | "study" | "habits";
  title: string;
  description: string;
  priority: "high" | "normal" | "low";
  icon: typeof Dumbbell;
  color: string;
}

const routinePresets: RoutinePreset[] = [
  // Fitness / Pushups
  {
    id: "pushups-50",
    category: "fitness",
    title: "Daily 50 Pushups (3 Sets: 20-15-15)",
    description: "Build upper body strength. Strict form, full chest touch, 60s rest between sets.",
    priority: "high",
    icon: Dumbbell,
    color: "text-amber-400 bg-amber-500/10 border-amber-500/30",
  },
  {
    id: "pushups-100",
    category: "fitness",
    title: "Century Pushup Challenge: 100 Reps",
    description: "4 sets of 25 spread across the day (morning, noon, evening, night).",
    priority: "high",
    icon: Flame,
    color: "text-rose-400 bg-rose-500/10 border-rose-500/30",
  },
  {
    id: "core-stretch",
    category: "fitness",
    title: "Post-Workout Stretch & Core (15 mins)",
    description: "Planks, hamstring stretches, and shoulder mobility to prevent stiffness.",
    priority: "normal",
    icon: Target,
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  },

  // Study & Deep Work
  {
    id: "study-pomodoro",
    category: "study",
    title: "Deep Work Study Block (2 Hours)",
    description: "Two 50-minute focused study sessions with a 10-minute break. No social media.",
    priority: "high",
    icon: BookOpen,
    color: "text-sky-400 bg-sky-500/10 border-sky-500/30",
  },
  {
    id: "study-revision",
    category: "study",
    title: "Active Recall & Revision (30 mins)",
    description: "Review today's study material by quizzing yourself and writing key points.",
    priority: "normal",
    icon: Clock,
    color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
  },
  {
    id: "code-practice",
    category: "study",
    title: "Coding / Problem Solving Session (1 Hour)",
    description: "Solve 2 algorithm problems or build 1 modular feature.",
    priority: "high",
    icon: Sparkles,
    color: "text-violet-400 bg-violet-500/10 border-violet-500/30",
  },

  // Daily Habits
  {
    id: "morning-hydra",
    category: "habits",
    title: "Morning Routine: 500ml Water & Task Planning",
    description: "Hydrate immediately after waking up and set your top 3 objectives for the day.",
    priority: "normal",
    icon: Calendar,
    color: "text-teal-400 bg-teal-500/10 border-teal-500/30",
  },
  {
    id: "evening-review",
    category: "habits",
    title: "Night Routine: Log Pushups, Study & Tasks",
    description: "Reflect on today's discipline, review completed habits, and plan tomorrow.",
    priority: "normal",
    icon: CheckCircle2,
    color: "text-blue-400 bg-blue-500/10 border-blue-500/30",
  },
];

export function DailyRoutineCreator({
  isOpen,
  onClose,
  onTasksCreated,
}: {
  isOpen: boolean;
  onClose: () => void;
  onTasksCreated?: () => void;
}) {
  const [activeCategory, setActiveCategory] = useState<"all" | "fitness" | "study" | "habits">("all");
  const [selectedIds, setSelectedIds] = useState<string[]>(["pushups-50", "study-pomodoro"]);
  const [loading, setLoading] = useState(false);
  const [successCount, setSuccessCount] = useState<number | null>(null);

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const filteredPresets = routinePresets.filter(
    (p) => activeCategory === "all" || p.category === activeCategory
  );

  const handleApplyRoutines = async () => {
    if (selectedIds.length === 0) return;
    setLoading(true);

    try {
      const today = new Date().toISOString().split("T")[0];
      const tasksToCreate = routinePresets.filter((p) => selectedIds.includes(p.id));

      for (const preset of tasksToCreate) {
        await createTask({
          title: preset.title,
          description: preset.description,
          priority: preset.priority,
          due_date: today,
        });
      }

      setSuccessCount(tasksToCreate.length);
      setTimeout(() => {
        setSuccessCount(null);
        onClose();
        if (onTasksCreated) onTasksCreated();
      }, 1000);
    } catch (err) {
      console.error("Failed to batch create routine tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/75 backdrop-blur-xl"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.94, y: 16 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 w-full max-w-2xl overflow-hidden rounded-3xl border border-white/15 bg-black/85 p-6 sm:p-8 backdrop-blur-3xl shadow-[0_24px_60px_rgba(0,0,0,0.9),0_0_40px_rgba(56,189,248,0.15)]"
        >
          {/* Top specular beam */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400 to-transparent" />

          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute right-5 top-5 flex h-8 w-8 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>

          {/* Header */}
          <div className="mb-6">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-400/10 px-3 py-1 text-xs font-semibold text-sky-300">
              <Sparkles className="h-3.5 w-3.5" />
              Daily Habit & Protocol Generator
            </div>
            <h2 className="text-2xl font-extrabold tracking-tight text-white">
              Daily Task Creator: <span className="text-gradient-cyan">Workout & Study</span>
            </h2>
            <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
              Select routine habits to automatically schedule for today with mobile notification alerts.
            </p>
          </div>

          {/* Category Tabs */}
          <div className="mb-6 flex gap-2 overflow-x-auto pb-1">
            {[
              { id: "all", label: "All Routines", count: routinePresets.length },
              { id: "fitness", label: "🏋️ Pushups & Workout", count: 3 },
              { id: "study", label: "📚 Focused Study", count: 3 },
              { id: "habits", label: "🎯 Daily Habits", count: 2 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveCategory(tab.id as any)}
                className={cn(
                  "rounded-xl px-3.5 py-1.5 text-xs font-semibold whitespace-nowrap transition-all duration-200 border",
                  activeCategory === tab.id
                    ? "border-sky-400/50 bg-sky-400/15 text-white shadow-[0_0_12px_rgba(56,189,248,0.25)]"
                    : "border-white/[0.08] bg-white/[0.03] text-muted-foreground hover:bg-white/[0.06] hover:text-white"
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Routine Presets Grid */}
          <div className="grid gap-3 sm:grid-cols-2 max-h-[340px] overflow-y-auto pr-1">
            {filteredPresets.map((preset) => {
              const isSelected = selectedIds.includes(preset.id);
              const Icon = preset.icon;

              return (
                <div
                  key={preset.id}
                  onClick={() => toggleSelect(preset.id)}
                  className={cn(
                    "cursor-pointer rounded-2xl border p-4 transition-all duration-200 relative group",
                    isSelected
                      ? "border-sky-400/60 bg-sky-500/[0.08] shadow-[0_0_20px_rgba(56,189,248,0.12)]"
                      : "border-white/[0.08] bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <div className={cn("flex h-9 w-9 items-center justify-center rounded-xl border", preset.color)}>
                        <Icon className="h-4.5 w-4.5" />
                      </div>
                      <div className="font-bold text-xs sm:text-sm text-white leading-tight">
                        {preset.title}
                      </div>
                    </div>

                    <div
                      className={cn(
                        "flex h-5 w-5 shrink-0 items-center justify-center rounded-lg border transition-colors",
                        isSelected
                          ? "border-sky-400 bg-sky-400 text-black shadow-[0_0_8px_#38bdf8]"
                          : "border-white/20 bg-black/40"
                      )}
                    >
                      {isSelected && <Check className="h-3 w-3 stroke-[3]" />}
                    </div>
                  </div>

                  <p className="mt-2.5 text-[11px] text-muted-foreground leading-relaxed line-clamp-2">
                    {preset.description}
                  </p>

                  <div className="mt-3 flex items-center gap-2">
                    <span className="rounded-md bg-white/5 border border-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wider text-sky-300 font-semibold">
                      {preset.priority}
                    </span>
                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                      <Bell className="h-2.5 w-2.5 text-emerald-400" /> Phone alert
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Action Footer */}
          <div className="mt-6 flex items-center justify-between border-t border-white/[0.08] pt-4">
            <div className="text-xs text-muted-foreground">
              <span className="font-bold text-white">{selectedIds.length}</span> routine(s) selected
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={onClose}
                className="rounded-xl border-white/10 text-xs text-muted-foreground hover:bg-white/5 hover:text-white"
              >
                Cancel
              </Button>

              <Button
                size="sm"
                disabled={loading || selectedIds.length === 0}
                onClick={handleApplyRoutines}
                className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 px-5 text-xs font-semibold text-white shadow-lg shadow-sky-500/25 hover:from-sky-400 hover:to-cyan-400 disabled:opacity-50"
              >
                {successCount ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                    {successCount} Routines Added!
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4" />
                    Activate Selected Routines
                  </>
                )}
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
