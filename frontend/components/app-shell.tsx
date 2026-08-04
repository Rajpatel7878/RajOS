'use client';

import { useState, useEffect, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar, useSidebarState } from '@/components/sidebar';
import { Topbar } from '@/components/topbar';
import { PageTransition } from '@/components/page-transition';
import { GradientMesh } from '@/components/gradient-mesh';
import { getSupabase } from '@/lib/supabase-client';
import { Loader2 } from 'lucide-react';

const GUEST_FLAG = 'rajos_guest';

export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [collapsed, setCollapsed] = useSidebarState();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (sessionStorage.getItem(GUEST_FLAG) === '1') {
        if (cancelled) return;
        setAuthed(true);
        return;
      }
      try {
        const supabase = getSupabase();
        const { data } = await supabase.auth.getSession();
        if (cancelled) return;
        if (data.session) {
          setAuthed(true);
        } else {
          router.replace('/login');
        }
      } catch {
        if (cancelled) return;
        router.replace('/login');
      }
    })();
    return () => { cancelled = true; };
  }, [router]);

  if (!authed) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-sky-400" />
      </div>
    );
  }

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
