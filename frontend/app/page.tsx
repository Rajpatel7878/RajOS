'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import Link from 'next/link';
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
} from 'lucide-react';
import nextDynamic from 'next/dynamic';
import { SectionHeading } from '@/components/section-heading';
import { LandingNav } from '@/components/landing-nav';
import { AnimatedCounter } from '@/components/animated-counter';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/glass-card';
import { OrbitalSystem } from '@/components/orbital-system';
import { pricingTiers } from '@/lib/data';

const NeuralBackground = nextDynamic(() => import('@/components/three/neural-background').then(m => m.NeuralBackground), { ssr: false });
const GradientMesh = nextDynamic(() => import('@/components/gradient-mesh').then(m => m.GradientMesh), { ssr: false });

const features = [
  {
    icon: Bot,
    title: 'AI Agents',
    tagline: 'Autonomous intelligence',
    description:
      'Agents that plan, reason, and execute. They break down complex objectives, choose the right tools, make decisions, and complete multi-step tasks autonomously.',
    points: ['Autonomous planning', 'Tool execution', 'Decision making'],
    accent: 'from-sky-500/20 to-blue-500/5',
    iconColor: 'text-sky-400',
  },
  {
    icon: BrainCircuit,
    title: 'Memory Engine',
    tagline: 'Never forget a thing',
    description:
      'A persistent memory layer that stores your preferences, projects, goals, and skills. Your AI recalls context across every conversation and agent.',
    points: ['Long-term memory', 'Personal intelligence', 'Context recall'],
    accent: 'from-cyan-500/20 to-teal-500/5',
    iconColor: 'text-cyan-400',
  },
  {
    icon: BookOpen,
    title: 'RAG Knowledge System',
    tagline: 'Understand your world',
    description:
      'Upload documents and let RajOS build a semantic knowledge base. Vector search retrieves exactly what matters, with source citations on every answer.',
    points: ['Document understanding', 'Semantic search', 'Knowledge retrieval'],
    accent: 'from-emerald-500/20 to-green-500/5',
    iconColor: 'text-emerald-400',
  },
  {
    icon: Cpu,
    title: 'Multi-LLM Engine',
    tagline: 'Best model for every task',
    description:
      'Route requests across GPT-4o, Claude, Gemini, and open-source models. Smart routing picks the optimal model, with automatic fallback on failure.',
    points: ['Multiple AI providers', 'Smart routing', 'Automatic fallback'],
    accent: 'from-violet-500/20 to-purple-500/5',
    iconColor: 'text-violet-400',
  },
  {
    icon: Workflow,
    title: 'Automation',
    tagline: 'Intelligent workflows',
    description:
      'Chain agents, triggers, and actions into reusable workflows. RajOS automates repetitive work and orchestrates complex pipelines across your tools.',
    points: ['Visual workflow builder', 'Event triggers', 'Pipeline orchestration'],
    accent: 'from-amber-500/20 to-orange-500/5',
    iconColor: 'text-amber-400',
  },
  {
    icon: Layers,
    title: 'Productivity Intelligence',
    tagline: 'Work at the speed of thought',
    description:
      'RajOS learns your patterns and surfaces what matters. Insights, summaries, and proactive suggestions keep you ahead without the busywork.',
    points: ['Smart summaries', 'Proactive insights', 'Focus protection'],
    accent: 'from-rose-500/20 to-pink-500/5',
    iconColor: 'text-rose-400',
  },
];

const flowSteps = [
  { icon: MessageSquare, label: 'User Input', desc: 'You speak, type, or upload' },
  { icon: Bot, label: 'AI Agent', desc: 'Picks up the objective' },
  { icon: BrainCircuit, label: 'Memory', desc: 'Recalls your context' },
  { icon: Search, label: 'Knowledge Retrieval', desc: 'Finds relevant docs' },
  { icon: Cpu, label: 'LLM Reasoning', desc: 'Thinks it through' },
  { icon: Zap, label: 'Action', desc: 'Executes the result' },
];

const technologies = [
  { icon: Cpu, name: 'Multi-LLM Orchestration', desc: 'GPT-4o, Claude, Gemini, Llama' },
  { icon: Database, name: 'Vector Database', desc: 'pgvector + HNSW indexing' },
  { icon: Network, name: 'Agent Framework', desc: 'LangGraph state machines' },
  { icon: GitBranch, name: 'RAG Pipeline', desc: 'Chunking, embeddings, retrieval' },
  { icon: Shield, name: 'Security & Privacy', desc: 'Row-level security, encryption' },
  { icon: Globe, name: 'Edge Deployment', desc: 'Deno edge functions, global CDN' },
];

const stats = [
  { value: 6, suffix: '', label: 'AI Agents' },
  { value: 6, suffix: '', label: 'LLM Providers' },
  { value: 8206, suffix: '', label: 'Memory Items' },
  { value: 99.9, suffix: '%', label: 'Uptime' },
];

