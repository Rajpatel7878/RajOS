"use client";

import { usePathname, useRouter } from "next/navigation";
import { Search, Command, Plus, Sparkles } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { NotificationBell } from "@/components/notification-bell";
import { QuickCapture } from "@/components/quick-capture";

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": { title: "Command Center", subtitle: "Your AI operating system at a glance" },
  "/chat": { title: "AI Chat", subtitle: "Converse with your intelligent agents" },
  "/agents": { title: "Agent Center", subtitle: "Manage and monitor your AI workforce" },
  "/memory": { title: "Memory Engine", subtitle: "Long-term intelligence and recall" },
  "/knowledge": { title: "Knowledge Center", subtitle: "RAG-powered document intelligence" },
  "/analytics": { title: "Analytics", subtitle: "AI intelligence insights and metrics" },
  "/tasks": { title: "Tasks", subtitle: "Manage your todo list" },
  "/notes": { title: "Notes", subtitle: "Capture ideas and thoughts" },
  "/settings": { title: "Settings", subtitle: "Configure your AI operating system" },
};

export function Topbar() {
  const pathname = usePathname();
  const router = useRouter();
  const meta = pageTitles[pathname] ?? { title: "RajOS", subtitle: "" };

  return (
    <>
      <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-white/[0.06] bg-black/30 px-6 backdrop-blur-2xl">
        <div className="flex flex-col">
          <h1 className="text-[15px] font-semibold tracking-tight text-white">{meta.title}</h1>
          <p className="text-xs text-muted-foreground">{meta.subtitle}</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Search — opens quick capture */}
          <button
            onClick={() => document.dispatchEvent(new CustomEvent("open-quick-capture"))}
            className="hidden items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-muted-foreground transition-colors hover:border-white/20 hover:bg-white/[0.05] md:flex"
          >
            <Search className="h-4 w-4" />
            <span>Quick capture...</span>
            <kbd className="ml-4 flex items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
              <Command className="h-2.5 w-2.5" />K
            </kbd>
          </button>

          {/* Quick add task */}
          <Button
            size="sm"
            onClick={() => document.dispatchEvent(new CustomEvent("open-quick-capture"))}
            className="hidden gap-2 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 text-white shadow-lg shadow-sky-500/20 hover:from-sky-400 hover:to-cyan-400 sm:flex"
          >
            <Plus className="h-4 w-4" />
            New
          </Button>

          {/* Live notification bell */}
          <NotificationBell />

          {/* Plan badge */}
          <Badge variant="outline" className="hidden border-sky-400/30 bg-sky-400/10 text-sky-300 lg:flex">
            <Sparkles className="mr-1 h-3 w-3" />
            Pro
          </Badge>

          {/* Avatar */}
          <Avatar className="h-9 w-9 border border-white/10">
            <AvatarFallback className="bg-gradient-to-br from-sky-500 to-cyan-500 text-xs font-bold text-white">
              RJ
            </AvatarFallback>
          </Avatar>
        </div>
      </header>

      {/* Global quick capture overlay (Ctrl+K) */}
      <QuickCapture />
    </>
  );
}
