"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  Search,
  Database,
  Zap,
  BookOpen,
  Check,
  Loader2,
  X,
  File,
  Code,
  Network,
  Sparkles,
  AlertCircle,
  Plus,
} from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { GlassCard } from "@/components/glass-card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { KnowledgeGraph } from "@/components/knowledge-graph";
import { cn } from "@/lib/utils";
import {
  getDocuments,
  searchKnowledge,
  getKnowledgeStats,
  uploadDocument,
  type DocumentItem,
  type SearchHit,
  type KnowledgeStats,
} from "@/services/api/documents";

const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  "text/plain": FileText,
  "text/markdown": Code,
  "application/json": Code,
  "text/csv": Database,
};

const statusStyles: Record<string, string> = {
  ready: "border-emerald-400/30 bg-emerald-400/10 text-emerald-300",
  processing: "border-amber-400/30 bg-amber-400/10 text-amber-300",
  failed: "border-rose-400/30 bg-rose-400/10 text-rose-300",
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [stats, setStats] = useState<KnowledgeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchHit[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const [showUpload, setShowUpload] = useState(false);
  const [filename, setFilename] = useState("");
  const [content, setContent] = useState("");
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [docs, kStats] = await Promise.all([
        getDocuments(),
        getKnowledgeStats().catch(() => null),
      ]);
      setDocuments(docs);
      if (kStats) setStats(kStats);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load knowledge base");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const results = await searchKnowledge(searchQuery.trim());
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Knowledge search failed");
    } finally {
      setIsSearching(false);
    }
  };

  const handleUploadSubmit = async () => {
    if (!filename.trim() || !content.trim()) return;
    setUploading(true);
    try {
      let mime = "text/plain";
      if (filename.endsWith(".md")) mime = "text/markdown";
      else if (filename.endsWith(".json")) mime = "application/json";
      else if (filename.endsWith(".csv")) mime = "text/csv";

      await uploadDocument({
        filename: filename.trim(),
        content: content.trim(),
        mime_type: mime,
      });

      setFilename("");
      setContent("");
      setShowUpload(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  return (
    <AppShell>
      {/* Stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            label: "Knowledge Documents",
            value: stats ? stats.total_documents : documents.length,
            icon: FileText,
            color: "text-sky-400",
          },
          {
            label: "Vector Chunks",
            value: stats ? stats.total_chunks : 0,
            icon: Network,
            color: "text-cyan-400",
          },
          {
            label: "Ready Index Ratio",
            value: stats && stats.total_documents ? `${Math.round((stats.ready_documents / stats.total_documents) * 100)}%` : "100%",
            icon: Sparkles,
            color: "text-emerald-400",
          },
          {
            label: "Storage Size",
            value: stats ? formatBytes(stats.total_file_size_bytes) : "0 B",
            icon: Database,
            color: "text-amber-400",
          },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.05} className="p-5">
            <div className={cn("flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]", stat.color)}>
              <stat.icon className="h-5 w-5" />
            </div>
            <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-xs text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Left: Upload + Documents List */}
        <div className="space-y-6 lg:col-span-2">
          {/* Upload Card */}
          <GlassCard hover={false} className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-white">Document Ingestion</h3>
              <Button
                size="sm"
                variant="outline"
                className="gap-2 border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]"
                onClick={() => setShowUpload(!showUpload)}
              >
                {showUpload ? <X className="h-3.5 w-3.5" /> : <Upload className="h-3.5 w-3.5" />}
                {showUpload ? "Cancel" : "Upload"}
              </Button>
            </div>

            <AnimatePresence mode="popLayout">
              {showUpload ? (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="space-y-3">
                  <input
                    type="text"
                    placeholder="Filename (e.g. Operating_Systems_Notes.md)"
                    value={filename}
                    onChange={(e) => setFilename(e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-white placeholder:text-muted-foreground focus:outline-none"
                  />
                  <textarea
                    placeholder="Paste document text..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    rows={4}
                    className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-xs text-white placeholder:text-muted-foreground focus:outline-none resize-none font-mono"
                  />
                  <Button
                    onClick={handleUploadSubmit}
                    disabled={uploading || !filename.trim() || !content.trim()}
                    size="sm"
                    className="w-full gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white"
                  >
                    {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                    Chunk & Index Document
                  </Button>
                </motion.div>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: "Ready", value: documents.filter((d) => d.status === "ready").length, color: "text-emerald-400" },
                    { label: "Processing", value: documents.filter((d) => d.status === "processing").length, color: "text-amber-400" },
                  ].map((s) => (
                    <div key={s.label} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                      <p className={cn("text-2xl font-bold", s.color)}>{s.value}</p>
                      <p className="text-xs text-muted-foreground">{s.label}</p>
                    </div>
                  ))}
                </div>
              )}
            </AnimatePresence>
          </GlassCard>

          {/* Document list */}
          <GlassCard hover={false} className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-white">Indexed Knowledge Base</h3>
              <span className="text-xs text-muted-foreground">{documents.length} files</span>
            </div>
            <div className="space-y-2 max-h-[400px] overflow-y-auto no-scrollbar">
              {documents.map((doc, i) => {
                const Icon = typeIcons[doc.mime_type] ?? FileText;
                return (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="group flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 transition-all hover:border-sky-400/20 hover:bg-white/[0.04]"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.02]">
                      <Icon className="h-4 w-4 text-sky-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs font-semibold text-white">{doc.title || doc.filename}</p>
                      <p className="text-[11px] text-muted-foreground">{formatBytes(doc.file_size)}</p>
                    </div>
                    <span className={cn("shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold capitalize", statusStyles[doc.status] || "border-white/10 bg-white/5 text-white")}>
                      {doc.status === "processing" && <Loader2 className="mr-1 inline h-2.5 w-2.5 animate-spin" />}
                      {doc.status}
                    </span>
                  </motion.div>
                );
              })}
            </div>
          </GlassCard>
        </div>

        {/* Right: Knowledge Graph + Hybrid Semantic Search */}
        <div className="space-y-6 lg:col-span-3">
          {/* Knowledge graph */}
          <GlassCard hover={false} className="p-0">
            <div className="flex items-center justify-between p-6 pb-3">
              <div>
                <h3 className="font-semibold text-white">Knowledge Graph</h3>
                <p className="text-xs text-muted-foreground">Semantic relationship graph across indexed document chunks</p>
              </div>
              <Badge variant="outline" className="border-sky-400/30 bg-sky-400/10 text-sky-300">
                <Sparkles className="mr-1 h-3 w-3" />
                Active RAG 2.0
              </Badge>
            </div>
            <div className="h-[380px] w-full px-2 pb-4">
              <KnowledgeGraph className="h-full w-full rounded-xl" />
            </div>
          </GlassCard>

          {/* Semantic search */}
          <GlassCard hover={false} className="p-6">
            <h3 className="mb-1 font-semibold text-white">Hybrid Semantic & Keyword Search</h3>
            <p className="mb-4 text-xs text-muted-foreground">Vector similarity search fused with exact SQL keyword density matching.</p>

            <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="flex gap-2">
              <div className="flex flex-1 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2.5 focus-within:border-sky-400/30">
                <Search className="h-4 w-4 text-muted-foreground" />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Ask anything about your uploaded documents..."
                  className="w-full bg-transparent text-sm text-white placeholder:text-muted-foreground focus:outline-none"
                />
              </div>
              <Button
                type="submit"
                disabled={isSearching || !searchQuery.trim()}
                className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
              >
                {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                Search
              </Button>
            </form>

            {/* Search Results */}
            {searchResults && (
              <div className="mt-4 space-y-3">
                <p className="text-xs font-medium text-muted-foreground">Retrieved knowledge chunks · {searchResults.length} hits</p>
                {searchResults.map((hit, i) => (
                  <motion.div
                    key={hit.chunk_id || i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <BookOpen className="h-4 w-4 text-emerald-400" />
                        <span className="text-sm font-semibold text-white">{hit.filename}</span>
                        <span className="text-xs text-sky-400/80 font-mono">({hit.heading})</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/5">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-sky-400 to-cyan-400"
                            style={{ width: `${Math.min(100, hit.score * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-sky-300">{(hit.score * 100).toFixed(0)}%</span>
                      </div>
                    </div>

                    <p className="mt-2 text-xs leading-relaxed text-slate-300 font-mono">{hit.content}</p>

                    <div className="mt-3 flex items-center gap-3 text-[11px] text-muted-foreground">
                      <span className="flex items-center gap-1"><Check className="h-3 w-3 text-emerald-400" /> Verified chunk</span>
                      <span className="flex items-center gap-1"><Database className="h-3 w-3 text-cyan-400" /> Hybrid reranked</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {!searchResults && !isSearching && (
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="text-xs text-muted-foreground">Suggested queries:</span>
                {["framework", "scheduling", "architecture", "database"].map((q) => (
                  <button
                    key={q}
                    onClick={() => { setSearchQuery(q); }}
                    className="rounded-full border border-white/10 bg-white/[0.02] px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-sky-400/20 hover:text-sky-300"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </GlassCard>
        </div>
      </div>
    </AppShell>
  );
}
