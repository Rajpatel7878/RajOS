'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Paperclip,
  Mic,
  Sparkles,
  Bot,
  BrainCircuit,
  BookOpen,
  ChevronDown,
  Plus,
  Search,
  MessageSquare,
  Zap,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  User,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { AppShell } from '@/components/app-shell';
import { GlassCard } from '@/components/glass-card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { conversations, llmModels, agents } from '@/lib/data';
import type { ChatMessage } from '@/lib/types';
import { sendMessage } from "@/services/api/chat";
import { getHistory } from "@/services/api/history";
import { createTask } from "@/services/api/tasks";
import { DailyRoutineCreator } from "@/components/daily-routine-creator";
import { Dumbbell, Check } from "lucide-react";

const suggestionPrompts = [
  { icon: 'Dumbbell', text: 'Create my daily 50 pushups workout routine' },
  { icon: 'BookOpen', text: 'Schedule a 2-hour focused study block' },
  { icon: 'Zap', text: 'Generate daily routine & productivity habits' },
  { icon: 'BrainCircuit', text: 'Plan today\'s top 3 priority objectives' },
];

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  Dumbbell,
  BookOpen,
  Zap,
  BrainCircuit,
  Bot,
};

export default function ChatPage() {
  const [selectedModel, setSelectedModel] = useState(llmModels[1]);
  const [selectedAgent, setSelectedAgent] = useState(agents[0]);
  const [showModelMenu, setShowModelMenu] = useState(false);
  const [showAgentMenu, setShowAgentMenu] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>(conversations[0].messages);
  const [isTyping, setIsTyping] = useState(false);
  const [activeConv, setActiveConv] = useState<string | number>(conversations[0].id);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [showRoutineModal, setShowRoutineModal] = useState(false);
  const [history, setHistory] = useState<
    {
      conversation_id: number;
      title: string;
      messages: { role: 'user' | 'assistant'; content: string }[];
    }[]
  >([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive or while typing
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const loadHistory = async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const data = await getHistory();
      setHistory(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load chat history';
      console.error('Failed to load chat history:', err);
      setHistoryError(message);
      return [];
    } finally {
      setHistoryLoading(false);
    }
  };

  // Load chat history once on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const handleNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    setActiveConv(0);
    setInput('');
    setIsTyping(false);
  };

  const handleSelectConversation = (id: number) => {
    const conversation = history.find(
      (item) => item.conversation_id === id
    );

    if (!conversation) return;

    setConversationId(id);
    setActiveConv(id);

    const restoredMessages: ChatMessage[] = conversation.messages.map(
      (msg, index) => ({
        id: `history-${id}-${index}`,
        role: msg.role,
        content: msg.content,
        timestamp: '',
      })
    );

    setMessages(restoredMessages);
    setInput('');
  };

  const handleSend = async () => {
    const message = input.trim();
    if (!message || isTyping) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
      }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      // Pass selected agent ID to backend
      const data = await sendMessage(message, conversationId, selectedAgent.id);

      // Use the agent name that actually responded (from backend routing)
      const respondingAgentName = data.agent_name ?? selectedAgent.name;

      const aiMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: data.response ?? (data as any).message ?? (data as any).content ?? 'No response received from AI.',
        timestamp: new Date().toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
        }),
        model: data.model ?? selectedModel.name,
        agent: respondingAgentName,
        sources: Array.isArray(data.sources)
          ? data.sources.map((s: any) =>
              typeof s === 'string' ? { title: s, snippet: s } : s
            )
          : [],
        memoryUsed: data.memory_used ?? [],
        suggestedTasks: (data as any).suggested_tasks ?? [],
      };

      setMessages((prev) => [...prev, aiMsg]);

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      // Refresh history after new message
      loadHistory();
    } catch (error) {
      console.error('Chat error:', error);

      const errorMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content:
          error instanceof Error
            ? `Sorry, I couldn't process your request: ${error.message}`
            : 'Sorry, I could not connect to the AI backend.',
        timestamp: new Date().toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
        }),
      };

      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <AppShell>
      <div className="flex h-full min-h-0 gap-6">
        {/* Conversation history sidebar */}
        <div className="hidden w-72 shrink-0 flex-col lg:flex h-full min-h-0">
          <GlassCard hover={false} className="flex h-full min-h-0 flex-1 flex-col p-0">
            <div className="p-4 border-b border-white/[0.06]">
              <Button
                onClick={handleNewConversation}
                className="w-full gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-white hover:from-sky-400 hover:to-cyan-400"
              >
                <Plus className="h-4 w-4" />
                New Conversation
              </Button>
            </div>
            <div className="px-4 py-3">
              <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.02] px-3 py-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <input
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search chats..."
                  className="w-full bg-transparent text-sm text-white placeholder:text-muted-foreground focus:outline-none"
                />
              </div>
            </div>
            <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-1 no-scrollbar">
              <div className="flex items-center justify-between px-3 py-2">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60">
                  Recent
                </p>
                {historyLoading && (
                  <Loader2 className="h-3 w-3 animate-spin text-sky-400" />
                )}
              </div>

              {historyError && (
                <div className="mx-2 my-2 rounded-lg border border-red-500/20 bg-red-500/10 p-2.5 text-xs text-red-300">
                  <div className="flex items-center gap-1.5 font-medium">
                    <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                    <span>Failed to load history</span>
                  </div>
                  <p className="mt-1 line-clamp-2 text-[11px] text-red-300/80">
                    {historyError}
                  </p>
                  <button
                    onClick={() => loadHistory()}
                    className="mt-2 inline-flex items-center gap-1 rounded border border-red-400/30 px-2 py-0.5 text-[10px] text-red-200 hover:bg-red-400/10 transition-colors"
                  >
                    <RefreshCw className="h-2.5 w-2.5" />
                    Retry
                  </button>
                </div>
              )}

              {historyLoading && history.length === 0 ? (
                <div className="space-y-2 px-2 py-1">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="h-14 w-full animate-pulse rounded-xl bg-white/[0.04]"
                    />
                  ))}
                </div>
              ) : history.length === 0 && !historyError ? (
                <div className="px-3 py-6 text-center text-xs text-muted-foreground">
                  No conversations yet. Start a new chat!
                </div>
              ) : (
                history
                  .filter((conv) =>
                    conv.title.toLowerCase().includes(searchTerm.toLowerCase())
                  )
                  .map((conv) => {
                    const lastMessage =
                      conv.messages[conv.messages.length - 1]?.content ??
                      'No messages yet';

                    return (
                      <button
                        key={conv.conversation_id}
                        onClick={() => handleSelectConversation(conv.conversation_id)}
                        className={cn(
                          'group flex w-full flex-col gap-1 rounded-xl px-3 py-2.5 text-left transition-colors',
                          activeConv === conv.conversation_id
                            ? 'border border-sky-400/20 bg-sky-400/5'
                            : 'hover:bg-white/[0.03]'
                        )}
                      >
                        <div className="flex items-center gap-2">
                          <MessageSquare
                            className={cn(
                              'h-3.5 w-3.5 shrink-0',
                              activeConv === conv.conversation_id
                                ? 'text-sky-400'
                                : 'text-muted-foreground'
                            )}
                          />
                          <span className="truncate text-sm font-medium text-white">
                            {conv.title}
                          </span>
                        </div>

                        <span className="truncate pl-5 text-xs text-muted-foreground">
                          {lastMessage}
                        </span>

                        <div className="flex items-center gap-2 pl-5">
                          <span className="text-[10px] text-muted-foreground">
                            Conversation #{conv.conversation_id}
                          </span>
                        </div>
                      </button>
                    );
                  })
              )}
            </div>
          </GlassCard>
        </div>

        {/* Chat area */}
        <div className="flex min-h-0 min-w-0 flex-1 flex-col h-full">
          <GlassCard hover={false} className="flex h-full min-h-0 flex-1 flex-col overflow-hidden p-0">
            {/* Chat header — model + agent selectors */}
            <div className="flex items-center gap-3 border-b border-white/[0.06] p-4">
              {/* Model selector */}
              <div className="relative">
                <button
                  onClick={() => { setShowModelMenu(!showModelMenu); setShowAgentMenu(false); }}
                  className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-white/[0.06]"
                >
                  <CpuIcon />
                  {selectedModel.name}
                  <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
                </button>
                <AnimatePresence>
                  {showModelMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: 8, scale: 0.97 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.97 }}
                      transition={{ duration: 0.15 }}
                      className="absolute left-0 top-full z-50 mt-2 w-80 rounded-xl border border-white/10 bg-black/90 p-2 backdrop-blur-2xl shadow-2xl"
                    >
                      {llmModels.map((m) => (
                        <button
                          key={m.id}
                          onClick={() => { setSelectedModel(m); setShowModelMenu(false); }}
                          className={cn(
                            'flex w-full items-center gap-3 rounded-lg p-3 text-left transition-colors hover:bg-white/5',
                            selectedModel.id === m.id && 'bg-white/5'
                          )}
                        >
                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-500/20 to-cyan-500/10">
                            <Sparkles className="h-4 w-4 text-sky-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-white">{m.name}</span>
                              <span className="rounded bg-white/5 px-1.5 py-0.5 text-[10px] text-muted-foreground">{m.latency}</span>
                            </div>
                            <p className="text-xs text-muted-foreground">{m.provider} · {m.contextWindow} context</p>
                          </div>
                          {selectedModel.id === m.id && <div className="h-2 w-2 rounded-full bg-sky-400" />}
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Agent selector */}
              <div className="relative">
                <button
                  onClick={() => { setShowAgentMenu(!showAgentMenu); setShowModelMenu(false); }}
                  className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-white/[0.06]"
                >
                  <div className="flex h-5 w-5 items-center justify-center rounded bg-gradient-to-br from-cyan-400 to-sky-500 text-[10px] font-bold text-white">
                    {selectedAgent.avatar}
                  </div>
                  {selectedAgent.name}
                  <ChevronDown className="h-3.5 w-3.5 text-muted-foreground" />
                </button>
                <AnimatePresence>
                  {showAgentMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: 8, scale: 0.97 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.97 }}
                      transition={{ duration: 0.15 }}
                      className="absolute left-0 top-full z-50 mt-2 w-72 rounded-xl border border-white/10 bg-black/90 p-2 backdrop-blur-2xl shadow-2xl"
                    >
                      {agents.filter(a => a.status !== 'Paused').map((a) => (
                        <button
                          key={a.id}
                          onClick={() => { setSelectedAgent(a); setShowAgentMenu(false); }}
                          className={cn(
                            'flex w-full items-center gap-3 rounded-lg p-3 text-left transition-colors hover:bg-white/5',
                            selectedAgent.id === a.id && 'bg-white/5'
                          )}
                        >
                          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-sky-500 text-xs font-bold text-white">
                            {a.avatar}
                          </div>
                          <div className="flex-1 min-w-0">
                            <span className="text-sm font-medium text-white">{a.name}</span>
                            <p className="truncate text-xs text-muted-foreground">{a.description}</p>
                          </div>
                          <span className={cn(
                            'h-2 w-2 rounded-full',
                            a.status === 'Active' || a.status === 'Executing' ? 'bg-emerald-400' : a.status === 'Planning' ? 'bg-amber-400' : 'bg-white/20'
                          )} />
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              <div className="ml-auto flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowRoutineModal(true)}
                  className="gap-1.5 rounded-xl border-sky-400/40 bg-sky-400/10 px-3 py-1.5 text-xs font-semibold text-sky-300 hover:bg-sky-400/20 hover:text-white transition-all shadow-[0_0_12px_rgba(56,189,248,0.2)]"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  ⚡ Daily Routines (Pushups & Study)
                </Button>

                <div className="hidden lg:flex items-center gap-2 text-xs text-muted-foreground ml-2">
                  <BrainCircuit className="h-4 w-4 text-violet-400" />
                  <span>3 memories</span>
                  <BookOpen className="h-4 w-4 text-emerald-400 ml-1" />
                  <span>14 docs</span>
                </div>
              </div>
            </div>

            {/* Daily Routine Creator Modal */}
            <DailyRoutineCreator
              isOpen={showRoutineModal}
              onClose={() => setShowRoutineModal(false)}
            />

            {/* Messages */}
            <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6 no-scrollbar">
              {messages.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <div className="relative mb-6">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500/20 to-cyan-500/10 shadow-lg shadow-sky-500/20">
                      <Sparkles className="h-8 w-8 text-sky-400" />
                    </div>
                    <div className="absolute inset-0 -z-10 rounded-2xl bg-sky-500/20 blur-2xl" />
                  </div>
                  <h3 className="text-xl font-bold text-white">How can I help you today?</h3>
                  <p className="mt-2 text-sm text-muted-foreground max-w-md">
                    Ask anything. {selectedAgent.name} is ready with your long-term memory and knowledge base.
                  </p>
                  <div className="mt-8 grid w-full max-w-xl grid-cols-1 gap-3 sm:grid-cols-2">
                    {suggestionPrompts.map((p) => {
                      const Icon = iconMap[p.icon] ?? Sparkles;
                      return (
                        <button
                          key={p.text}
                          onClick={() => setInput(p.text)}
                          className="group flex items-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.02] p-3.5 text-left transition-all hover:border-sky-400/30 hover:bg-white/[0.05] hover:shadow-[0_8px_20px_rgba(56,189,248,0.1)]"
                        >
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sky-500/10 text-sky-400 group-hover:scale-110 transition-transform">
                            <Icon className="h-4 w-4" />
                          </div>
                          <span className="text-xs sm:text-sm text-white font-medium">{p.text}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="mx-auto max-w-3xl space-y-6">
                  {messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} agentName={selectedAgent.name} />
                  ))}
                  {isTyping && <TypingIndicator agentName={selectedAgent.name} />}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* ── Typing Chat Input Bar (Permanently Set at Bottom) ── */}
            <div className="shrink-0 border-t border-white/[0.08] bg-black/70 p-3 sm:p-4 backdrop-blur-2xl z-20">
              <div className="mx-auto max-w-3xl">
                {/* Context Pills & Quick Prompts Bar */}
                <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-[11px] font-medium text-muted-foreground">Active Context:</span>
                    <span className="inline-flex items-center gap-1 rounded-full border border-sky-400/30 bg-sky-400/10 px-2 py-0.5 text-[11px] font-medium text-sky-300">
                      <Bot className="h-3 w-3" /> {selectedAgent.name}
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full border border-violet-400/30 bg-violet-400/10 px-2 py-0.5 text-[11px] font-medium text-violet-300">
                      <BrainCircuit className="h-3 w-3" /> Memory Active
                    </span>
                    <span className="hidden sm:inline-flex items-center gap-1 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
                      <BookOpen className="h-3 w-3" /> 14 Docs
                    </span>
                  </div>

                  {/* Quick action shortcuts */}
                  <div className="hidden sm:flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => setInput("Schedule my daily 50 pushups routine today")}
                      className="rounded-lg border border-white/10 bg-white/[0.03] px-2 py-0.5 text-[10px] text-muted-foreground hover:border-sky-400/30 hover:text-white transition-colors"
                    >
                      ⚡ Pushups
                    </button>
                    <button
                      type="button"
                      onClick={() => setInput("Plan a 2-hour focused deep study block")}
                      className="rounded-lg border border-white/10 bg-white/[0.03] px-2 py-0.5 text-[10px] text-muted-foreground hover:border-sky-400/30 hover:text-white transition-colors"
                    >
                      📚 Study
                    </button>
                  </div>
                </div>

                {/* 3D Elevated Typing Box */}
                <div className="relative flex items-end gap-2 rounded-2xl border border-white/[0.12] bg-gradient-to-b from-white/[0.05] to-black/60 p-2.5 shadow-[0_4px_24px_rgba(0,0,0,0.5)] transition-all duration-200 focus-within:border-sky-400/50 focus-within:bg-black/80 focus-within:shadow-[0_0_25px_rgba(56,189,248,0.25)]">
                  <button
                    type="button"
                    title="Attach file"
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-muted-foreground transition-all hover:bg-white/[0.08] hover:text-sky-300 active:scale-95"
                  >
                    <Paperclip className="h-4 w-4" />
                  </button>

                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    placeholder={`Message ${selectedAgent.name} (Enter to send, Shift+Enter for new line)...`}
                    rows={1}
                    className="min-h-[40px] max-h-36 flex-1 resize-none bg-transparent py-2 text-sm text-white placeholder:text-muted-foreground/70 focus:outline-none leading-relaxed"
                  />

                  <button
                    type="button"
                    title="Voice input"
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-muted-foreground transition-all hover:bg-white/[0.08] hover:text-cyan-300 active:scale-95"
                  >
                    <Mic className="h-4 w-4" />
                  </button>

                  <Button
                    onClick={handleSend}
                    disabled={!input.trim() || isTyping}
                    className={cn(
                      "h-9 w-9 shrink-0 rounded-xl p-0 text-white transition-all duration-200 shadow-md",
                      input.trim() && !isTyping
                        ? "bg-gradient-to-r from-sky-500 to-cyan-400 hover:from-sky-400 hover:to-cyan-300 shadow-sky-500/30 hover:scale-105 active:scale-95"
                        : "bg-white/10 text-muted-foreground opacity-50 cursor-not-allowed"
                    )}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                <div className="mt-2 flex items-center justify-between px-1 text-[11px] text-muted-foreground/70">
                  <span>Press <kbd className="rounded border border-white/10 bg-white/5 px-1.5 py-0.5 font-mono text-[10px] text-white/90">Enter ↵</kbd> to send</span>
                  <span>RajOS AI Neural Engine · Continuous Context</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </AppShell>
  );
}

function CpuIcon() {
  return <Sparkles className="h-4 w-4 text-sky-400" />;
}

function MessageBubble({ message, agentName }: { message: ChatMessage; agentName: string }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex justify-end gap-3"
      >
        <div className="max-w-[80%]">
          <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-sky-500/15 to-cyan-500/5 border border-sky-400/20 px-4 py-3">
            <p className="text-sm leading-relaxed text-white">{message.content}</p>
          </div>
          <div className="mt-1 flex justify-end">
            <span className="text-xs text-muted-foreground">{message.timestamp}</span>
          </div>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03]">
          <User className="h-4 w-4 text-muted-foreground" />
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex gap-3"
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-sky-500 text-xs font-bold text-white">
        {agentName[0]}
      </div>
      <div className="max-w-[85%] flex-1">
        <div className="rounded-2xl rounded-tl-sm border border-white/[0.06] bg-white/[0.02] px-4 py-3">
          <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
            <span className="font-medium text-cyan-400">{message.agent ?? agentName}</span>
            {message.model && <span>· {message.model}</span>}
          </div>
          <p className="text-sm leading-relaxed text-white/90">{message.content}</p>

          {/* Sources */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 space-y-2 border-t border-white/[0.06] pt-3">
              <p className="text-xs font-semibold text-muted-foreground">Sources retrieved</p>
              {message.sources.map((src, i) => (
                <div key={i} className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-3.5 w-3.5 text-emerald-400" />
                    <span className="text-sm font-medium text-white">{src.title}</span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{src.snippet}</p>
                </div>
              ))}
            </div>
          )}

          {/* Memory used */}
          {message.memoryUsed && message.memoryUsed.length > 0 && (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className="text-xs text-muted-foreground">Memory used:</span>
              {message.memoryUsed.map((m) => (
                <span key={m} className="flex items-center gap-1 rounded-full border border-violet-400/20 bg-violet-400/5 px-2 py-0.5 text-xs text-violet-300">
                  <BrainCircuit className="h-3 w-3" /> {m}
                </span>
              ))}
            </div>
          )}

          {/* Actionable Protocol Tasks (Pushups, Workout, Study blocks) */}
          {message.suggestedTasks && message.suggestedTasks.length > 0 && (
            <div className="mt-4 space-y-2.5 border-t border-white/[0.08] pt-3">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold text-sky-400 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5" /> Actionable Protocol Tasks
                </p>
                <span className="text-[10px] text-muted-foreground">Click to add to dashboard</span>
              </div>
              {message.suggestedTasks.map((t, idx) => (
                <TaskAddCard key={idx} task={t} />
              ))}
            </div>
          )}
        </div>

        {/* Action bar */}
        <div className="mt-2 flex items-center gap-1">
          {[
            { icon: Copy, label: 'Copy' },
            { icon: ThumbsUp, label: 'Good' },
            { icon: ThumbsDown, label: 'Bad' },
            { icon: RefreshCw, label: 'Regenerate' },
          ].map((action) => (
            <button
              key={action.label}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-white/5 hover:text-white"
              aria-label={action.label}
            >
              <action.icon className="h-3.5 w-3.5" />
            </button>
          ))}
          <span className="ml-2 text-xs text-muted-foreground">{message.timestamp}</span>
        </div>
      </div>
    </motion.div>
  );
}

