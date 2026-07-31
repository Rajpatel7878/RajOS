"use client";

export default function GlassCard({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="
        rounded-3xl
        border
        border-white/10
        bg-white/5
        p-6
        backdrop-blur-2xl
        shadow-2xl
        transition-all
        duration-500
        hover:-translate-y-3
        hover:rotate-1
        hover:shadow-cyan-500/20
      "
    >
      {children}
    </div>
  );
}
