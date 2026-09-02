"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  BrainCircuit,
  BookOpen,
  BarChart3,
  Settings,
  CheckSquare,
  StickyNote,
  FileText,
  Workflow,
  User,
  ChevronLeft,
  Sparkles,
  Zap,
  Radio,
  Cpu,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { navSections } from "@/lib/data";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard,
  MessageSquare,
  Bot,
  BrainCircuit,
  BookOpen,
  BarChart3,
  Settings,
  CheckSquare,
  StickyNote,
  FileText,
  Workflow,
  User,
};

export function Sidebar({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  const pathname = usePathname();

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 80 : 272 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="sticky top-0 z-30 flex h-screen shrink-0 flex-col border-r border-white/[0.08] bg-black/60 backdrop-blur-3xl shadow-[4px_0_24px_-4px_rgba(0,0,0,0.5)]"
      style={{ perspective: "1000px" }}
    >
      {/* 3D Vertical accent light line */}
      <div className="pointer-events-none absolute inset-y-0 right-0 w-[1px] bg-gradient-to-b from-sky-400/40 via-cyan-400/15 to-transparent" />

      {/* ── Logo & Brand ── */}
      <div className="flex h-16 items-center justify-between px-5 border-b border-white/[0.05]">
        <Link href="/" className="flex items-center gap-3 overflow-hidden group">
          {/* Holographic 3D Logo Cube */}
          <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 via-cyan-500 to-blue-600 shadow-lg shadow-sky-500/30 transition-transform duration-300 group-hover:scale-105 group-hover:rotate-3">
            <Sparkles className="h-5 w-5 text-white animate-pulse" />
            {/* Glowing orbital halo */}
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-sky-400 to-cyan-400 blur-md opacity-50 -z-10 group-hover:opacity-80 transition-opacity" />
            <div className="absolute -inset-0.5 rounded-xl border border-white/40 opacity-70" />
          </div>

          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="flex flex-col leading-none"
              >
                <div className="flex items-center gap-1.5">
                  <span className="text-[16px] font-bold tracking-tight bg-gradient-to-r from-white via-white/95 to-white/70 bg-clip-text text-transparent">
                    RajOS
                  </span>
                  <span className="rounded-full bg-sky-500/20 border border-sky-400/30 px-1.5 py-0.2 text-[9px] font-semibold text-sky-300">
                    3D
                  </span>
                </div>
                <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-sky-400/70 mt-1">
                  AI Operating System
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </Link>

        {/* Collapse toggle button */}
        <button
          onClick={onToggle}
          className={cn(
            "flex h-7 w-7 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] text-muted-foreground transition-all duration-200 hover:border-sky-400/40 hover:bg-sky-400/10 hover:text-white",
            collapsed && "mx-auto"
          )}
          aria-label="Toggle sidebar"
        >
          <ChevronLeft
            className={cn(
              "h-4 w-4 transition-transform duration-300",
              collapsed && "rotate-180 text-sky-400"
            )}
          />
        </button>
      </div>

      {/* ── Navigation Sections ── */}
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-3 py-3 no-scrollbar">
        {navSections.map((section) => (
          <div key={section.heading} className="flex flex-col gap-1">
            <AnimatePresence>
              {!collapsed && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="px-3 pb-1.5 pt-3.5 text-[10px] font-bold uppercase tracking-[0.2em] text-muted-foreground/60"
                >
                  {section.heading}
                </motion.p>
              )}
            </AnimatePresence>

            {collapsed && (
              <div className="mx-3 my-1 h-px bg-white/[0.08] first:hidden" />
            )}

            {section.items.map((item) => {
              const Icon = iconMap[item.icon] ?? LayoutDashboard;
              const active =
                pathname === item.href || pathname.startsWith(item.href + "/");

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                    active
                      ? "text-white shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1)]"
                      : "text-muted-foreground hover:text-white hover:bg-white/[0.04]"
                  )}
                >
                  {/* Active 3D highlight pill */}
                  {active && (
                    <motion.div
                      layoutId="sidebar-active-pill"
                      className="absolute inset-0 rounded-xl border border-sky-400/30 bg-gradient-to-r from-sky-500/20 via-cyan-500/10 to-transparent shadow-[0_0_16px_rgba(56,189,248,0.2)]"
                      transition={{ type: "spring", stiffness: 450, damping: 35 }}
                    />
                  )}

                  {/* Active left indicator glow bar */}
                  {active && (
                    <motion.div
                      layoutId="sidebar-indicator-bar"
                      className="absolute left-0 top-1/2 h-6 w-[3.5px] -translate-y-1/2 rounded-full bg-gradient-to-b from-sky-400 to-cyan-400 shadow-[0_0_8px_rgba(56,189,248,0.8)]"
                    />
                  )}

                  {/* Icon container with 3D depth */}
                  <div
                    className={cn(
                      "relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition-all duration-200",
                      active
                        ? "border-sky-400/40 bg-sky-400/15 text-sky-400 shadow-[0_0_12px_rgba(56,189,248,0.3)]"
                        : "border-white/[0.06] bg-white/[0.02] text-muted-foreground group-hover:border-white/15 group-hover:bg-white/[0.06] group-hover:text-white"
                    )}
                  >
                    <Icon className="h-4 w-4 transition-transform duration-200 group-hover:scale-110" />
                  </div>

                  {/* Label */}
                  <AnimatePresence>
                    {!collapsed && (
                      <motion.span
                        initial={{ opacity: 0, x: -6 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -6 }}
                        className="relative truncate font-medium text-[13.5px]"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>

                  {/* Active trailing accent dot */}
                  {active && !collapsed && (
                    <div className="ml-auto h-1.5 w-1.5 rounded-full bg-sky-400 shadow-[0_0_6px_#38bdf8]" />
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* ── 3D System Online Telemetry ── */}
      <div className="border-t border-white/[0.06] p-3">
        <div
          className={cn(
            "relative overflow-hidden rounded-xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent p-3 backdrop-blur-md",
            collapsed && "flex justify-center p-2"
          )}
        >
          {/* Subtle status glow corner */}
          <div className="pointer-events-none absolute -right-6 -bottom-6 h-16 w-16 rounded-full bg-emerald-500/15 blur-xl" />

          <div className="flex items-center gap-3">
            {/* Pulsing 3D Radio Orb */}
            <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-500/10">
              <Radio className="h-4 w-4 text-emerald-400 animate-pulse" />
              <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-emerald-400 ring-2 ring-black">
                <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-75" />
              </span>
            </div>

            <AnimatePresence>
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col leading-tight min-w-0"
                >
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-semibold text-white">
                      Core Online
                    </span>
                    <span className="rounded bg-emerald-500/20 px-1 py-0.2 text-[9px] font-mono text-emerald-300">
                      v2.0
                    </span>
                  </div>
                  <span className="text-[10px] text-muted-foreground truncate">
                    5 Agents · Gemini 3.1
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.aside>
  );
}

export function useSidebarState() {
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => {
    const stored = localStorage.getItem("rajos-sidebar-collapsed");
    if (stored === "true") setCollapsed(true);
  }, []);
  useEffect(() => {
    localStorage.setItem("rajos-sidebar-collapsed", String(collapsed));
  }, [collapsed]);
  return [collapsed, setCollapsed] as const;
}
