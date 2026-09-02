"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bell, BellRing, CheckCircle2, Clock, AlertTriangle,
  Smartphone, Loader2, X, ExternalLink, BellOff,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { usePushNotifications } from "@/hooks/usePushNotifications";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

interface Summary {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
  due_today: number;
  push_enabled: boolean;
}

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [sendingTest, setSendingTest] = useState(false);
  const [testMsg, setTestMsg] = useState("");
  const panelRef = useRef<HTMLDivElement>(null);
  const { permission, isSubscribed, loading, subscribe, unsubscribe } = usePushNotifications();

  const urgentCount = (summary?.overdue ?? 0) + (summary?.due_today ?? 0);

  // Load summary on open and every 30s
  const loadSummary = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const res = await fetch(`${API}/notifications/summary`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setSummary(await res.json());
    } catch { /* ignore */ }
  };

  useEffect(() => {
    loadSummary();
    const id = setInterval(loadSummary, 30000);
    return () => clearInterval(id);
  }, []);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const handleTestPush = async () => {
    const token = localStorage.getItem("token");
    setSendingTest(true);
    setTestMsg("");
    try {
      const res = await fetch(`${API}/notifications/send-test`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ title: "🔔 RajOS Test", body: "Push notifications are working!" }),
      });
      const data = await res.json();
      setTestMsg(data.sent > 0 ? "✅ Sent!" : "⚠️ No devices subscribed yet.");
    } catch { setTestMsg("❌ Failed"); }
    finally { setSendingTest(false); }
  };

  return (
    <div className="relative" ref={panelRef}>
      {/* Bell button */}
      <button
        onClick={() => { setOpen((o) => !o); loadSummary(); }}
        className={cn(
          "relative flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] transition-colors hover:bg-white/[0.08]",
          open && "bg-white/[0.08] border-sky-400/30"
        )}
      >
        {urgentCount > 0 ? (
          <BellRing className="h-4 w-4 text-amber-400 animate-[wiggle_1s_ease-in-out_infinite]" />
        ) : (
          <Bell className="h-4 w-4 text-muted-foreground" />
        )}
        {urgentCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[9px] font-bold text-white">
            {urgentCount > 9 ? "9+" : urgentCount}
          </span>
        )}
      </button>

      {/* Dropdown panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ duration: 0.18 }}
            className="absolute right-0 top-full z-50 mt-2 w-80 rounded-2xl border border-white/10 bg-black/90 shadow-2xl backdrop-blur-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-3">
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4 text-sky-400" />
                <span className="text-sm font-semibold text-white">Notifications</span>
              </div>
              <button onClick={() => setOpen(false)} className="text-muted-foreground hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Task summary */}
            <div className="p-4 space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Task Overview</p>
              {summary ? (
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { label: "Total", value: summary.total, icon: CheckCircle2, color: "text-sky-400" },
                    { label: "Completed", value: summary.completed, icon: CheckCircle2, color: "text-emerald-400" },
                    { label: "Pending", value: summary.pending, icon: Clock, color: "text-amber-400" },
                    { label: "Overdue", value: summary.overdue, icon: AlertTriangle, color: "text-rose-400" },
                  ].map((s) => (
                    <div key={s.label} className="flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.03] p-3">
                      <s.icon className={cn("h-4 w-4 shrink-0", s.color)} />
                      <div>
                        <p className="text-lg font-bold text-white leading-none">{s.value}</p>
                        <p className="text-[10px] text-muted-foreground">{s.label}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-sky-400" />
                </div>
              )}

              {summary && summary.due_today > 0 && (
                <div className="rounded-xl border border-amber-400/20 bg-amber-400/[0.08] px-3 py-2 text-xs text-amber-300">
                  ⏰ {summary.due_today} task{summary.due_today > 1 ? "s" : ""} due today
                </div>
              )}

              <a
                href="/tasks"
                className="flex items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-xs text-muted-foreground hover:text-white transition-colors"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                View all tasks
              </a>
            </div>

            {/* Push notification control */}
            <div className="border-t border-white/[0.06] p-4 space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Push Notifications
              </p>
              <div className="flex items-center gap-2">
                <div className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-lg",
                  isSubscribed ? "bg-emerald-500/20 text-emerald-400" : "bg-white/5 text-muted-foreground"
                )}>
                  {isSubscribed ? <Smartphone className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
                </div>
                <div className="flex-1">
                  <p className="text-xs font-medium text-white">
                    {isSubscribed ? "Notifications active" : "Notifications off"}
                  </p>
                  <p className="text-[10px] text-muted-foreground">
                    {isSubscribed ? "Works even when tab is closed" : "Enable to get task alerts"}
                  </p>
                </div>
              </div>

              {permission === "denied" ? (
                <div className="rounded-lg bg-rose-500/10 px-3 py-2 text-xs text-rose-300">
                  Push blocked in browser. Enable in browser settings.
                </div>
              ) : isSubscribed ? (
                <div className="flex gap-2">
                  <button
                    onClick={handleTestPush}
                    disabled={sendingTest}
                    className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] py-2 text-xs text-muted-foreground hover:text-white transition-colors disabled:opacity-50"
                  >
                    {sendingTest ? <Loader2 className="h-3 w-3 animate-spin" /> : "Send Test"}
                  </button>
                  <button
                    onClick={unsubscribe}
                    disabled={loading}
                    className="flex-1 flex items-center justify-center gap-1.5 rounded-lg border border-rose-500/20 bg-rose-500/[0.08] py-2 text-xs text-rose-300 hover:bg-rose-500/[0.15] transition-colors disabled:opacity-50"
                  >
                    Turn Off
                  </button>
                </div>
              ) : (
                <button
                  onClick={subscribe}
                  disabled={loading}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 py-2.5 text-xs font-semibold text-white hover:from-sky-400 hover:to-cyan-400 disabled:opacity-60 transition-all"
                >
                  {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Bell className="h-3.5 w-3.5" />}
                  {loading ? "Enabling..." : "Enable Push Notifications"}
                </button>
              )}
              {testMsg && <p className="text-center text-xs text-muted-foreground">{testMsg}</p>}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
