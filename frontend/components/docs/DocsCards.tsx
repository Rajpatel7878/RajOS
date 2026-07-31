"use client";

import {
  BookOpen,
  Code2,
  Rocket,
} from "lucide-react";

const docs = [
  {
    icon: BookOpen,
    title: "Getting Started",
    description: "Learn the basics and setup your RajOS workspace.",
  },
  {
    icon: Code2,
    title: "Developer Guide",
    description: "Build integrations and extend RajOS capabilities.",
  },
  {
    icon: Rocket,
    title: "Deployment",
    description: "Deploy and manage your AI workspace easily.",
  },
];

export default function DocsCards() {
  return (
    <>
      {docs.map((doc) => {
        const Icon = doc.icon;

        return (
          <div
            key={doc.title}
            className="glass rounded-3xl p-8 hover-glow transition-all duration-300"
          >

            <Icon className="mb-5 h-10 w-10 text-cyan-400" />

            <h3 className="text-2xl font-bold text-white">
              {doc.title}
            </h3>

            <p className="mt-3 text-slate-400">
              {doc.description}
            </p>

          </div>
        );
      })}
    </>
  );
}
