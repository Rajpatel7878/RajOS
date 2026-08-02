export type MemoryCategory =
  | 'Projects'
  | 'Goals'
  | 'Preferences'
  | 'Skills'
  | 'Knowledge';

export type Importance = 'Critical' | 'High' | 'Medium' | 'Low';

export interface MemoryItem {
  id: string;
  title: string;
  description: string;
  category: MemoryCategory;
  importance: Importance;
  createdAt: string;
  relevanceScore: number;
  tags: string[];
}

export type AgentStatus = 'Active' | 'Planning' | 'Idle' | 'Executing' | 'Paused';

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  avatar: string;
  tasksCompleted: number;
  successRate: number;
  lastActive: string;
  tools: string[];
  currentTask?: string;
  steps?: AgentStep[];
}

export interface AgentStep {
  id: string;
  label: string;
  status: 'done' | 'active' | 'pending';
  tool?: string;
  detail?: string;
}

export interface KnowledgeDoc {
  id: string;
  title: string;
  type: 'PDF' | 'Web' | 'Note' | 'Code' | 'Data';
  chunks: number;
  vectors: number;
  status: 'Indexed' | 'Processing' | 'Failed';
  uploadedAt: string;
  size: string;
}

export interface KnowledgeNode {
  id: string;
  label: string;
  group: 'core' | 'domain' | 'document' | 'concept';
}

export interface KnowledgeEdge {
  source: string;
  target: string;
  weight: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  model?: string;
  agent?: string;
  sources?: { title: string; snippet: string }[];
  memoryUsed?: string[];
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  messages: ChatMessage[];
  model: string;
  agent: string;
}

export interface LLMModel {
  id: string;
  name: string;
  provider: string;
  contextWindow: string;
  strengths: string[];
  costPerMTok: number;
  latency: 'Fast' | 'Medium' | 'Slow';
}

export interface ActivityItem {
  id: string;
  type: 'agent' | 'memory' | 'knowledge' | 'chat' | 'automation' | 'system';
  title: string;
  description: string;
  timestamp: string;
  status: 'success' | 'running' | 'info' | 'warning';
}

export interface StatCard {
  id: string;
  label: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'flat';
  icon: string;
  sparkline: number[];
}

export interface PricingTier {
  name: string;
  price: string;
  period: string;
  tagline: string;
  features: string[];
  cta: string;
  highlighted?: boolean;
}
