"use client";

import {
  Brain,
  FileText,
  Zap,
  ShieldCheck,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Memory",
    description: "RajOS remembers your preferences and improves over time.",
  },
  {
    icon: FileText,
    title: "Smart Notes",
    description: "Create, organize and manage notes with AI assistance.",
  },
  {
    icon: Zap,
    title: "Automation",
    description: "Complete tasks faster with intelligent workflows.",
  },
  {
    icon: ShieldCheck,
    title: "Secure Workspace",
    description: "Your data stays protected inside your personal system.",
  },
];

export default function FeatureCards() {
  return (
    <>
      {features.map((feature) => {
        const Icon = feature.icon;

        return (
          <div
            key={feature.title}
            className="glass hover-glow rounded-2xl p-6 transition-all duration-300 hover:-translate-y-2 hover:border-cyan-400/30"
          >
            <Icon className="mb-4 h-10 w-10 text-cyan-400" />

            <h3 className="mb-2 text-xl font-semibold text-white">
              {feature.title}
            </h3>

            <p className="text-sm text-slate-400">
              {feature.description}
            </p>
          </div>
        );
      })}
    </>
  );
}
