"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, useMotionValue, useSpring, useTransform, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  BrainCircuit,
  BookOpen,
  BarChart3,
  CheckSquare,
  Settings,
  Sparkles,
  Command,
} from "lucide-react";
import { cn } from "@/lib/utils";

const dockItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, color: "text-sky-400" },
  { label: "AI Chat", href: "/chat", icon: MessageSquare, color: "text-cyan-400" },
  { label: "Agents", href: "/agents", icon: Bot, color: "text-violet-400" },
  { label: "Tasks", href: "/tasks", icon: CheckSquare, color: "text-emerald-400" },
  { label: "Memory", href: "/memory", icon: BrainCircuit, color: "text-amber-400" },
  { label: "Knowledge", href: "/knowledge", icon: BookOpen, color: "text-rose-400" },
  { label: "Analytics", href: "/analytics", icon: BarChart3, color: "text-blue-400" },
  { label: "Settings", href: "/settings", icon: Settings, color: "text-slate-400" },
];

function DockIcon({
  item,
  mouseX,
  pathname,
}: {
  item: (typeof dockItems)[0];
  mouseX: any;
  pathname: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [hovered, setHovered] = useState(false);

  const distance = useTransform(mouseX, (val: number) => {
    const bounds = ref.current?.getBoundingClientRect() ?? { x: 0, width: 0 };
    return val - bounds.x - bounds.width / 2;
  });

  const widthSync = useTransform(distance, [-120, 0, 120], [42, 58, 42]);
  const width = useSpring(widthSync, { mass: 0.1, stiffness: 200, damping: 14 });

  const active = pathname === item.href || pathname.startsWith(item.href + "/");
  const Icon = item.icon;

  return (
    <div
      ref={ref}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="relative flex items-center justify-center"
    >
      <AnimatePresence>
        {hovered && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.85 }}
            animate={{ opacity: 1, y: -45, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.85 }}
            transition={{ duration: 0.15 }}
            className="pointer-events-none absolute -top-2 flex flex-col items-center z-50"
          >
            <div className="rounded-lg border border-white/15 bg-black/85 px-2.5 py-1 text-[11px] font-semibold text-white shadow-xl backdrop-blur-md whitespace-nowrap">
              {item.label}
            </div>
            <div className="h-1.5 w-1.5 rotate-45 border-r border-b border-white/15 bg-black/85" />
          </motion.div>
        )}
      </AnimatePresence>

      <Link href={item.href}>
        <motion.div
          style={{ width, height: width }}
          className={cn(
            "relative flex items-center justify-center rounded-2xl border transition-colors duration-200",
            active
              ? "border-sky-400/40 bg-gradient-to-b from-sky-400/20 to-cyan-500/10 shadow-[0_0_16px_rgba(56,189,248,0.35)] text-white"
              : "border-white/[0.08] bg-white/[0.04] text-muted-foreground hover:border-white/20 hover:bg-white/[0.08] hover:text-white"
          )}
        >
          <Icon className={cn("h-5 w-5 transition-transform duration-200", hovered && "scale-110", active && item.color)} />
          {active && (
            <span className="absolute -bottom-1 h-1 w-1 rounded-full bg-sky-400 shadow-[0_0_6px_#38bdf8]" />
          )}
        </motion.div>
      </Link>
    </div>
  );
}

export function SpatialDock() {
  const mouseX = useMotionValue(Infinity);
  const pathname = usePathname();

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
      onMouseMove={(e) => mouseX.set(e.pageX)}
      onMouseLeave={() => mouseX.set(Infinity)}
      className="fixed bottom-5 left-1/2 -translate-x-1/2 z-40 hidden md:flex items-center gap-2 rounded-3xl border border-white/[0.12] bg-black/60 px-4 py-2.5 backdrop-blur-3xl shadow-[0_20px_50px_rgba(0,0,0,0.8),0_0_20px_rgba(56,189,248,0.1)]"
      style={{ perspective: "1000px" }}
    >
      {/* 3D Top Specular Light Line */}
      <div className="pointer-events-none absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />

      {dockItems.map((item) => (
        <DockIcon key={item.label} item={item} mouseX={mouseX} pathname={pathname} />
      ))}

      {/* Quick capture button separator & trigger */}
      <div className="h-6 w-px bg-white/10 mx-1" />

      <button
        onClick={() => document.dispatchEvent(new CustomEvent("open-quick-capture"))}
        className="flex h-10 w-10 items-center justify-center rounded-2xl border border-sky-400/30 bg-sky-400/10 text-sky-300 hover:bg-sky-400/20 hover:text-white transition-all duration-200"
        title="Quick Capture (Ctrl+K)"
      >
        <Sparkles className="h-4 w-4" />
      </button>
    </motion.div>
  );
}
