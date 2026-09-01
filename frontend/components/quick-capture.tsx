"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Loader2, CheckCircle2, Zap, StickyNote, Brain, X } from "lucide-react";
import { cn } from "@/lib/utils";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Mode = "task" | "note" | "memory";

const modes: { id: Mode; label: string; icon: typeof Plus; placeholder: string; color: string }[] = [
  { id: "task", label: "Task", icon: CheckCircle2, placeholder: "Add a task... (e.g. Review PR by Friday)", color: "text-sky-400" },
  { id: "note", label: "Note", icon: StickyNote, placeholder: "Capture a note...", color: "text-amber-400" },
  { id: "memory", label: "Memory", icon: Brain, placeholder: "Save a memory... (format: key: value)", color: "text-violet-400" },
];

export function QuickCapture() {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<Mode>("task");
  const [value, setValue] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const close = useCallback(() => {
    setOpen(false);
    setValue("");
    setStatus("idle");
    setMessage("");
  }, []);

  // Open on Ctrl+K / Cmd+K or custom event
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === "Escape") close();
    };
    const eventHandler = () => setOpen(true);
    document.addEventListener("keydown", handler);
    document.addEventListener("open-quick-capture", eventHandler);
    return () => {
      document.removeEventListener("keydown", handler);
      document.removeEventListener("open-quick-capture", eventHandler);
    };
  }, [close]);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  const handleSubmit = async () => {
    if (!value.trim()) return;
    const token = localStorage.getItem("token");
    setStatus("loading");
    try {
      if (mode === "task") {
        const res = await fetch(`${API}/tasks/`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ title: value.trim() }),
        });
        if (!res.ok) throw new Error("Failed");
        setMessage("✅ Task created!");
      } else if (mode === "note") {
        const res = await fetch(`${API}/notes/`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ title: value.trim().slice(0, 60), content: value.trim() }),
        });
        if (!res.ok) throw new Error("Failed");
        setMessage("📝 Note saved!");
      } else if (mode === "memory") {
        const [k, ...rest] = value.split(":");
        const key = k.trim() || "note";
        const val = rest.join(":").trim() || value.trim();
        const res = await fetch(`${API}/memory/`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ key, value: val }),
        });
        if (!res.ok) throw new Error("Failed");
        setMessage("🧠 Memory saved!");
      }
      setStatus("success");
      setValue("");
      setTimeout(close, 1200);
    } catch {
      setStatus("error");
      setMessage("❌ Failed — check backend connection");
      setTimeout(() => setStatus("idle"), 2000);
    }
  };

  const activeMode = modes.find((m) => m.id === mode)!;

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={close}
          />

          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, y: -24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -24, scale: 0.97 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="fixed left-1/2 top-24 z-50 w-full max-w-lg -translate-x-1/2 overflow-hidden rounded-2xl border border-white/10 bg-black/95 shadow-2xl backdrop-blur-2xl"
          >
            {/* Mode tabs */}
            <div className="flex items-center gap-1 border-b border-white/[0.06] p-2">
              {modes.map((m) => (
                <button
                  key={m.id}
                  onClick={() => setMode(m.id)}
                  className={cn(
                    "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all",
                    mode === m.id
                      ? "bg-white/10 text-white"
                      : "text-muted-foreground hover:text-white hover:bg-white/5"
                  )}
                >
                  <m.icon className={cn("h-3.5 w-3.5", mode === m.id && m.color)} />
                  {m.label}
                </button>
              ))}
              <button onClick={close} className="ml-auto text-muted-foreground hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Input */}
            <div className="p-4">
              <div className="flex items-center gap-3">
                <activeMode.icon className={cn("h-5 w-5 shrink-0", activeMode.color)} />
                <input
                  ref={inputRef}
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit();
                    }
                  }}
                  placeholder={activeMode.placeholder}
                  className="flex-1 bg-transparent text-sm text-white placeholder:text-muted-foreground focus:outline-none"
                />
                <button
                  onClick={handleSubmit}
                  disabled={!value.trim() || status === "loading"}
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-sky-500 to-cyan-500 text-white disabled:opacity-40 hover:from-sky-400 hover:to-cyan-400 transition-all"
                >
                  {status === "loading" ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                </button>
              </div>

              {/* Status message */}
              <AnimatePresence>
                {message && (
                  <motion.p
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="mt-3 text-xs text-muted-foreground text-center"
                  >
                    {message}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>

            {/* Footer hint */}
            <div className="flex items-center justify-between border-t border-white/[0.06] px-4 py-2">
              <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                <Zap className="h-3 w-3 text-sky-400" />
                Quick Capture
              </div>
              <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                <kbd className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 font-mono">Enter</kbd>
                to save ·
                <kbd className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 font-mono">Esc</kbd>
                to close
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
