"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  X,
  Volume2,
  VolumeX,
  Timer as TimerIcon,
  Flame,
  BookOpen,
  Minimize2,
  Maximize2,
  Sparkles,
  Dumbbell,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Task } from "@/services/api/tasks";

interface TaskTimerModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onCompleteTask: (taskId: number) => void;
}

export function TaskTimerModal({
  task,
  isOpen,
  onClose,
  onCompleteTask,
}: TaskTimerModalProps) {
  // Mode: "countdown" (Pomodoro / Study) or "stopwatch" (Pushups / Workout count-up)
  const isWorkout = task?.title?.toLowerCase().includes("pushup") || task?.title?.toLowerCase().includes("workout");
  const [mode, setMode] = useState<"countdown" | "stopwatch">(isWorkout ? "stopwatch" : "countdown");

  // Timer settings
  const [targetSeconds, setTargetSeconds] = useState<number>(25 * 60); // default 25 mins
  const [secondsRemaining, setSecondsRemaining] = useState<number>(25 * 60);
  const [stopwatchSeconds, setStopwatchSeconds] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [isMinimized, setIsMinimized] = useState<boolean>(false);

  // Pushup workout set tracker
  const [setsCompleted, setSetsCompleted] = useState<number[]>([]);

  // Update mode when task changes
  useEffect(() => {
    if (task) {
      const workout = task.title.toLowerCase().includes("pushup") || task.title.toLowerCase().includes("workout");
      setMode(workout ? "stopwatch" : "countdown");
      setIsRunning(false);
      setStopwatchSeconds(0);
      setSecondsRemaining(25 * 60);
      setSetsCompleted([]);
    }
  }, [task]);

  // Audio chime using Web Audio API oscillator
  const playChime = useCallback(() => {
    if (!soundEnabled || typeof window === "undefined") return;
    try {
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3); // A5

      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 1.2);
    } catch {
      // Audio autoplay restrictions
    }
  }, [soundEnabled]);

  // Timer interval loop
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      if (mode === "countdown") {
        setSecondsRemaining((prev) => {
          if (prev <= 1) {
            setIsRunning(false);
            playChime();
            return 0;
          }
          return prev - 1;
        });
      } else {
        setStopwatchSeconds((prev) => prev + 1);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, mode, playChime]);

  // Preset picker
  const setPreset = (mins: number) => {
    setIsRunning(false);
    setTargetSeconds(mins * 60);
    setSecondsRemaining(mins * 60);
  };

  const handleToggleRunning = () => {
    setIsRunning((prev) => !prev);
  };

  const handleReset = () => {
    setIsRunning(false);
    if (mode === "countdown") {
      setSecondsRemaining(targetSeconds);
    } else {
      setStopwatchSeconds(0);
      setSetsCompleted([]);
    }
  };

  const handleComplete = () => {
    if (!task) return;
    setIsRunning(false);
    playChime();
    onCompleteTask(task.id);
    onClose();
  };

  const formatTime = (totalSecs: number) => {
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Circular progress calculation
  const progress =
    mode === "countdown"
      ? targetSeconds > 0
        ? (targetSeconds - secondsRemaining) / targetSeconds
        : 0
      : (stopwatchSeconds % 60) / 60;

  if (!isOpen || !task) return null;

  // ── Floating Minimized HUD Mode ──
  if (isMinimized) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.85, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.85, y: 20 }}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border border-sky-400/40 bg-black/90 p-3.5 backdrop-blur-2xl shadow-[0_12px_36px_rgba(0,0,0,0.8),0_0_20px_rgba(56,189,248,0.25)]"
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/20 text-sky-400">
          {mode === "stopwatch" ? <Dumbbell className="h-4 w-4" /> : <TimerIcon className="h-4 w-4" />}
        </div>
        <div>
          <div className="text-[11px] text-muted-foreground truncate max-w-[140px] font-medium">
            {task.title}
          </div>
          <div className="font-mono text-base font-bold text-white tracking-wider">
            {mode === "countdown" ? formatTime(secondsRemaining) : formatTime(stopwatchSeconds)}
          </div>
        </div>

        <div className="flex items-center gap-1.5 ml-2">
          <button
            onClick={handleToggleRunning}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            {isRunning ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5 ml-0.5" />}
          </button>
          <button
            onClick={() => setIsMinimized(false)}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
            title="Expand"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </motion.div>
    );
  }

  // ── Full 3D Modal Window ──
  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 backdrop-blur-xl"
        />

        {/* Modal Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.92, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.92, y: 20 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 w-full max-w-lg overflow-hidden rounded-3xl border border-white/15 bg-black/90 p-6 sm:p-8 backdrop-blur-3xl shadow-[0_24px_60px_rgba(0,0,0,0.9),0_0_40px_rgba(56,189,248,0.2)] text-center"
        >
          {/* Top specular beam */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400 to-transparent" />

          {/* Top Controls: Sound, Minimize, Close */}
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="flex h-8 w-8 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-white transition-colors"
              title={soundEnabled ? "Mute audio" : "Enable audio"}
            >
              {soundEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4 text-rose-400" />}
            </button>

            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setIsMinimized(true)}
                className="flex h-8 w-8 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-white transition-colors"
                title="Minimize timer"
              >
                <Minimize2 className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={onClose}
                className="flex h-8 w-8 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-white transition-colors"
                title="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Task Header */}
          <div className="mb-5">
            <div className="inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-400/10 px-3 py-1 text-xs font-semibold text-sky-300 mb-2">
              <Sparkles className="h-3.5 w-3.5" />
              Active Objective Focus Session
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-white leading-tight px-4">
              {task.title}
            </h2>
            {task.description && (
              <p className="mt-1 text-xs text-muted-foreground line-clamp-1 max-w-sm mx-auto">
                {task.description}
              </p>
            )}
          </div>

          {/* Mode Switcher: Countdown (Study) vs Stopwatch (Workout) */}
          <div className="mx-auto mb-6 flex max-w-xs rounded-xl border border-white/10 bg-white/5 p-1">
            <button
              onClick={() => {
                setMode("countdown");
                setIsRunning(false);
              }}
              className={cn(
                "flex-1 rounded-lg py-1.5 text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5",
                mode === "countdown"
                  ? "bg-gradient-to-r from-sky-500 to-cyan-400 text-white shadow-md"
                  : "text-muted-foreground hover:text-white"
              )}
            >
              <BookOpen className="h-3.5 w-3.5" />
              Study Pomodoro
            </button>
            <button
              onClick={() => {
                setMode("stopwatch");
                setIsRunning(false);
              }}
              className={cn(
                "flex-1 rounded-lg py-1.5 text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5",
                mode === "stopwatch"
                  ? "bg-gradient-to-r from-sky-500 to-cyan-400 text-white shadow-md"
                  : "text-muted-foreground hover:text-white"
              )}
            >
              <Dumbbell className="h-3.5 w-3.5" />
              Pushup Workout
            </button>
          </div>

          {/* Circular SVG Timer Display */}
          <div className="relative mx-auto mb-6 flex h-52 w-52 items-center justify-center">
            {/* SVG Progress Ring */}
            <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="44"
                className="stroke-white/[0.08]"
                strokeWidth="5"
                fill="transparent"
              />
              <circle
                cx="50"
                cy="50"
                r="44"
                className="stroke-sky-400 transition-all duration-500"
                strokeWidth="5"
                strokeDasharray={276.46}
                strokeDashoffset={276.46 * (1 - progress)}
                strokeLinecap="round"
                fill="transparent"
                style={{ filter: "drop-shadow(0 0 8px rgba(56, 189, 248, 0.6))" }}
              />
            </svg>

            {/* Central Digits */}
            <div className="absolute flex flex-col items-center">
              <div className="font-mono text-4xl sm:text-5xl font-extrabold tracking-tight text-white">
                {mode === "countdown" ? formatTime(secondsRemaining) : formatTime(stopwatchSeconds)}
              </div>
              <div className="mt-1 text-[11px] font-semibold uppercase tracking-wider text-sky-400">
                {isRunning ? (mode === "countdown" ? "Focusing..." : "Reps Ticking") : "Paused"}
              </div>
            </div>
          </div>

          {/* Countdown Preset Buttons */}
          {mode === "countdown" && (
            <div className="mb-6 flex justify-center gap-2">
              {[
                { label: "5m", mins: 5 },
                { label: "15m", mins: 15 },
                { label: "25m", mins: 25 },
                { label: "50m", mins: 50 },
              ].map((p) => (
                <button
                  key={p.label}
                  onClick={() => setPreset(p.mins)}
                  className={cn(
                    "rounded-xl border px-3 py-1 text-xs font-semibold transition-all duration-200",
                    targetSeconds === p.mins * 60
                      ? "border-sky-400 bg-sky-400/20 text-sky-300"
                      : "border-white/10 bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-white"
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          )}

          {/* Workout Pushup Set Tracker */}
          {mode === "stopwatch" && (
            <div className="mb-6 rounded-2xl border border-white/[0.08] bg-white/[0.02] p-3 text-xs">
              <div className="text-muted-foreground font-semibold mb-2">Pushup Sets Completed</div>
              <div className="flex justify-center gap-3">
                {[
                  { set: 1, reps: "20 Reps" },
                  { set: 2, reps: "15 Reps" },
                  { set: 3, reps: "15 Reps" },
                ].map((item) => {
                  const done = setsCompleted.includes(item.set);
                  return (
                    <button
                      key={item.set}
                      onClick={() =>
                        setSetsCompleted((prev) =>
                          prev.includes(item.set) ? prev.filter((s) => s !== item.set) : [...prev, item.set]
                        )
                      }
                      className={cn(
                        "flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all",
                        done
                          ? "border-emerald-500 bg-emerald-500/20 text-emerald-300 shadow-[0_0_12px_rgba(52,211,153,0.3)]"
                          : "border-white/10 bg-white/5 text-muted-foreground hover:text-white"
                      )}
                    >
                      <CheckCircle2 className={cn("h-3.5 w-3.5", done && "text-emerald-400")} />
                      Set {item.set} ({item.reps})
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Primary Action Buttons */}
          <div className="flex items-center justify-center gap-3">
            <Button
              variant="outline"
              size="lg"
              onClick={handleReset}
              className="h-12 w-12 rounded-2xl border-white/10 p-0 text-muted-foreground hover:bg-white/10 hover:text-white"
              title="Reset timer"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>

            <Button
              size="lg"
              onClick={handleToggleRunning}
              className={cn(
                "h-12 flex-1 max-w-[180px] gap-2 rounded-2xl font-bold text-sm shadow-xl transition-all duration-200",
                isRunning
                  ? "border border-amber-400/40 bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 shadow-amber-500/20"
                  : "bg-gradient-to-r from-sky-500 to-cyan-400 text-white hover:from-sky-400 hover:to-cyan-300 shadow-sky-500/30"
              )}
            >
              {isRunning ? (
                <>
                  <Pause className="h-4 w-4" /> Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 ml-0.5" /> Start Timer
                </>
              )}
            </Button>

            <Button
              size="lg"
              onClick={handleComplete}
              className="h-12 gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 px-5 text-sm font-bold text-white shadow-xl shadow-emerald-500/25 hover:from-emerald-400 hover:to-teal-400 transition-all"
            >
              <CheckCircle2 className="h-4 w-4" />
              Done
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
