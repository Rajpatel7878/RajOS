"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { StickyNote, Plus, Search, Pin, Trash2, Loader2, X } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getNotes, createNote, deleteNote, type Note } from "@/services/api/notes";

const noteColors = [
  "from-sky-500/20 to-cyan-500/5",
  "from-violet-500/20 to-purple-500/5",
  "from-emerald-500/20 to-teal-500/5",
  "from-amber-500/20 to-orange-500/5",
  "from-rose-500/20 to-pink-500/5",
  "from-cyan-500/20 to-sky-500/5",
];

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [creating, setCreating] = useState(false);

  const loadNotes = async () => {
    try {
      setLoading(true);
      const data = await getNotes();
      setNotes(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotes();
  }, []);

  const handleCreate = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    setCreating(true);
    try {
      await createNote({ title: newTitle.trim(), content: newContent.trim() });
      setNewTitle("");
      setNewContent("");
      setShowForm(false);
      await loadNotes();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create note");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (noteId: number) => {
    try {
      await deleteNote(noteId);
      setNotes((prev) => prev.filter((n) => n.id !== noteId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete note");
    }
  };

  const filtered = notes.filter(
    (n) =>
      !search ||
      n.title.toLowerCase().includes(search.toLowerCase()) ||
      n.content.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Notes</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {notes.length} notes · Capture ideas and quick thoughts.
          </p>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
        >
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
          {showForm ? "Cancel" : "New Note"}
        </Button>
      </div>

      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <GlassCard className="p-5 space-y-3">
            <Input
              placeholder="Note title..."
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="border-white/[0.08] bg-white/[0.02] text-white placeholder:text-muted-foreground/60"
            />
            <textarea
              placeholder="Write your note content..."
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              rows={4}
              className="w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 py-2 text-sm text-white placeholder:text-muted-foreground/60 focus:outline-none focus:border-sky-400/50 resize-none"
            />
            <Button
              onClick={handleCreate}
              disabled={creating || !newTitle.trim() || !newContent.trim()}
              className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
            >
              {creating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Save Note
            </Button>
          </GlassCard>
        </motion.div>
      )}

      {error && (
        <div className="mb-4 rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      <div className="mb-6 relative max-w-md">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search notes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border-white/[0.08] bg-white/[0.02] pl-11 text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02]">
            <StickyNote className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold text-white">No notes found</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {search ? "Try adjusting your search." : "Create your first note above."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((note, i) => {
            const color = noteColors[i % noteColors.length];
            return (
              <motion.div
                key={note.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
              >
                <GlassCard hover className="relative overflow-hidden p-5 group">
                  <div
                    className={`pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br ${color} blur-2xl`}
                  />
                  <div className="relative flex items-start justify-between">
                    <StickyNote className="h-5 w-5 text-sky-400/70" />
                    <button
                      onClick={() => handleDelete(note.id)}
                      className="opacity-0 group-hover:opacity-100 rounded-lg p-1 text-muted-foreground transition-all hover:bg-rose-500/10 hover:text-rose-400"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <h3 className="relative mt-3 font-semibold text-white">
                    {note.title}
                  </h3>
                  <p className="relative mt-1.5 text-sm leading-relaxed text-muted-foreground line-clamp-3">
                    {note.content}
                  </p>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
