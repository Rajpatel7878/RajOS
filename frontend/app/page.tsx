"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Bot,
  BrainCircuit,
  BookOpen,
  Cpu,
  Workflow,
  Sparkles,
  Zap,
  Shield,
  Database,
  Network,
  Layers,
  GitBranch,
  Check,
  Terminal,
  Globe,
  Search,
  Target,
  Lightbulb,
  MessageSquare,
  Orbit,
} from "lucide-react";
import nextDynamic from "next/dynamic";
import { SectionHeading } from "@/components/section-heading";
import { LandingNav } from "@/components/landing-nav";
import { AnimatedCounter } from "@/components/animated-counter";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/glass-card";
import { pricingTiers } from "@/lib/data";

const NeuralBackground = nextDynamic(() => import("@/components/three/neural-background").then((m) => m.NeuralBackground), { ssr: false });
const GradientMesh = nextDynamic(() => import("@/components/gradient-mesh").then((m) => m.GradientMesh), { ssr: false });
const AICore = nextDynamic(() => import("@/components/three/ai-core").then((m) => ({ default: m.AICore })), {
  ssr: false,
  loading: () => <div className="h-72 w-72 rounded-full border border-sky-400/20 bg-sky-500/10 animate-pulse" />,
});

const features = [
  {
    icon: Bot,
    title: "AI Agents",
    tagline: "Autonomous intelligence",
    description:
      "Agents that plan, reason, and execute. They break down complex objectives, choose the right tools, make decisions, and complete multi-step tasks autonomously.",
    points: ["Autonomous planning", "Tool execution", "Decision making"],
    gradient: "sky" as const,
    iconColor: "text-sky-400",
  },
  {
    icon: BrainCircuit,
    title: "Memory Engine",
    tagline: "Never forget a thing",
    description:
      "A persistent memory layer that stores your preferences, projects, goals, and skills. Your AI recalls context across every conversation and agent.",
    points: ["Long-term memory", "Personal intelligence", "Context recall"],
    gradient: "cyan" as const,
    iconColor: "text-cyan-400",
  },
  {
    icon: BookOpen,
    title: "RAG Knowledge System",
    tagline: "Understand your world",
    description:
      "Upload documents and let RajOS build a semantic knowledge base. Vector search retrieves exactly what matters, with source citations on every answer.",
    points: ["Document understanding", "Semantic search", "Knowledge retrieval"],
    gradient: "emerald" as const,
    iconColor: "text-emerald-400",
  },
  {
    icon: Cpu,
    title: "Multi-LLM Engine",
    tagline: "Best model for every task",
    description:
      "Route requests across GPT-4o, Claude, Gemini, and open-source models. Smart routing picks the optimal model, with automatic fallback on failure.",
    points: ["Multiple AI providers", "Smart routing", "Automatic fallback"],
    gradient: "violet" as const,
    iconColor: "text-violet-400",
  },
  {
    icon: Workflow,
    title: "Automation",
    tagline: "Intelligent workflows",
    description:
      "Chain agents, triggers, and actions into reusable workflows. RajOS automates repetitive work and orchestrates complex pipelines across your tools.",
    points: ["Visual workflow builder", "Event triggers", "Pipeline orchestration"],
    gradient: "amber" as const,
    iconColor: "text-amber-400",
  },
  {
    icon: Layers,
    title: "Productivity Intelligence",
    tagline: "Work at the speed of thought",
    description:
      "RajOS learns your patterns and surfaces what matters. Insights, summaries, and proactive suggestions keep you ahead without the busywork.",
    points: ["Smart summaries", "Proactive insights", "Focus protection"],
    gradient: "rose" as const,
    iconColor: "text-rose-400",
  },
];

const technologies = [
  { icon: Cpu, name: "Multi-LLM Orchestration", desc: "GPT-4o, Claude, Gemini, Llama" },
  { icon: Database, name: "Vector Database", desc: "pgvector + HNSW indexing" },
  { icon: Network, name: "Agent Framework", desc: "LangGraph state machines" },
  { icon: GitBranch, name: "RAG Pipeline", desc: "Chunking, embeddings, retrieval" },
  { icon: Shield, name: "Security & Privacy", desc: "Row-level security, encryption" },
  { icon: Globe, name: "Edge Deployment", desc: "Deno edge functions, global CDN" },
];

const stats = [
  { value: 5, suffix: "", label: "AI Specialists" },
  { value: 6, suffix: "", label: "LLM Providers" },
  { value: 8206, suffix: "", label: "Memory Items" },
  { value: 99.9, suffix: "%", label: "Uptime" },
];

