"use client";

import {
  LayoutDashboard,
  CheckCircle,
  FileText,
  Brain,
} from "lucide-react";

export default function DashboardMockup() {
  return (
    <div className="relative h-full rounded-3xl border border-white/10 animate-float bg-black/30 p-6 shadow-2xl">

      <div className="flex items-center gap-3 border-b border-white/10 pb-4">
        <LayoutDashboard className="h-6 w-6 text-cyan-400" />

        <span className="font-semibold text-white">
          RajOS Dashboard
        </span>
      </div>


      <div className="mt-6 grid gap-4">

        <div className="rounded-xl bg-white/5 p-4">
          <div className="flex items-center gap-3">
            <Brain className="text-violet-400" />
            <span className="text-white">
              AI Memory Active
            </span>
          </div>
        </div>


        <div className="rounded-xl bg-white/5 p-4">
          <div className="flex items-center gap-3">
            <FileText className="text-cyan-400" />
            <span className="text-white">
              Smart Notes
            </span>
          </div>
        </div>


        <div className="rounded-xl bg-white/5 p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-green-400" />
            <span className="text-white">
              Tasks Completed
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
