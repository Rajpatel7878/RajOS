import API from "./client";

function getToken() {
  return localStorage.getItem("token");
}

export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  specialty: string;
  status: "Active" | "Idle" | "Executing" | "Planning" | "Paused";
  tools: string[];
  tasksCompleted: number;
  successRate: number;
  lastActive: string;
  avatar: string;
}

export interface AgentRunRequest {
  prompt: string;
  context?: Record<string, unknown>;
}

export interface AgentRunResult {
  agent_id: string;
  agent_name: string;
  response: string;
  status: string;
  steps?: { label: string; status: string; tool?: string }[];
}

export async function getAgents(): Promise<AgentInfo[]> {
  const res = await fetch(`${API}/agents/`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch agents");
  return data;
}

export async function runAgent(
  agentId: string,
  request: AgentRunRequest
): Promise<AgentRunResult> {
  const res = await fetch(`${API}/agents/${agentId}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(request),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to run agent");
  return data;
}

export async function getAgentStatus(agentId: string) {
  const res = await fetch(`${API}/agents/${agentId}/status`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to get agent status");
  return data;
}
