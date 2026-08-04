'use client';

import { motion } from 'framer-motion';
import {
  User,
  Mail,
  MapPin,
  Calendar,
  Edit3,
  Award,
  Zap,
  BrainCircuit,
  Bot,
  Activity,
  Sparkles,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

const stats = [
  { label: 'Tasks Completed', value: '5,885', icon: Zap, color: 'text-amber-400' },
  { label: 'Active Agents', value: '6', icon: Bot, color: 'text-cyan-400' },
  { label: 'Memory Items', value: '8,206', icon: BrainCircuit, color: 'text-violet-400' },
  { label: 'Total Interactions', value: '94.5K', icon: Activity, color: 'text-sky-400' },
];

const achievements = [
  { label: 'Power User', desc: '1,000+ AI interactions', icon: Zap, earned: true },
  { label: 'Memory Master', desc: '5,000+ memory items stored', icon: BrainCircuit, earned: true },
  { label: 'Agent Commander', desc: 'Deployed 5+ agents', icon: Bot, earned: true },
  { label: 'Early Adopter', desc: 'Joined during beta', icon: Sparkles, earned: true },
];

export default function ProfilePage() {
  return (
    <AppShell>
      {/* Header card */}
      <GlassCard hover={false} className="mb-6 overflow-hidden p-0">
        <div className="relative">
          <div className="h-32 w-full bg-gradient-to-r from-sky-500/20 via-cyan-500/10 to-violet-500/20" />
          <div className="px-6 pb-6">
            <div className="-mt-12 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div className="flex items-end gap-4">
                <Avatar className="h-24 w-24 border-4 border-background">
                  <AvatarFallback className="bg-gradient-to-br from-sky-500 to-cyan-500 text-2xl font-bold text-white">
                    RJ
                  </AvatarFallback>
                </Avatar>
                <div className="pb-2">
                  <h2 className="text-xl font-bold text-white">Raj Patel</h2>
                  <p className="text-sm text-muted-foreground">Founder & CEO</p>
                </div>
              </div>
              <Button variant="outline" className="gap-2 border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]">
                <Edit3 className="h-4 w-4" />
                Edit Profile
              </Button>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5"><Mail className="h-4 w-4" /> raj@rajos.ai</span>
              <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" /> San Francisco, CA</span>
              <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4" /> Joined Jan 2025</span>
              <Badge variant="outline" className="border-sky-400/30 bg-sky-400/10 text-sky-300">
                <Sparkles className="mr-1 h-3 w-3" /> Pro Plan
              </Badge>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Stats */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
          >
            <GlassCard hover={false} className="p-5">
              <div className="flex items-center justify-between">
                <div className={`flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02] ${stat.color}`}>
                  <stat.icon className="h-5 w-5" />
                </div>
              </div>
              <p className="mt-4 text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Achievements */}
      <GlassCard hover={false} className="p-6">
        <div className="flex items-center gap-2">
          <Award className="h-5 w-5 text-amber-400" />
          <h3 className="font-semibold text-white">Achievements</h3>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {achievements.map((ach, i) => (
            <motion.div
              key={ach.label}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + i * 0.06 }}
              className="flex flex-col items-center rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 text-center"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-400/[0.06]">
                <ach.icon className="h-5 w-5 text-amber-400" />
              </div>
              <p className="mt-3 text-sm font-medium text-white">{ach.label}</p>
              <p className="mt-0.5 text-xs text-muted-foreground">{ach.desc}</p>
            </motion.div>
          ))}
        </div>
      </GlassCard>
    </AppShell>
  );
}
