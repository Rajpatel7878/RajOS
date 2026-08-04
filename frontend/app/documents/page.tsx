'use client';

import { motion } from 'framer-motion';
import {
  FileText,
  Upload,
  File,
  FileImage,
  FileSpreadsheet,
  FileCode,
  MoreVertical,
  Download,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';

const sampleDocs = [
  { id: 1, name: 'Q3-Performance-Report.pdf', type: 'pdf', size: '2.4 MB', uploaded: '2 hours ago', status: 'Indexed' },
  { id: 2, name: 'agent-architecture-diagram.png', type: 'image', size: '1.1 MB', uploaded: 'Yesterday', status: 'Indexed' },
  { id: 3, name: 'customer-data-export.csv', type: 'spreadsheet', size: '4.8 MB', uploaded: '3 days ago', status: 'Indexed' },
  { id: 4, name: 'rag-pipeline-notes.md', type: 'code', size: '12 KB', uploaded: '5 days ago', status: 'Indexed' },
  { id: 5, name: 'product-spec-v2.pdf', type: 'pdf', size: '890 KB', uploaded: '1 week ago', status: 'Processing' },
  { id: 6, name: 'meeting-transcript-aug.txt', type: 'file', size: '45 KB', uploaded: '1 week ago', status: 'Indexed' },
];

const typeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  pdf: FileText,
  image: FileImage,
  spreadsheet: FileSpreadsheet,
  code: FileCode,
  file: File,
};

const typeColors: Record<string, string> = {
  pdf: 'text-rose-400 bg-rose-500/10',
  image: 'text-violet-400 bg-violet-500/10',
  spreadsheet: 'text-emerald-400 bg-emerald-500/10',
  code: 'text-sky-400 bg-sky-500/10',
  file: 'text-amber-400 bg-amber-500/10',
};

export default function DocumentsPage() {
  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Documents</h1>
          <p className="mt-1 text-sm text-muted-foreground">Upload, index, and manage files for AI-powered search.</p>
        </div>
        <Button className="gap-2 bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">
          <Upload className="h-4 w-4" />
          Upload
        </Button>
      </div>

      {/* Upload zone */}
      <GlassCard hover={false} className="mb-6 border-dashed border-white/10 p-8">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-sky-400/20 bg-sky-400/[0.06]">
            <Upload className="h-6 w-6 text-sky-400" />
          </div>
          <p className="mt-3 text-sm font-medium text-white">Drop files here or click to upload</p>
          <p className="mt-1 text-xs text-muted-foreground">PDF, TXT, MD, CSV, PNG — up to 50 MB</p>
        </div>
      </GlassCard>

      {/* Document list */}
      <div className="space-y-3">
        {sampleDocs.map((doc, i) => {
          const Icon = typeIcons[doc.type] ?? File;
          return (
            <motion.div
              key={doc.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <GlassCard hover className="flex items-center gap-4 p-4">
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 ${typeColors[doc.type]}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="truncate text-sm font-medium text-white">{doc.name}</p>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{doc.size}</span>
                    <span>·</span>
                    <span>{doc.uploaded}</span>
                    <span>·</span>
                    <span className={doc.status === 'Processing' ? 'text-amber-400' : 'text-emerald-400'}>
                      {doc.status}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-white/[0.05] hover:text-white">
                    <Download className="h-4 w-4" />
                  </button>
                  <button className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-white/[0.05] hover:text-white">
                    <MoreVertical className="h-4 w-4" />
                  </button>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>
    </AppShell>
  );
}
