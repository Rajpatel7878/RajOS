'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Cpu,
  Key,
  Shield,
  Palette,
  Sliders,
  Check,
  Eye,
  EyeOff,
  Sparkles,
  Moon,
  Sun,
  Monitor,
  Bell,
  Globe,
  Zap,
  BrainCircuit,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { llmModels } from '@/lib/data';

const sections = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'models', label: 'AI Models', icon: Cpu },
  { id: 'api-keys', label: 'API Keys', icon: Key },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'appearance', label: 'Appearance', icon: Palette },
  { id: 'preferences', label: 'Preferences', icon: Sliders },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('profile');
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [enabledModels, setEnabledModels] = useState<Record<string, boolean>>({
    gpt4o: true,
    claude35: true,
    gemini15: true,
    claude3op: false,
    llama3405: false,
    mistralL: true,
  });
  const [defaultModel, setDefaultModel] = useState('claude35');

  const toggleKey = (id: string) => setShowKeys((p) => ({ ...p, [id]: !p[id] }));

  return (
    <AppShell>
      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        {/* Section nav */}
        <div className="space-y-1">
          {sections.map((section, i) => (
            <motion.button
              key={section.id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              onClick={() => setActiveSection(section.id)}
              className={cn(
                'flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-all',
                activeSection === section.id
                  ? 'border border-sky-400/20 bg-sky-400/5 text-white'
                  : 'text-muted-foreground hover:bg-white/[0.03] hover:text-white'
              )}
            >
              <section.icon className={cn('h-4 w-4', activeSection === section.id ? 'text-sky-400' : '')} />
              {section.label}
            </motion.button>
          ))}
        </div>

        {/* Content */}
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-6"
        >
          {/* Profile */}
          {activeSection === 'profile' && (
            <>
              <GlassCard hover={false} className="p-6">
                <h3 className="mb-1 font-semibold text-white">Profile</h3>
                <p className="mb-6 text-sm text-muted-foreground">Manage your personal information and avatar.</p>

                <div className="flex items-center gap-6">
                  <div className="relative">
                    <Avatar className="h-20 w-20 border-2 border-sky-400/20">
                      <AvatarFallback className="bg-gradient-to-br from-sky-500 to-cyan-500 text-xl font-bold text-white">
                        RJ
                      </AvatarFallback>
                    </Avatar>
                    <button className="absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full border border-white/10 bg-black/80 text-white">
                      <Sparkles className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-white">Raj Patel</h4>
                    <p className="text-sm text-muted-foreground">raj@rajos.ai</p>
                    <Badge variant="outline" className="mt-2 border-sky-400/30 bg-sky-400/10 text-sky-300">
                      <Sparkles className="mr-1 h-3 w-3" /> Pro Plan
                    </Badge>
                  </div>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label className="text-xs text-muted-foreground">Full Name</Label>
                    <Input defaultValue="Raj Patel" className="mt-1.5 border-white/10 bg-white/[0.02]" />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Email</Label>
                    <Input defaultValue="raj@rajos.ai" className="mt-1.5 border-white/10 bg-white/[0.02]" />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Role</Label>
                    <Input defaultValue="Founder & CEO" className="mt-1.5 border-white/10 bg-white/[0.02]" />
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Timezone</Label>
                    <Input defaultValue="PST (UTC-8)" className="mt-1.5 border-white/10 bg-white/[0.02]" />
                  </div>
                </div>
                <div className="mt-6 flex justify-end gap-3">
                  <Button variant="outline" className="border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]">Cancel</Button>
                  <Button className="bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">Save Changes</Button>
                </div>
              </GlassCard>
            </>
          )}

          {/* AI Models */}
          {activeSection === 'models' && (
            <GlassCard hover={false} className="p-6">
              <h3 className="mb-1 font-semibold text-white">AI Model Configuration</h3>
              <p className="mb-6 text-sm text-muted-foreground">Enable models, set your default, and configure smart routing.</p>

              <div className="space-y-3">
                {llmModels.map((model) => (
                  <div
                    key={model.id}
                    className={cn(
                      'flex items-center gap-4 rounded-xl border p-4 transition-all',
                      enabledModels[model.id]
                        ? 'border-sky-400/20 bg-sky-400/[0.03]'
                        : 'border-white/[0.06] bg-white/[0.02]'
                    )}
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-gradient-to-br from-sky-500/20 to-cyan-500/10">
                      <Cpu className="h-5 w-5 text-sky-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{model.name}</span>
                        <span className="rounded bg-white/5 px-1.5 py-0.5 text-[10px] text-muted-foreground">{model.provider}</span>
                        {defaultModel === model.id && (
                          <Badge variant="outline" className="border-emerald-400/30 bg-emerald-400/10 text-emerald-300 text-[10px]">Default</Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {model.contextWindow} context · ${model.costPerMTok}/MTok · {model.latency} · {model.strengths.join(', ')}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      {enabledModels[model.id] && (
                        <button
                          onClick={() => setDefaultModel(model.id)}
                          className={cn(
                            'rounded-lg border px-3 py-1.5 text-xs font-medium transition-all',
                            defaultModel === model.id
                              ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300'
                              : 'border-white/10 bg-white/[0.02] text-muted-foreground hover:text-white'
                          )}
                        >
                          Set Default
                        </button>
                      )}
                      <Switch
                        checked={enabledModels[model.id]}
                        onCheckedChange={(v) => setEnabledModels((p) => ({ ...p, [model.id]: v }))}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-xl border border-sky-400/20 bg-sky-400/[0.03] p-4">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-sky-400" />
                  <span className="text-sm font-medium text-white">Smart Routing</span>
                  <Switch defaultChecked />
                </div>
                <p className="mt-2 text-xs text-muted-foreground">
                  RajOS automatically routes each request to the best model based on task type, context length, and cost. Fallback activates if a model times out.
                </p>
              </div>
            </GlassCard>
          )}

          {/* API Keys */}
          {activeSection === 'api-keys' && (
            <GlassCard hover={false} className="p-6">
              <h3 className="mb-1 font-semibold text-white">API Keys</h3>
              <p className="mb-6 text-sm text-muted-foreground">Connect your LLM provider accounts. Keys are encrypted and never exposed.</p>

              <div className="space-y-3">
                {[
                  { id: 'openai', name: 'OpenAI', key: 'sk-proj-9f2a...c4e8', connected: true },
                  { id: 'anthropic', name: 'Anthropic', key: 'sk-ant-3b7c...d9f1', connected: true },
                  { id: 'google', name: 'Google AI', key: 'AIzaSyH4k2...mN8pQ', connected: true },
                  { id: 'mistral', name: 'Mistral', key: '—', connected: false },
                ].map((provider) => (
                  <div key={provider.id} className="flex items-center gap-4 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.02]">
                      <Key className="h-5 w-5 text-sky-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-white">{provider.name}</span>
                        {provider.connected ? (
                          <Badge variant="outline" className="border-emerald-400/30 bg-emerald-400/10 text-emerald-300 text-[10px]">
                            <Check className="mr-1 h-2.5 w-2.5" /> Connected
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="border-white/15 bg-white/5 text-muted-foreground text-[10px]">Not connected</Badge>
                        )}
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <code className="font-mono text-xs text-muted-foreground">
                          {showKeys[provider.id] ? provider.key : '••••••••••••••••'}
                        </code>
                        {provider.connected && (
                          <button onClick={() => toggleKey(provider.id)} className="text-muted-foreground hover:text-white">
                            {showKeys[provider.id] ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                          </button>
                        )}
                      </div>
                    </div>
                    <Button size="sm" variant="outline" className="border-white/15 bg-white/[0.03] text-white hover:bg-white/[0.08]">
                      {provider.connected ? 'Update' : 'Connect'}
                    </Button>
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {/* Security */}
          {activeSection === 'security' && (
            <>
              <GlassCard hover={false} className="p-6">
                <h3 className="mb-1 font-semibold text-white">Security</h3>
                <p className="mb-6 text-sm text-muted-foreground">Protect your account and data.</p>

                <div className="space-y-4">
                  {[
                    { label: 'Two-Factor Authentication', desc: 'Require a verification code at sign-in', enabled: true },
                    { label: 'Biometric Lock', desc: 'Lock RajOS with fingerprint or face ID', enabled: true },
                    { label: 'Session Timeout', desc: 'Auto-sign-out after 30 minutes of inactivity', enabled: false },
                    { label: 'Audit Logging', desc: 'Track all AI actions and data access', enabled: true },
                    { label: 'Data Encryption at Rest', desc: 'AES-256 encryption for stored data', enabled: true },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                      <div className="flex items-center gap-3">
                        <Shield className="h-4 w-4 text-sky-400" />
                        <div>
                          <p className="text-sm font-medium text-white">{item.label}</p>
                          <p className="text-xs text-muted-foreground">{item.desc}</p>
                        </div>
                      </div>
                      <Switch defaultChecked={item.enabled} />
                    </div>
                  ))}
                </div>
              </GlassCard>

              <GlassCard hover={false} className="p-6">
                <h3 className="mb-1 font-semibold text-white">Active Sessions</h3>
                <p className="mb-4 text-sm text-muted-foreground">Devices currently signed in to your account.</p>
                <div className="space-y-3">
                  {[
                    { device: 'MacBook Pro · Chrome', location: 'San Francisco, CA', current: true },
                    { device: 'iPhone 15 Pro · Safari', location: 'San Francisco, CA', current: false },
                  ].map((session) => (
                    <div key={session.device} className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                      <div className="flex items-center gap-3">
                        <Monitor className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm font-medium text-white">{session.device}</p>
                          <p className="text-xs text-muted-foreground">{session.location}</p>
                        </div>
                      </div>
                      {session.current ? (
                        <Badge variant="outline" className="border-emerald-400/30 bg-emerald-400/10 text-emerald-300">Current</Badge>
                      ) : (
                        <Button size="sm" variant="ghost" className="text-red-400 hover:bg-red-500/10 hover:text-red-300">Revoke</Button>
                      )}
                    </div>
                  ))}
                </div>
              </GlassCard>
            </>
          )}

          {/* Appearance */}
          {activeSection === 'appearance' && (
            <GlassCard hover={false} className="p-6">
              <h3 className="mb-1 font-semibold text-white">Appearance</h3>
              <p className="mb-6 text-sm text-muted-foreground">Customize how RajOS looks.</p>

              <div>
                <Label className="mb-3 block text-sm text-white">Theme</Label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'dark', label: 'Dark', icon: Moon, active: true },
                    { id: 'light', label: 'Light', icon: Sun, active: false },
                    { id: 'system', label: 'System', icon: Monitor, active: false },
                  ].map((theme) => (
                    <button
                      key={theme.id}
                      className={cn(
                        'flex flex-col items-center gap-2 rounded-xl border p-4 transition-all',
                        theme.active
                          ? 'border-sky-400/30 bg-sky-400/5'
                          : 'border-white/[0.06] bg-white/[0.02] hover:border-white/15'
                      )}
                    >
                      <theme.icon className={cn('h-5 w-5', theme.active ? 'text-sky-400' : 'text-muted-foreground')} />
                      <span className="text-sm font-medium text-white">{theme.label}</span>
                      {theme.active && <Check className="absolute top-2 right-2 h-3.5 w-3.5 text-sky-400" />}
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-6">
                <Label className="mb-3 block text-sm text-white">Accent Color</Label>
                <div className="flex gap-3">
                  {['#38bdf8', '#22d3ee', '#34d399', '#a78bfa', '#fbbf24', '#fb7185'].map((color, i) => (
                    <button
                      key={color}
                      className={cn(
                        'h-10 w-10 rounded-xl border-2 transition-all',
                        i === 0 ? 'border-white scale-110' : 'border-transparent hover:scale-105'
                      )}
                      style={{ background: color }}
                    />
                  ))}
                </div>
              </div>

              <div className="mt-6 space-y-4">
                {[
                  { label: 'Reduced Motion', desc: 'Minimize animations and transitions', enabled: false },
                  { label: 'Glassmorphism Effects', desc: 'Enable frosted glass blur on panels', enabled: true },
                  { label: 'Compact Mode', desc: 'Reduce spacing for more content per screen', enabled: false },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div>
                      <p className="text-sm font-medium text-white">{item.label}</p>
                      <p className="text-xs text-muted-foreground">{item.desc}</p>
                    </div>
                    <Switch defaultChecked={item.enabled} />
                  </div>
                ))}
              </div>
            </GlassCard>
          )}

          {/* Preferences */}
          {activeSection === 'preferences' && (
            <GlassCard hover={false} className="p-6">
              <h3 className="mb-1 font-semibold text-white">Preferences</h3>
              <p className="mb-6 text-sm text-muted-foreground">Configure how your AI operating system behaves.</p>

              <div className="space-y-4">
                {[
                  { label: 'Proactive Suggestions', desc: 'RajOS suggests actions based on your patterns', icon: Sparkles, enabled: true },
                  { label: 'Auto-Save Conversations', desc: 'Automatically store all chat history to memory', icon: BrainCircuit, enabled: true },
                  { label: 'Real-time Agent Monitoring', desc: 'Show live agent activity in the sidebar', icon: Zap, enabled: true },
                  { label: 'Smart Notifications', desc: 'Only notify for high-priority agent events', icon: Bell, enabled: true },
                  { label: 'Auto-Index Uploads', desc: 'Automatically add uploaded files to knowledge base', icon: Globe, enabled: true },
                  { label: 'Memory Retention', desc: 'Keep memories indefinitely (disable for 90-day limit)', icon: BrainCircuit, enabled: true },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
                    <div className="flex items-center gap-3">
                      <item.icon className="h-4 w-4 text-sky-400" />
                      <div>
                        <p className="text-sm font-medium text-white">{item.label}</p>
                        <p className="text-xs text-muted-foreground">{item.desc}</p>
                      </div>
                    </div>
                    <Switch defaultChecked={item.enabled} />
                  </div>
                ))}
              </div>

              <div className="mt-6 flex justify-end">
                <Button className="bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400">Save Preferences</Button>
              </div>
            </GlassCard>
          )}
        </motion.div>
      </div>
    </AppShell>
  );
}
