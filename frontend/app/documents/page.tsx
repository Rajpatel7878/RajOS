"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Upload,
  File,
  FileCode,
  FileSpreadsheet,
  Trash2,
  Loader2,
  X,
  Plus,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  getDocuments,
  uploadDocument,
  deleteDocument,
  type DocumentItem,
} from "@/services/api/documents";

const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  "text/plain": FileText,
  "text/markdown": FileCode,
  "application/json": FileCode,
  "text/csv": FileSpreadsheet,
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [filename, setFilename] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [activeDoc, setActiveDoc] = useState<DocumentItem | null>(null);

  const loadDocs = async () => {
    try {
      setLoading(true);
      const data = await getDocuments();
      setDocuments(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUploadSubmit = async () => {
    if (!filename.trim() || !content.trim()) return;
    setSubmitting(true);
    try {
      let mime = "text/plain";
      if (filename.endsWith(".md")) mime = "text/markdown";
      else if (filename.endsWith(".json")) mime = "application/json";
      else if (filename.endsWith(".csv")) mime = "text/csv";

      await uploadDocument({
        filename: filename.trim(),
        title: title.trim() || filename.trim(),
        content: content.trim(),
        mime_type: mime,
      });

      setFilename("");
      setTitle("");
      setContent("");
      setShowUploadModal(false);
      await loadDocs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to upload document");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (activeDoc?.id === id) setActiveDoc(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete document");
    }
  };

  const handleFileDrop = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setFilename(file.name);
    setTitle(file.name.replace(/\.[^/.]+$/, ""));

    const reader = new FileReader();
    reader.onload = (event) => {
      if (event.target?.result) {
        setContent(event.target.result as string);
      }
    };
    reader.readAsText(file);
  };

  return (
    <AppShell>
      <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Documents</h1>
          <p className="mt-1 text-sm text-muted-foreground">Upload, chunk, and index documents for RAG 2.0 Knowledge Search.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={loadDocs} variant="outline" size="sm" className="gap-2 border-white/10 text-white">
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </Button>
          <Button
            onClick={() => setShowUploadModal(true)}
            className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
          >
            <Upload className="h-4 w-4" />
            Upload Document
          </Button>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Upload Modal / Form */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="mb-6">
            <GlassCard className="p-6 space-y-4 border-sky-500/30">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <Upload className="h-4 w-4 text-sky-400" />
                  Upload & Process Knowledge Document
                </h3>
                <button onClick={() => setShowUploadModal(false)} className="text-muted-foreground hover:text-white">
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Quick File Select</label>
                  <input
                    type="file"
                    accept=".txt,.md,.json,.csv"
                    onChange={handleFileDrop}
                    className="w-full text-xs text-muted-foreground file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-sky-500/20 file:text-sky-300 hover:file:bg-sky-500/30 cursor-pointer"
                  />
                </div>

                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Filename</label>
                  <Input
                    placeholder="e.g. Operating_Systems_Notes.md"
                    value={filename}
                    onChange={(e) => setFilename(e.target.value)}
                    className="border-white/[0.08] bg-white/[0.02] text-xs text-white"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Title (Optional)</label>
                <Input
                  placeholder="e.g. Operating Systems Chapter 4 Notes"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="border-white/[0.08] bg-white/[0.02] text-xs text-white"
                />
              </div>

              <div>
                <label className="text-xs text-muted-foreground mb-1 block">Document Text Content</label>
                <textarea
                  placeholder="Paste or drop document text here..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={6}
                  className="w-full rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 py-2 text-xs text-white placeholder:text-muted-foreground/60 focus:outline-none focus:border-sky-400/50 resize-none font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button type="button" onClick={() => setShowUploadModal(false)} variant="outline" size="sm" className="border-white/10">
                  Cancel
                </Button>
                <Button
                  onClick={handleUploadSubmit}
                  disabled={submitting || !filename.trim() || !content.trim()}
                  size="sm"
                  className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
                >
                  {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                  Process & Index
                </Button>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document Detail Viewer Drawer / Modal */}
      <AnimatePresence>
        {activeDoc && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl border border-white/10 bg-slate-950 p-6 shadow-2xl flex flex-col">
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3 mb-4">
                <div>
                  <h2 className="text-lg font-bold text-white">{activeDoc.title || activeDoc.filename}</h2>
                  <p className="text-xs text-muted-foreground">{activeDoc.filename} · {formatBytes(activeDoc.file_size)}</p>
                </div>
                <button onClick={() => setActiveDoc(null)} className="rounded-lg p-1 text-muted-foreground hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto bg-black/40 rounded-xl p-4 border border-white/[0.06] text-xs font-mono text-slate-200 whitespace-pre-wrap">
                {activeDoc.content}
              </div>

              <div className="mt-4 pt-3 border-t border-white/[0.08] flex items-center justify-between">
                <span className="text-xs text-muted-foreground">ID #{activeDoc.id} · Status: {activeDoc.status}</span>
                <Button onClick={() => setActiveDoc(null)} size="sm" variant="outline" className="border-white/10">
                  Close
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Document List Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc, i) => {
            const Icon = typeIcons[doc.mime_type] ?? File;
            return (
              <motion.div key={doc.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                <GlassCard hover className="flex items-center gap-4 p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-sky-500/10 text-sky-400">
                    <Icon className="h-5 w-5" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-semibold text-white">{doc.title || doc.filename}</p>
                    <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                      <span>{doc.filename}</span>
                      <span>·</span>
                      <span>{formatBytes(doc.file_size)}</span>
                      <span>·</span>
                      <span className="flex items-center gap-1">
                        {doc.status === "ready" && <CheckCircle2 className="h-3 w-3 text-emerald-400" />}
                        {doc.status === "processing" && <Loader2 className="h-3 w-3 animate-spin text-amber-400" />}
                        {doc.status === "failed" && <AlertTriangle className="h-3 w-3 text-rose-400" />}
                        <span className="capitalize">{doc.status}</span>
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button onClick={() => setActiveDoc(doc)} size="sm" variant="outline" className="text-xs border-white/10">
                      View Content
                    </Button>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="rounded-lg p-2 text-muted-foreground hover:bg-rose-500/10 hover:text-rose-400 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      )}

      {!loading && documents.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.02]">
            <FileText className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="font-semibold text-white">No knowledge documents found</h3>
          <p className="mt-1 text-sm text-muted-foreground">Upload your first document above to enable AI Retrieval-Augmented Generation.</p>
        </div>
      )}
    </AppShell>
  );
}
