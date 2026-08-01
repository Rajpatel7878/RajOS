'use client';

import { useState, useEffect, type ReactNode } from 'react';
import { Sidebar, useSidebarState } from '@/components/sidebar';
import { Topbar } from '@/components/topbar';
import { PageTransition } from '@/components/page-transition';
import { GradientMesh } from '@/components/gradient-mesh';

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useSidebarState();

  return (
    <div className="relative flex min-h-screen bg-background text-foreground">
      <GradientMesh className="pointer-events-none fixed inset-0 z-0" />
      <div className="pointer-events-none fixed inset-0 z-0 bg-gradient-to-b from-transparent via-transparent to-black/40" />

      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      <div className="relative z-10 flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <PageTransition>
            <div className="mx-auto max-w-[1600px] p-6 lg:p-8">{children}</div>
          </PageTransition>
        </main>
      </div>
    </div>
  );
}
