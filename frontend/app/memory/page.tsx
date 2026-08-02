'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  BrainCircuit,
  Target,
  Star,
  Settings,
  Lightbulb,
  BookOpen,
  TrendingUp,
  Plus,
  Filter,
  Sparkles,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { memoryItems } from '@/lib/data';
import type { MemoryCategory, Importance } from '@/lib/types';

const categories: { label: MemoryCategory | 'All'; icon: React.ComponentType<{ className?: string }>; count?: number }[] = [
  { label: 'All', icon: Sparkles },
  { label: 'Projects', icon: Target },
  { label: 'Goals', icon: TrendingUp },
  { label: 'Preferences', icon: Settings },
  { label: 'Skills', icon: Lightbulb },
  { label: 'Knowledge', icon: BookOpen },
];

const importanceColors: Record<Importance, string> = {
  Critical: 'border-rose-400/30 bg-rose-400/10 text-rose-300',
  High: 'border-amber-400/30 bg-amber-400/10 text-amber-300',
  Medium: 'border-sky-400/30 bg-sky-400/10 text-sky-300',
  Low: 'border-white/15 bg-white/5 text-muted-foreground',
};

const categoryColors: Record<MemoryCategory, string> = {
  Projects: 'text-sky-400',
  Goals: 'text-emerald-400',
  Preferences: 'text-amber-400',
  Skills: 'text-violet-400',
  Knowledge: 'text-cyan-400',
};

export default function MemoryPage() {
  const [activeCategory, setActiveCategory] = useState<MemoryCategory | 'All'>('All');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return memoryItems.filter((item) => {
      const matchCat = activeCategory === 'All' || item.category === activeCategory;
      const matchSearch =
        !search ||
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.description.toLowerCase().includes(search.toLowerCase()) ||
        item.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()));
      return matchCat && matchSearch;
    });
  }, [activeCategory, search]);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    memoryItems.forEach((m) => {
      counts[m.category] = (counts[m.category] || 0) + 1;
    });
    return counts;
  }, []);

  return (
    <AppShell>
      {/* Stats row */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Total Memories', value: '8,206', icon: BrainCircuit, color: 'text-sky-400', change: '+248 this week' },
          { label: 'Critical Items', value: '142', icon: Star, color: 'text-rose-400', change: '+12 this week' },
          { label: 'Avg Relevance', value: '81.4', icon: TrendingUp, color: 'text-emerald-400', change: '+3.2 pts' },
          { label: 'Categories', value: '5', icon: Filter, color: 'text-violet-400', change: 'all active' },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.06} className="p-5">
            <div className="flex items-center justify-between">
              <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]', stat.color)}>
                <stat.icon className="h-5 w-5" />
              </div>
              <span className="text-xs text-muted-foreground">{stat.change}</span>
            </div>
            <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-sm text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => {
            const count = cat.label === 'All' ? memoryItems.length : categoryCounts[cat.label] || 0;
            return (
              <button
                key={cat.label}
                onClick={() => setActiveCategory(cat.label)}
                className={cn(
                  'flex items-center gap-2 rounded-xl border px-3.5 py-2 text-sm font-medium transition-all',
                  activeCategory === cat.label
                    ? 'border-sky-400/30 bg-sky-400/10 text-sky-300'
                    : 'border-white/[0.08] bg-white/[0.02] text-muted-foreground hover:text-white hover:border-white/15'
                )}
              >
                <cat.icon className="h-4 w-4" />
                {cat.label}
                <span className="rounded-full bg-white/5 px-1.5 py-0.5 text-[10px] text-muted-foreground">{count}</span>
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search memories..."
              className="w-full bg-transparent text-sm text-white placeholder:text-muted-foreground focus:outline-none lg:w-48"
            />
          </div>
          <Button className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">
            <Plus className="h-4 w-4" />
            Add Memory
          </Button>
        </div>
      </div>

      {/* Memory cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <AnimatePresence mode="popLayout">
          {filtered.map((item, i) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, delay: i * 0.04 }}
            >
              <GlassCard className="h-full p-5">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className={cn('text-xs font-semibold uppercase tracking-wider', categoryColors[item.category])}>
                      {item.category}
                    </span>
                  </div>
                  <span className={cn('rounded-full border px-2 py-0.5 text-[10px] font-semibold', importanceColors[item.importance])}>
                    {item.importance}
                  </span>
                </div>

                <h3 className="mt-3 font-semibold text-white">{item.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground line-clamp-3">
                  {item.description}
                </p>

                <div className="mt-4 flex flex-wrap gap-1.5">
                  {item.tags.map((tag) => (
                    <span key={tag} className="rounded-md bg-white/5 px-2 py-0.5 text-xs text-muted-foreground">
                      #{tag}
                    </span>
                  ))}
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-white/[0.06] pt-3">
                  <span className="text-xs text-muted-foreground">{item.createdAt}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-muted-foreground">AI Relevance</span>
                    <div className="flex items-center gap-1">
                      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/5">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.relevanceScore}%` }}
                          transition={{ duration: 1, delay: 0.2 + i * 0.04, ease: 'easeOut' }}
                          className="h-full rounded-full bg-gradient-to-r from-sky-400 to-cyan-400"
                        />
                      </div>
                      <span className="text-xs font-semibold text-white">{item.relevanceScore}</span>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02]">
            <Search className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold text-white">No memories found</h3>
          <p className="mt-1 text-sm text-muted-foreground">Try adjusting your search or filters.</p>
        </div>
      )}
    </AppShell>
  );
}
