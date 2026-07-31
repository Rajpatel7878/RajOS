"use client";

import DashboardMockup from "./DashboardMockup";
import AIChatPanel from "./AIChatPanel";
import MemoryPanel from "./MemoryPanel";

export default function WorkspaceSection() {
  return (
    <section
      id="workspace"
      className="mx-auto max-w-7xl px-6 py-24"
    >

      <div className="grid items-center gap-16 lg:grid-cols-2">

        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
            AI WORKSPACE
          </p>

          <h2 className="text-gradient text-4xl font-bold md:text-6xl">
            Your Complete Intelligent Workspace
          </h2>

          <p className="mt-6 text-lg text-slate-400">
            Manage tasks, conversations, notes and AI memory from one powerful dashboard.
          </p>
        </div>


        <div className="relative h-[450px] rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">

          <DashboardMockup />

        </div>

      </div>

      <div className="mt-12 grid gap-8 md:grid-cols-2">
        <AIChatPanel />
        <MemoryPanel />
      </div>

    </section>
  );
}
