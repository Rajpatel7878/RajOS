"use client";

import { usePathname, useRouter } from "next/navigation";
import { Search, Command, Plus, Sparkles, ChevronRight } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { NotificationBell } from "@/components/notification-bell";
import { QuickCapture } from "@/components/quick-capture";

const pageTitles: Record<string, { title: string; subtitle: string; segment: string }> = {
  "/dashboard": { title: "Command Center", subtitle: "Your AI operating system at a glance", segment: "Dashboard" },
  "/chat":      { title: "AI Chat",         subtitle: "Converse with your intelligent agents",   segment: "Chat" },
  "/agents":    { title: "Agent Center",    subtitle: "Manage and monitor your AI workforce",     segment: "Agents" },
  "/memory":    { title: "Memory Engine",   subtitle: "Long-term intelligence and recall",        segment: "Memory" },
  "/knowledge": { title: "Knowledge Center",subtitle: "RAG-powered document intelligence",        segment: "Knowledge" },
  "/analytics": { title: "Analytics",       subtitle: "AI intelligence insights and metrics",     segment: "Analytics" },
  "/tasks":     { title: "Tasks",           subtitle: "Manage your todo list",                    segment: "Tasks" },
  "/notes":     { title: "Notes",           subtitle: "Capture ideas and thoughts",               segment: "Notes" },
  "/settings":  { title: "Settings",        subtitle: "Configure your AI operating system",       segment: "Settings" },
};

export function Topbar() {
  const pathname = usePathname();
  const router   = useRouter();
  const meta = pageTitles[pathname] ?? { title: "RajOS", subtitle: "", segment: "Home" };

  return (
    <>
      <header
        className={[
          "sticky top-0 z-20 flex h-16 items-center justify-between gap-4 px-6",
          "bg-gradient-to-r from-black/60 via-black/40 to-black/60",
          "backdrop-blur-3xl",
          "border-b border-white/[0.06]",
          "shadow-[0_1px_0_0_rgba(56,189,248,0.08)]",
        ].join(" ")}
      >
        {/* ── Left: title + breadcrumb ── */}
        <div className="flex flex-col gap-0.5 min-w-0">
          {/* Breadcrumb */}
          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/50 font-medium tracking-wide uppercase">
            <span>RajOS</span>
            <ChevronRight className="h-2.5 w-2.5 opacity-40" />
            <span className="text-sky-400/70">{meta.segment}</span>
          </div>

          {/* Title with glow */}
          <div className="relative flex items-center gap-2">
            {/* Subtle glow blob behind title */}
            <span
              aria-hidden
              className="pointer-events-none absolute -left-2 -top-1 h-7 w-32 rounded-full bg-sky-500/10 blur-xl"
            />
            <h1 className="relative text-[15px] font-semibold tracking-tight bg-gradient-to-r from-white via-white/90 to-white/60 bg-clip-text text-transparent">
              {meta.title}
            </h1>
          </div>
        </div>

        {/* ── Right section ── */}
        <div className="flex items-center gap-2.5">

          {/* Search pill */}
          <button
            onClick={() => document.dispatchEvent(new CustomEvent("open-quick-capture"))}
            className={[
              "group hidden md:flex items-center gap-2.5 px-3.5 py-2 rounded-xl",
              "border border-white/[0.08] bg-white/[0.03] text-sm text-muted-foreground",
              "transition-all duration-200",
              "hover:border-sky-400/40 hover:bg-sky-400/[0.05] hover:text-white",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500/60",
              "shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]",
            ].join(" ")}
          >
            <Search className="h-3.5 w-3.5 text-muted-foreground/60 group-hover:text-sky-400 transition-colors" />
            <span className="text-[13px]">Quick capture...</span>
            <kbd className="ml-3 flex items-center gap-0.5 rounded-md border border-white/[0.08] bg-white/[0.04] px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground/60">
              <Command className="h-2.5 w-2.5" />K
            </kbd>
          </button>

          {/* Thin separator */}
          <div className="hidden sm:block h-5 w-px bg-white/[0.08]" />

          {/* "New" button with shimmer gradient */}
          <Button
            size="sm"
            onClick={() => document.dispatchEvent(new CustomEvent("open-quick-capture"))}
            className={[
              "relative hidden sm:flex items-center gap-1.5 overflow-hidden",
              "rounded-xl px-3.5 py-2 text-[13px] font-medium text-white",
              "bg-gradient-to-r from-sky-500 via-cyan-400 to-sky-500",
              "bg-[length:200%_100%] animate-[shimmer_3s_linear_infinite]",
              "shadow-[0_0_16px_rgba(56,189,248,0.35)] hover:shadow-[0_0_24px_rgba(56,189,248,0.5)]",
              "transition-all duration-200",
            ].join(" ")}
          >
            {/* Shimmer overlay */}
            <span
              aria-hidden
              className="pointer-events-none absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full animate-[shimmer_3s_linear_infinite]"
            />
            <Plus className="h-4 w-4" />
            New
          </Button>

          {/* Thin separator */}
          <div className="hidden sm:block h-5 w-px bg-white/[0.08]" />

          {/* Notification bell */}
          <NotificationBell />

          {/* Pro badge */}
          <Badge
            variant="outline"
            className="hidden lg:flex items-center gap-1 border-sky-400/30 bg-sky-400/10 text-sky-300 text-[11px]"
          >
            <Sparkles className="h-3 w-3" />
            Pro
          </Badge>

          {/* Thin separator */}
          <div className="hidden lg:block h-5 w-px bg-white/[0.08]" />

          {/* Avatar with gradient ring + online dot */}
          <div className="relative flex items-center justify-center">
            {/* Gradient ring */}
            <span
              aria-hidden
              className="absolute inset-0 rounded-full bg-gradient-to-br from-sky-400 via-cyan-400 to-blue-500 p-[1.5px] opacity-80"
            />
            <Avatar className="relative h-9 w-9 border-2 border-black/80">
              <AvatarFallback className="bg-gradient-to-br from-sky-500 to-cyan-500 text-xs font-bold text-white">
                RJ
              </AvatarFallback>
            </Avatar>
            {/* Online indicator */}
            <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ring-black shadow-[0_0_6px_rgba(52,211,153,0.7)]" />
          </div>

        </div>
      </header>

      {/* Global quick capture overlay (Ctrl+K) */}
      <QuickCapture />
    </>
  );
}