function TypingIndicator({ agentName }: { agentName: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-sky-500 text-xs font-bold text-white">
        {agentName[0]}
      </div>
      <div className="rounded-2xl rounded-tl-sm border border-white/[0.06] bg-white/[0.02] px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-cyan-400">{agentName} is thinking</span>
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="h-1.5 w-1.5 rounded-full bg-sky-400"
                animate={{ opacity: [0.3, 1, 0.3], y: [0, -3, 0] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.15 }}
              />
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function TaskAddCard({
  task,
}: {
  task: { title: string; description?: string; priority: 'high' | 'normal' | 'low'; due_date?: string };
}) {
  const [added, setAdded] = useState(false);
  const [adding, setAdding] = useState(false);

  const handleAdd = async () => {
    setAdding(true);
    try {
      await createTask({
        title: task.title,
        description: task.description,
        priority: task.priority,
        due_date: task.due_date || new Date().toISOString().split('T')[0],
      });
      setAdded(true);
    } catch {
      // ignore
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-sky-400/20 bg-sky-500/[0.05] p-3 text-left">
      <div className="min-w-0 flex-1">
        <div className="text-xs font-bold text-white leading-tight">{task.title}</div>
        {task.description && (
          <div className="mt-0.5 text-[11px] text-muted-foreground line-clamp-1">
            {task.description}
          </div>
        )}
      </div>
      <Button
        size="sm"
        disabled={added || adding}
        onClick={handleAdd}
        className={cn(
          'h-7 shrink-0 gap-1 rounded-lg px-2.5 text-[11px] font-semibold transition-all',
          added
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
            : 'bg-sky-400/20 text-sky-300 border border-sky-400/40 hover:bg-sky-400/30'
        )}
      >
        {added ? (
          <>
            <Check className="h-3 w-3" /> Added
          </>
        ) : (
          <>
            <Plus className="h-3 w-3" /> Add Task
          </>
        )}
      </Button>
    </div>
  );
}
