'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  MessageSquare,
  Bot,
  BrainCircuit,
  BookOpen,
  BarChart3,
  Settings,
  ChevronLeft,
  Sparkles,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { navItems } from '@/lib/data';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  LayoutDashboard,
  MessageSquare,
  Bot,
  BrainCircuit,
  BookOpen,
  BarChart3,
  Settings,
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
      animate={{ width: collapsed ? 76 : 264 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="sticky top-0 z-30 flex h-screen shrink-0 flex-col border-r border-white/[0.06] bg-black/40 backdrop-blur-2xl"
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-5">
        <Link href="/" className="flex items-center gap-2.5 overflow-hidden">
          <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 shadow-lg shadow-sky-500/30">
            <Sparkles className="h-5 w-5 text-white" />
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 blur-md opacity-50 -z-10" />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                className="flex flex-col leading-none"
              >
                <span className="text-[15px] font-bold tracking-tight text-white">
                  RajOS
                </span>
                <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-sky-400/70">
                  AI Operating System
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </Link>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={onToggle}
        className="mx-auto mb-2 flex h-6 w-6 items-center justify-center rounded-md border border-white/10 bg-white/5 text-muted-foreground transition-colors hover:bg-white/10 hover:text-white"
        aria-label="Toggle sidebar"
      >
        <ChevronLeft
          className={cn(
            'h-3.5 w-3.5 transition-transform duration-300',
            collapsed && 'rotate-180'
          )}
        />
      </button>

      {/* Nav */}
      <nav className="flex flex-1 flex-col gap-1 px-3 py-2">
        <AnimatePresence>
          {!collapsed && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="px-3 pb-2 pt-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-muted-foreground/60"
            >
              Workspace
            </motion.p>
          )}
        </AnimatePresence>
        {navItems.map((item) => {
          const Icon = iconMap[item.icon] ?? LayoutDashboard;
          const active =
            pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all',
                active
                  ? 'text-white'
                  : 'text-muted-foreground hover:text-white hover:bg-white/[0.04]'
              )}
            >
              {active && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-xl border border-sky-400/20 bg-gradient-to-r from-sky-500/15 to-cyan-500/5"
                  transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                />
              )}
              {active && (
                <motion.div
                  layoutId="sidebar-indicator"
                  className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-full bg-gradient-to-b from-sky-400 to-cyan-400"
                />
              )}
              <Icon
                className={cn(
                  'relative h-[18px] w-[18px] shrink-0 transition-colors',
                  active
                    ? 'text-sky-400'
                    : 'text-muted-foreground group-hover:text-sky-400/80'
                )}
              />
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -6 }}
                    className="relative"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </nav>

      {/* System status */}
      <div className="border-t border-white/[0.06] p-3">
        <div
          className={cn(
            'flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-3',
            collapsed && 'justify-center px-0'
          )}
        >
          <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10">
            <Zap className="h-4 w-4 text-emerald-400" />
            <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 ring-2 ring-black/50">
              <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-60" />
            </span>
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col leading-tight"
              >
                <span className="text-xs font-semibold text-white">
                  System Online
                </span>
                <span className="text-[10px] text-muted-foreground">
                  6 agents · 4 LLMs active
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
}

export function useSidebarState() {
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => {
    const stored = localStorage.getItem('rajos-sidebar-collapsed');
    if (stored === 'true') setCollapsed(true);
  }, []);
  useEffect(() => {
    localStorage.setItem('rajos-sidebar-collapsed', String(collapsed));
  }, [collapsed]);
  return [collapsed, setCollapsed] as const;
}
