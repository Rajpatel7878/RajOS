"use client";

import {
  Code2,
  Globe,
  Mail,
} from "lucide-react";

export default function SocialLinks() {
  return (
    <div className="mt-10 flex justify-center gap-4">

      <Code2 className="h-6 w-6 text-slate-400 hover:text-cyan-400 transition-colors" />

      <Globe className="h-6 w-6 text-slate-400 hover:text-cyan-400 transition-colors" />

      <Mail className="h-6 w-6 text-slate-400 hover:text-cyan-400 transition-colors" />

    </div>
  );
}
