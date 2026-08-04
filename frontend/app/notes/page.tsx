'use client';

import { motion } from 'framer-motion';
import { StickyNote, Plus, Search, Pin } from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const sampleNotes = [
  { id: 1, title: 'Product roadmap brainstorm', excerpt: 'Key milestones for Q4: multi-agent orchestration, voice commands, mobile app...', color: 'from-sky-500/20 to-cyan-500/5', pinned: true, date: '2 hours ago' },
  { id: 2, title: 'Meeting notes — investor call', excerpt: 'Discussed Series A timeline, key metrics to highlight, competitive landscape...', color: 'from-violet-500/20 to-purple-500/5', pinned: true, date: 'Yesterday' },
  { id: 3, title: 'Agent architecture ideas', excerpt: 'Consider event-driven model for agent communication. Pub/sub pattern with...', color: 'from-emerald-500/20 to-teal-500/5', pinned: false, date: '3 days ago' },
  { id: 4, title: 'Customer feedback themes', excerpt: 'Top requests: export to PDF, team sharing, custom agent templates...', color: 'from-amber-500/20 to-orange-500/5', pinned: false, date: '5 days ago' },
  { id: 5, title: 'Research — RAG optimization', excerpt: 'Chunking strategies: sliding window vs semantic boundaries. Embedding...', color: 'from-rose-500/20 to-pink-500/5', pinned: false, date: '1 week ago' },
  { id: 6, title: 'Hiring notes — ML engineer', excerpt: 'Looking for someone with RAG experience, production deployment, and...', color: 'from-cyan-500/20 to-sky-500/5', pinned: false, date: '1 week ago' },
];

export default function NotesPage() {
  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Notes</h1>
          <p className="mt-1 text-sm text-muted-foreground">Capture ideas, meeting notes, and quick thoughts.</p>
        </div>
        <Button className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">
          <Plus className="h-4 w-4" />
          New Note
        </Button>
      </div>

      <div className="mb-6 relative max-w-md">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search notes..."
          className="border-white/[0.08] bg-white/[0.02] pl-11 text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sampleNotes.map((note, i) => (
          <motion.div
            key={note.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
          >
            <GlassCard hover className={`relative overflow-hidden p-5`}>
              <div className={`pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br ${note.color} blur-2xl`} />
              <div className="relative flex items-start justify-between">
                <StickyNote className="h-5 w-5 text-sky-400/70" />
                {note.pinned && <Pin className="h-4 w-4 text-amber-400/70" />}
              </div>
              <h3 className="relative mt-3 font-semibold text-white">{note.title}</h3>
              <p className="relative mt-1.5 text-sm leading-relaxed text-muted-foreground line-clamp-2">{note.excerpt}</p>
              <p className="relative mt-3 text-xs text-muted-foreground/60">{note.date}</p>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </AppShell>
  );
}
