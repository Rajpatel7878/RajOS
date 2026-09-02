"use client";

import { useState, useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Sidebar, useSidebarState } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";
import { PageTransition } from "@/components/page-transition";
import { GradientMesh } from "@/components/gradient-mesh";
import { Loader2 } from "lucide-react";

const GUEST_FLAG = "rajos_guest";

export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [collapsed, setCollapsed] = useSidebarState();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (sessionStorage.getItem(GUEST_FLAG) === "1") {
        if (cancelled) return;
        setAuthed(true);
        return;
      }
      try {
        const token = localStorage.getItem("token");
        if (cancelled) return;
        if (token) {
          setAuthed(true);
        } else {
          router.replace("/login");
        }
      } catch {
        if (cancelled) return;
        router.replace("/login");
      }
    })();
    return () => { cancelled = true; };
  }, [router]);

  if (!authed) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="relative flex flex-col items-center gap-4">
          {/* Glowing loader */}
          <div className="relative">
            <div className="absolute inset-0 animate-ping rounded-full bg-sky-400/20" />
            <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 to-cyan-500 shadow-2xl shadow-sky-500/40">
              <Loader2 className="h-7 w-7 animate-spin text-white" />
            </div>
          </div>
          <p className="text-sm text-muted-foreground animate-pulse">Loading RajOS...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen bg-background text-foreground overflow-hidden">
      {/* Layered 3D background */}
      <GradientMesh className="pointer-events-none fixed inset-0 z-0" />

      {/* Depth gradient overlay */}
      <div className="pointer-events-none fixed inset-0 z-0 bg-gradient-to-b from-transparent via-transparent to-black/50" />

      {/* Side depth vignette */}
      <div className="pointer-events-none fixed inset-y-0 left-0 z-0 w-32 bg-gradient-to-r from-black/30 to-transparent" />
      <div className="pointer-events-none fixed inset-y-0 right-0 z-0 w-32 bg-gradient-to-l from-black/20 to-transparent" />

      {/* Subtle horizontal light streak */}
      <div
        className="pointer-events-none fixed left-0 right-0 z-0 h-px opacity-30"
        style={{
          top: "30%",
          background: "linear-gradient(90deg, transparent, rgba(56,189,248,0.15), rgba(34,211,238,0.15), transparent)",
        }}
      />

      {/* Sidebar */}
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      {/* Main content */}
      <div className="relative z-10 flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto">
          <PageTransition>
            <div className="mx-auto max-w-[1600px] p-6 lg:p-8">
              {children}
            </div>
          </PageTransition>
        </main>
      </div>
    </div>
  );
}