export default function LandingPage() {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 60]);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0]);

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-background text-foreground">
      <GradientMesh className="pointer-events-none fixed inset-0 z-0" />
      <NeuralBackground className="pointer-events-none fixed inset-0 z-0 opacity-40" />
      <div className="pointer-events-none fixed inset-0 z-0 bg-gradient-to-b from-transparent via-background/50 to-background" />

      <LandingNav />

      {/* Hero */}
      <section
        ref={heroRef}
        className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 pb-24 pt-16 text-center"
      >
        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="flex flex-col items-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8 inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/5 px-4 py-1.5 text-xs font-medium text-sky-300 backdrop-blur-sm"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Introducing RajOS 1.0 — The AI Operating System
          </motion.div>

          {/* Orbital System */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.2, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="relative mb-6 h-[380px] w-full max-w-[500px]"
          >
            <OrbitalSystem className="absolute inset-0" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="text-balance text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl lg:leading-[1.05]"
          >
            RajOS — Your Personal
            <br />
            <span className="text-gradient-blue">AI Operating System</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="mt-6 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground"
          >
            An intelligent workspace that remembers, reasons, and acts.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="mt-10 flex flex-col items-center gap-3 sm:flex-row"
          >
            <Button
              asChild
              size="lg"
              className="group h-12 gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 px-8 text-base font-semibold text-white shadow-xl shadow-sky-500/25 transition-all hover:from-sky-400 hover:to-cyan-400 hover:shadow-sky-500/40"
            >
              <Link href="/login">
                Launch RajOS
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="outline"
              className="h-12 gap-2 rounded-xl border-white/15 bg-white/[0.03] px-8 text-base font-semibold text-white backdrop-blur-sm hover:bg-white/[0.08]"
            >
              <Link href="/#features">
                Explore Platform
              </Link>
            </Button>
          </motion.div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <div className="flex h-10 w-6 items-start justify-center rounded-full border border-white/20 p-1.5">
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
              className="h-1.5 w-1 rounded-full bg-sky-400"
            />
          </div>
        </motion.div>
      </section>

      {/* Stats bar */}
      <section className="relative z-30 border-y border-white/[0.06] bg-black/50 backdrop-blur-xl">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-px px-6 lg:grid-cols-4 lg:px-8">
          {stats.map((s, i) => (
            <div
              key={s.label}
              className="flex flex-col items-center gap-1 py-8 text-center lg:border-l lg:border-white/[0.06] lg:first:border-l-0"
            >
              <AnimatedCounter
                value={s.value}
                suffix={s.suffix}
                className="text-3xl font-bold tracking-tight text-white lg:text-4xl"
              />
              <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* AI OS Introduction */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <SectionHeading
              align="left"
              eyebrow="The Operating System"
              title={<>Not a chatbot. Not an app.<br />An <span className="text-gradient-blue">operating system</span> for intelligence.</>}
              description="RajOS unifies AI agents, memory, knowledge, and automation into a single coherent system. It does not just answer questions — it remembers your context, retrieves your knowledge, reasons through problems, and takes action on your behalf."
            />
            <div className="mt-8 space-y-4">
              {[
                { icon: Target, title: 'Purpose-built for intelligence', desc: 'Every component designed for reasoning, recall, and autonomous action.' },
                { icon: Lightbulb, title: 'Contextually aware', desc: 'Knows your projects, preferences, and goals across every interaction.' },
                { icon: Terminal, title: 'Built for builders and teams', desc: 'From solo creators to enterprise — scale intelligence without limits.' },
              ].map((item, i) => (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.5, delay: i * 0.1 }}
                  className="flex gap-4"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-sky-400/20 bg-sky-400/10">
                    <item.icon className="h-5 w-5 text-sky-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{item.title}</h4>
                    <p className="mt-0.5 text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Terminal mockup */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-sky-500/10 to-cyan-500/5 blur-2xl" />
            <GlassCard hover={false} className="overflow-hidden p-0">
              <div className="flex items-center gap-2 border-b border-white/[0.06] px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-500/60" />
                  <div className="h-3 w-3 rounded-full bg-amber-500/60" />
                  <div className="h-3 w-3 rounded-full bg-emerald-500/60" />
                </div>
                <span className="ml-2 text-xs font-mono text-muted-foreground">rajos — agent:atlas</span>
              </div>
              <div className="space-y-3 p-5 font-mono text-sm">
                <div className="text-muted-foreground">
                  <span className="text-sky-400">user</span> {'>'} Plan a launch campaign for Project Aurora
                </div>
                <div className="text-cyan-300">
                  <span className="text-emerald-400">atlas</span> {'>'} Analyzing objective...
                </div>
                <div className="ml-4 space-y-1.5 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2"><Check className="h-3 w-3 text-emerald-400" /> Retrieved 14 knowledge docs</div>
                  <div className="flex items-center gap-2"><Check className="h-3 w-3 text-emerald-400" /> Recalled 3 memory items</div>
                  <div className="flex items-center gap-2"><Check className="h-3 w-3 text-emerald-400" /> Selected GPT-4o (reasoning)</div>
                  <div className="flex items-center gap-2 text-sky-400"><span className="h-3 w-3 animate-pulse rounded-full bg-sky-400" /> Synthesizing 7-step plan...</div>
                </div>
                <div className="text-white/80">
                  Plan ready. 7 steps, 3 agents, est. 2h execution.
                </div>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </section>

      {/* Feature Showcase */}
      <section id="features" className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <SectionHeading
          eyebrow="Capabilities"
          title={<>Everything an AI OS <span className="text-gradient-blue">should do</span></>}
          description="Six integrated systems working as one. Each is powerful alone — together they form an operating system for intelligence."
        />

        <div className="mt-16 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <GlassCard key={feature.title} delay={i * 0.08} className="h-full p-6">
              <div className={`mb-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-gradient-to-br ${feature.accent}`}>
                <feature.icon className={`h-6 w-6 ${feature.iconColor}`} />
              </div>
              <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {feature.tagline}
              </div>
              <h3 className="text-xl font-bold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
              <ul className="mt-4 space-y-2">
                {feature.points.map((point) => (
                  <li key={point} className="flex items-center gap-2 text-sm text-white/70">
                    <Check className="h-4 w-4 shrink-0 text-sky-400" />
                    {point}
                  </li>
                ))}
              </ul>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <SectionHeading
          eyebrow="Architecture"
          title={<>How <span className="text-gradient-blue">RajOS</span> thinks</>}
          description="Every interaction flows through a six-stage intelligence pipeline — from your input to autonomous action."
        />

        <div className="mt-16">
          {/* Desktop flow */}
          <div className="hidden lg:flex items-center justify-between gap-2">
            {flowSteps.map((step, i) => (
              <div key={step.label} className="flex flex-1 items-center">
                <motion.div
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{ duration: 0.5, delay: i * 0.12 }}
                  className="group relative flex flex-1 flex-col items-center gap-3"
                >
                  <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl border border-white/10 bg-gradient-to-b from-white/[0.06] to-white/[0.01] backdrop-blur-xl transition-all group-hover:border-sky-400/30 group-hover:shadow-lg group-hover:shadow-sky-500/10">
                    <step.icon className="h-7 w-7 text-sky-400" />
                    <div className="absolute inset-0 rounded-2xl bg-sky-500/0 transition-colors group-hover:bg-sky-500/5" />
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-semibold text-white">{step.label}</div>
                    <div className="mt-0.5 text-xs text-muted-foreground">{step.desc}</div>
                  </div>
                  <span className="absolute -top-2 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-sky-400/10 text-[10px] font-bold text-sky-400">
                    {i + 1}
                  </span>
                </motion.div>
                {i < flowSteps.length - 1 && (
                  <motion.div
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: 1 }}
                    viewport={{ once: true, margin: '-60px' }}
                    transition={{ duration: 0.4, delay: i * 0.12 + 0.3 }}
                    className="mx-1 h-px w-8 origin-left bg-gradient-to-r from-sky-400/40 to-cyan-400/40"
                  />
                )}
              </div>
            ))}
          </div>

          {/* Mobile flow */}
          <div className="space-y-3 lg:hidden">
            {flowSteps.map((step, i) => (
              <motion.div
                key={step.label}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="flex items-center gap-4"
              >
                <div className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03]">
                  <step.icon className="h-5 w-5 text-sky-400" />
                  <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-sky-400/20 text-[9px] font-bold text-sky-400">
                    {i + 1}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">{step.label}</div>
                  <div className="text-xs text-muted-foreground">{step.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology */}
      <section id="technology" className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <SectionHeading
          eyebrow="Under the Hood"
          title={<>Enterprise-grade <span className="text-gradient-blue">technology</span></>}
          description="Built on a modern, secure, and scalable stack. Every component engineered for production reliability."
        />

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {technologies.map((tech, i) => (
            <motion.div
              key={tech.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="group flex items-center gap-4 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5 backdrop-blur-sm transition-all hover:border-sky-400/20 hover:bg-white/[0.04]"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-gradient-to-b from-white/[0.06] to-transparent">
                <tech.icon className="h-5 w-5 text-sky-400" />
              </div>
              <div>
                <h4 className="font-semibold text-white">{tech.name}</h4>
                <p className="text-sm text-muted-foreground">{tech.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Pricing Preview */}
      <section id="pricing" className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <SectionHeading
          eyebrow="Pricing"
          title={<>Start free. <span className="text-gradient-blue">Scale infinitely.</span></>}
          description="From exploration to enterprise — RajOS grows with your intelligence needs."
        />

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {pricingTiers.map((tier, i) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`relative rounded-2xl border p-6 backdrop-blur-xl transition-all ${
                tier.highlighted
                  ? 'border-sky-400/30 bg-gradient-to-b from-sky-500/[0.08] to-cyan-500/[0.02] shadow-2xl shadow-sky-500/10 lg:-translate-y-4 lg:scale-[1.03]'
                  : 'border-white/[0.08] bg-white/[0.02] hover:border-white/15'
              }`}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-sky-500 to-cyan-500 px-3 py-1 text-xs font-semibold text-white shadow-lg shadow-sky-500/30">
                    <Sparkles className="h-3 w-3" />
                    Most Popular
                  </span>
                </div>
              )}
              <h3 className="text-lg font-bold text-white">{tier.name}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{tier.tagline}</p>
              <div className="mt-5 flex items-baseline gap-1">
                <span className="text-4xl font-bold tracking-tight text-white">{tier.price}</span>
                <span className="text-sm text-muted-foreground">{tier.period}</span>
              </div>
              <Button
                asChild
                className={`mt-6 w-full rounded-xl ${
                  tier.highlighted
                    ? 'bg-gradient-to-r from-sky-500 to-cyan-500 text-white shadow-lg shadow-sky-500/20 hover:from-sky-400 hover:to-cyan-400'
                    : 'border border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]'
                }`}
                variant={tier.highlighted ? 'default' : 'outline'}
              >
                <Link href="/dashboard">{tier.cta}</Link>
              </Button>
              <ul className="mt-6 space-y-3">
                {tier.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm text-white/70">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-sky-400" />
                    {f}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 py-24 lg:px-8 lg:py-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          className="relative overflow-hidden rounded-3xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-white/[0.01] p-12 text-center backdrop-blur-xl lg:p-20"
        >
          <div className="pointer-events-none absolute -top-1/2 left-1/2 h-full w-2/3 -translate-x-1/2 rounded-full bg-sky-500/15 blur-[120px]" />
          <div className="relative">
            <h2 className="mx-auto max-w-2xl text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl lg:text-5xl lg:leading-[1.1]">
              The future of computing is an <span className="text-gradient-blue">operating system that thinks.</span>
            </h2>
            <p className="mx-auto mt-5 max-w-xl text-pretty text-lg text-muted-foreground">
              Launch RajOS and give your work a memory, a mind, and the ability to act.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button
                asChild
                size="lg"
                className="group h-12 gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 px-8 text-base font-semibold text-white shadow-xl shadow-sky-500/25 hover:from-sky-400 hover:to-cyan-400"
              >
                <Link href="/dashboard">
                  Launch RajOS
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="h-12 rounded-xl border-white/15 bg-white/[0.03] px-8 text-base font-semibold text-white hover:bg-white/[0.08]"
              >
                <Link href="/chat">Try AI Chat</Link>
              </Button>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.06] bg-black/30 backdrop-blur-sm">
        <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
          <div className="grid gap-12 lg:grid-cols-5">
            <div className="lg:col-span-2">
              <Link href="/" className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <span className="text-lg font-bold text-white">RajOS</span>
              </Link>
              <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted-foreground">
                The personal AI operating system that remembers, reasons, and acts. Built for the next era of intelligent computing.
              </p>
              <div className="mt-6 flex gap-3">
                {['Twitter', 'GitHub', 'Discord'].map((s) => (
                  <div key={s} className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/[0.02] text-xs font-medium text-muted-foreground transition-colors hover:border-sky-400/20 hover:text-sky-400">
                    {s[0]}
                  </div>
                ))}
              </div>
            </div>
            {[
              { title: 'Platform', links: ['AI Agents', 'Memory Engine', 'Knowledge Base', 'Multi-LLM', 'Automation'] },
              { title: 'Company', links: ['About', 'Blog', 'Careers', 'Press', 'Contact'] },
              { title: 'Resources', links: ['Documentation', 'API Reference', 'Guides', 'Community', 'Status'] },
            ].map((col) => (
              <div key={col.title}>
                <h4 className="text-sm font-semibold text-white">{col.title}</h4>
                <ul className="mt-4 space-y-3">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#" className="text-sm text-muted-foreground transition-colors hover:text-sky-400">
                        {link}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/[0.06] pt-8 sm:flex-row">
            <p className="text-xs text-muted-foreground">
              © 2025 RajOS. All rights reserved. Built for the future of intelligence.
            </p>
            <div className="flex gap-6 text-xs text-muted-foreground">
              <a href="#" className="hover:text-white">Privacy</a>
              <a href="#" className="hover:text-white">Terms</a>
              <a href="#" className="hover:text-white">Security</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