export default function LandingPage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 50]);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.7], [1, 0]);

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground">
      {/* 3D Ambient Backdrop */}
      <GradientMesh className="pointer-events-none fixed inset-0 z-0" />
      <NeuralBackground className="pointer-events-none fixed inset-0 z-0 opacity-40" />
      <div className="pointer-events-none fixed inset-0 z-0 bg-gradient-to-b from-transparent via-background/60 to-background" />

      <LandingNav />

      {/* ── Hero Section ── */}
      <section
        ref={heroRef}
        className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 pb-24 pt-20 text-center"
      >
        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="flex flex-col items-center max-w-5xl">
          {/* Pill announcement badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-400/10 px-4 py-1.5 text-xs font-semibold text-sky-300 backdrop-blur-md shadow-[0_0_16px_rgba(56,189,248,0.2)]"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Introducing RajOS 2.0 — The 3D Spatial AI Operating System
          </motion.div>

          {/* 3D Interactive Spatial Stage */}
          <div className="relative mb-6 h-[320px] w-full max-w-[550px] flex items-center justify-center">
            {/* 3D Canvas AI Core */}
            <div className="absolute inset-0 flex items-center justify-center cursor-grab active:cursor-grabbing">
              <AICore className="h-[300px] w-[300px]" />
            </div>

            {/* Orbiting 3D Floating Glass Badges */}
            <motion.div
              animate={{ y: [0, -8, 0], x: [0, 4, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -left-4 top-10 hidden sm:flex items-center gap-2 rounded-2xl border border-sky-400/30 bg-black/65 px-3.5 py-1.5 backdrop-blur-xl shadow-[0_0_20px_rgba(56,189,248,0.2)]"
            >
              <Bot className="h-4 w-4 text-sky-400" />
              <span className="text-xs font-semibold text-white">Atlas Orchestrator</span>
            </motion.div>

            <motion.div
              animate={{ y: [0, 8, 0], x: [0, -5, 0] }}
              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut", delay: 1 }}
              className="absolute -right-4 top-16 hidden sm:flex items-center gap-2 rounded-2xl border border-violet-400/30 bg-black/65 px-3.5 py-1.5 backdrop-blur-xl shadow-[0_0_20px_rgba(167,139,250,0.2)]"
            >
              <BrainCircuit className="h-4 w-4 text-violet-400" />
              <span className="text-xs font-semibold text-white">Persistent Memory</span>
            </motion.div>

            <motion.div
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 2 }}
              className="absolute -left-6 bottom-8 hidden sm:flex items-center gap-2 rounded-2xl border border-emerald-400/30 bg-black/65 px-3.5 py-1.5 backdrop-blur-xl shadow-[0_0_20px_rgba(52,211,153,0.2)]"
            >
              <BookOpen className="h-4 w-4 text-emerald-400" />
              <span className="text-xs font-semibold text-white">RAG Vector Search</span>
            </motion.div>

            <motion.div
              animate={{ y: [0, 7, 0] }}
              transition={{ duration: 5.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
              className="absolute -right-6 bottom-12 hidden sm:flex items-center gap-2 rounded-2xl border border-amber-400/30 bg-black/65 px-3.5 py-1.5 backdrop-blur-xl shadow-[0_0_20px_rgba(251,191,36,0.2)]"
            >
              <Cpu className="h-4 w-4 text-amber-400" />
              <span className="text-xs font-semibold text-white">Multi-LLM Dispatch</span>
            </motion.div>
          </div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="text-balance text-4xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl lg:leading-[1.05]"
          >
            RajOS — Your Personal
            <br />
            <span className="text-gradient-blue">AI Operating System</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="mt-6 max-w-2xl text-pretty text-base sm:text-lg leading-relaxed text-muted-foreground"
          >
            An autonomous spatial workspace that remembers, reasons, and acts. Orchestrate multiple AI agents, query your entire knowledge base in 3D, and automate complex workflows seamlessly.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="mt-10 flex flex-col items-center gap-3 sm:flex-row"
          >
            <Button
              asChild
              size="lg"
              className="group h-12 gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 px-8 text-base font-semibold text-white shadow-xl shadow-sky-500/25 transition-all hover:from-sky-400 hover:to-cyan-400 hover:shadow-sky-500/40"
            >
              <Link href="/login">
                Launch Workspace
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="h-12 gap-2 rounded-xl border-white/15 bg-white/[0.03] px-8 text-base font-semibold text-white backdrop-blur-sm hover:bg-white/[0.08]"
            >
              <Link href="#features">Explore Platform</Link>
            </Button>
          </motion.div>

          {/* ── 3D Perspective App Showcase Stage ── */}
          <motion.div
            initial={{ opacity: 0, y: 40, rotateX: 12 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.9, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="mt-16 w-full rounded-3xl border border-white/15 bg-black/70 p-2 sm:p-4 backdrop-blur-3xl shadow-[0_30px_100px_-20px_rgba(0,0,0,0.9),0_0_50px_rgba(56,189,248,0.15)]"
            style={{ perspective: "1200px" }}
          >
            {/* Top Bar with window controls */}
            <div className="flex items-center justify-between border-b border-white/[0.08] px-4 py-3">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-rose-500/80" />
                <span className="h-3 w-3 rounded-full bg-amber-500/80" />
                <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
                <span className="ml-3 text-xs font-mono text-muted-foreground flex items-center gap-1.5">
                  <Sparkles className="h-3 w-3 text-sky-400" /> RajOS Command Center — Neural Core Online
                </span>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                5 Specialists Live
              </div>
            </div>

            {/* Window Content Preview Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 text-left">
              <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 backdrop-blur-md">
                <div className="flex items-center gap-2 text-xs font-semibold text-sky-400 mb-1.5">
                  <Bot className="h-4 w-4" /> Agent Orchestrator
                </div>
                <div className="text-sm font-bold text-white">Atlas System v2.0</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Autonomous task planning & multi-agent routing across Nova, Sage, Echo, and Pulse.
                </p>
              </div>

              <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 backdrop-blur-md">
                <div className="flex items-center gap-2 text-xs font-semibold text-violet-400 mb-1.5">
                  <BrainCircuit className="h-4 w-4" /> Vector Memory Core
                </div>
                <div className="text-sm font-bold text-white">8,206 Semantic Nodes</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Persistent long-term recall indexed with HNSW embeddings.
                </p>
              </div>

              <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4 backdrop-blur-md">
                <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 mb-1.5">
                  <Zap className="h-4 w-4" /> Real-time Execution
                </div>
                <div className="text-sm font-bold text-white">0.8s Average Latency</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Gemini 3.1 default with multi-provider intelligent fallback.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Stats Bar ── */}
      <section className="relative z-30 border-y border-white/[0.06] bg-black/60 backdrop-blur-xl">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-px px-6 lg:grid-cols-4 lg:px-8">
          {stats.map((s) => (
            <div
              key={s.label}
              className="flex flex-col items-center gap-1 py-8 text-center lg:border-l lg:border-white/[0.06] lg:first:border-l-0"
            >
              <AnimatedCounter
                value={s.value}
                suffix={s.suffix}
                className="text-3xl font-extrabold tracking-tight text-white lg:text-4xl"
              />
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ── 3D Feature Showcase ── */}
      <section id="features" className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <SectionHeading
          eyebrow="Capabilities"
          title={<>Everything an AI OS <span className="text-gradient-blue">should do</span></>}
          description="Six integrated systems working as one. Each is powerful alone — together they form a unified operating system for intelligence."
        />

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <GlassCard
              key={feature.title}
              gradient={feature.gradient}
              delay={i * 0.08}
              className="h-full p-6"
            >
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5 shadow-inner">
                <feature.icon className={`h-6 w-6 ${feature.iconColor}`} />
              </div>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {feature.tagline}
              </div>
              <h3 className="mb-3 text-xl font-bold tracking-tight text-white">
                {feature.title}
              </h3>
              <p className="mb-6 text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
              <ul className="space-y-2 border-t border-white/[0.06] pt-4 text-xs text-muted-foreground">
                {feature.points.map((pt) => (
                  <li key={pt} className="flex items-center gap-2">
                    <Check className="h-3.5 w-3.5 text-sky-400" />
                    {pt}
                  </li>
                ))}
              </ul>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* ── Architecture Stack ── */}
      <section className="relative z-10 border-t border-white/[0.06] bg-black/40 px-6 py-24 backdrop-blur-2xl lg:px-8 lg:py-32">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="Architecture"
            title={<>Engineered for <span className="text-gradient-cyan">scale & reliability</span></>}
            description="Modern, modular infrastructure designed from first principles."
          />

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {technologies.map((tech, i) => (
              <GlassCard key={tech.name} delay={i * 0.05} className="p-6">
                <tech.icon className="mb-4 h-6 w-6 text-sky-400" />
                <h4 className="font-bold text-white text-base">{tech.name}</h4>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{tech.desc}</p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
