"use client";

import DocsCards from "./DocsCards";

export default function DocsSection() {
  return (
    <section
      id="docs"
      className="mx-auto max-w-7xl px-6 py-24"
    >

      <div className="text-center">

        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
          DOCUMENTATION
        </p>

        <h2 className="text-gradient text-4xl font-bold md:text-6xl">
          Learn How RajOS Works
        </h2>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          Explore guides, tutorials and resources to get the most from your AI workspace.
        </p>

      </div>


      <div className="mt-16 grid gap-8 md:grid-cols-3">

        <DocsCards />

      </div>


    </section>
  );
}
