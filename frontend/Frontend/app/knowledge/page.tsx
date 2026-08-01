'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  Globe,
  Code,
  Database as FileData,
  Network,
  Sparkles,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { KnowledgeGraph } from '@/components/knowledge-graph';
import { cn } from '@/lib/utils';
import { knowledgeDocs } from '@/lib/data';

const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  PDF: FileText,
  Web: Globe,
  Note: FileText,
  Code: Code,
  Data: Database,
};

const statusStyles: Record<string, string> = {
  Indexed: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',
  Processing: 'border-amber-400/30 bg-amber-400/10 text-amber-300',
  Failed: 'border-red-400/30 bg-red-400/10 text-red-300',
};

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [searchResults, setSearchResults] = useState<{ title: string; snippet: string; score: number }[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const filteredDocs = knowledgeDocs.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    setTimeout(() => {
      setSearchResults([
        { title: 'Q3 Financial Report', snippet: 'Revenue increased 34% quarter-over-quarter, driven primarily by enterprise contract expansion in the EMEA region...', score: 0.94 },
        { title: 'Market Analysis 2025', snippet: 'The AI platform market is projected to reach $280B by 2028, with personal AI assistants showing the highest growth velocity...', score: 0.87 },
        { title: 'API Reference Documentation', snippet: 'The vector search endpoint accepts a query string and returns the top-K semantically similar chunks from the knowledge base...', score: 0.81 },
      ]);
      setIsSearching(false);
    }, 1200);
  };

  const totalVectors = knowledgeDocs.reduce((sum, d) => sum + d.vectors, 0);
  const totalChunks = knowledgeDocs.reduce((sum, d) => sum + d.chunks, 0);

  return (
    <AppShell>
      {/* Stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Documents', value: String(knowledgeDocs.length), icon: FileText, color: 'text-sky-400' },
          { label: 'Vector Embeddings', value: totalVectors.toLocaleString(), icon: Database, color: 'text-cyan-400' },
          { label: 'Text Chunks', value: totalChunks.toLocaleString(), icon: Network, color: 'text-emerald-400' },
          { label: 'Avg Retrieval', value: '42ms', icon: Zap, color: 'text-amber-400' },
        ].map((stat, i) => (
          <GlassCard key={stat.label} delay={i * 0.06} className="p-5">
            <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]', stat.color)}>
              <stat.icon className="h-5 w-5" />
            </div>
            <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-sm text-muted-foreground">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Left: Upload + documents */}
        <div className="space-y-6 lg:col-span-2">
          {/* Upload zone */}
          <GlassCard hover={false} className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-white">Document Upload</h3>
              <Button
                size="sm"
                variant="outline"
                className="gap-2 border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]"
                onClick={() => setShowUpload(!showUpload)}
              >
                <Upload className="h-3.5 w-3.5" />
                Upload
              </Button>
            </div>

            <AnimatePresence>
              {showUpload ? (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="rounded-xl border-2 border-dashed border-sky-400/30 bg-sky-400/5 p-8 text-center">
                    <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-sky-400/10">
                      <Upload className="h-6 w-6 text-sky-400" />
                    </div>
                    <p className="text-sm font-medium text-white">Drop files here</p>
                    <p className="mt-1 text-xs text-muted-foreground">PDF, TXT, MD, DOCX, CSV — up to 50MB</p>
                    <Button className="mt-4 gap-2 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400" size="sm">
                      <File className="h-3.5 w-3.5" />
                      Browse Files
                    </Button>
                  </div>
                </motion.div>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Indexed', value: knowledgeDocs.filter(d => d.status === 'Indexed').length, color: 'text-emerald-400' },
                    { label: 'Processing', value: knowledgeDocs.filter(d => d.status === 'Processing').length, color: 'text-amber-400' },
                  ].map((s) => (
                    <div key={s.label} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                      <p className={cn('text-2xl font-bold', s.color)}>{s.value}</p>
                      <p className="text-xs text-muted-foreground">{s.label}</p>
                    </div>
                  ))}
                </div>
              )}
            </AnimatePresence>
          </GlassCard>

          {/* Documents list */}
          <GlassCard hover={false} className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-white">Knowledge Documents</h3>
              <span className="text-xs text-muted-foreground">{filteredDocs.length} files</span>
            </div>
            <div className="space-y-2 max-h-[400px] overflow-y-auto no-scrollbar">
              {filteredDocs.map((doc, i) => {
                const Icon = typeIcons[doc.type] ?? FileText;
                return (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className="group flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 transition-all hover:border-sky-400/20 hover:bg-white/[0.04]"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.02]">
                      <Icon className="h-4 w-4 text-sky-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-white">{doc.title}</p>
                      <p className="text-xs text-muted-foreground">{doc.chunks} chunks · {doc.size}</p>
                    </div>
                    <span className={cn('shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold', statusStyles[doc.status])}>
                      {doc.status === 'Processing' && <Loader2 className="mr-1 inline h-2.5 w-2.5 animate-spin" />}
                      {doc.status}
                    </span>
                  </motion.div>
                );
              })}
            </div>
          </GlassCard>
        </div>

        {/* Right: Knowledge graph + semantic search */}
        <div className="space-y-6 lg:col-span-3">
          {/* Knowledge graph */}
          <GlassCard hover={false} className="p-0">
            <div className="flex items-center justify-between p-6 pb-3">
              <div>
                <h3 className="font-semibold text-white">Knowledge Graph</h3>
                <p className="text-sm text-muted-foreground">Semantic relationships across your knowledge base</p>
              </div>
              <Badge variant="outline" className="border-sky-400/30 bg-sky-400/10 text-sky-300">
                <Sparkles className="mr-1 h-3 w-3" />
                Live
              </Badge>
            </div>
            <div className="h-[420px] w-full px-2 pb-4">
              <KnowledgeGraph className="h-full w-full rounded-xl" />
            </div>
          </GlassCard>

          {/* Semantic search */}
          <GlassCard hover={false} className="p-6">
            <h3 className="mb-1 font-semibold text-white">Semantic Search</h3>
            <p className="mb-4 text-sm text-muted-foreground">Search by meaning, not keywords. Powered by vector similarity.</p>

            <div className="flex gap-2">
              <div className="flex flex-1 items-center gap-2 rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2.5 focus-within:border-sky-400/30">
                <Search className="h-4 w-4 text-muted-foreground" />
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Ask anything about your documents..."
                  className="w-full bg-transparent text-sm text-white placeholder:text-muted-foreground focus:outline-none"
                />
              </div>
              <Button
                onClick={handleSearch}
                disabled={isSearching}
                className="gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
              >
                {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                Search
              </Button>
            </div>

            {/* Results */}
            {searchResults && (
              <div className="mt-4 space-y-3">
                <p className="text-xs font-medium text-muted-foreground">Retrieved context · {searchResults.length} sources</p>
                {searchResults.map((result, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <BookOpen className="h-4 w-4 text-emerald-400" />
                        <span className="text-sm font-medium text-white">{result.title}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-20 overflow-hidden rounded-full bg-white/5">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-sky-400 to-cyan-400"
                            style={{ width: `${result.score * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-semibold text-sky-300">{(result.score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{result.snippet}</p>
                    <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1"><Check className="h-3 w-3 text-emerald-400" /> Verified source</span>
                      <span className="flex items-center gap-1"><Database className="h-3 w-3 text-cyan-400" /> Vector match</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {!searchResults && !isSearching && (
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="text-xs text-muted-foreground">Try:</span>
                {['revenue growth', 'agent architecture', 'user retention'].map((q) => (
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
