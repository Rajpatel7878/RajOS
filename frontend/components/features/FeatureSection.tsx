"use client";

import FeatureCards from "./FeatureCards";

export default function FeatureSection() {
  return (
    <section
      id="features"
      className="mx-auto max-w-7xl px-6 py-24"
    >
      <div className="text-center">

        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
          FEATURES
        </p>

        <h2 className="text-gradient text-4xl font-bold md:text-6xl">
          Everything You Need In One AI Workspace
        </h2>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          RajOS brings AI, productivity, memory and automation together in a single intelligent platform.
        </p>

      </div>


      <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
        <FeatureCards />
      </div>

    </section>
  );
}
