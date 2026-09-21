import API from "./client";

function getToken() {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null;
}

export interface Memory {
  id: number;
  key: string;
  value: string;
  content?: string | null;
  memory_type: "preference" | "goal" | "project" | "instruction" | "fact" | string;
  source: "explicit_user" | "inferred_llm" | "system" | string;
  confidence: "low" | "medium" | "high" | string;
  importance: "low" | "medium" | "high" | "critical" | string;
  status: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  last_accessed_at?: string | null;
  access_count: number;
}

export interface MemoryCreate {
  key: string;
  value: string;
  content?: string;
  memory_type?: string;
  confidence?: string;
  importance?: string;
  source?: string;
}

export interface MemoryUpdate {
  key?: string;
  value?: string;
  content?: string;
  memory_type?: string;
  confidence?: string;
  importance?: string;
  status?: string;
}

export interface MemoryStats {
  total_memories: number;
  active_memories: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
}

export async function getMemories(category?: string, search?: string): Promise<Memory[]> {
  const params = new URLSearchParams();
  if (category && category.toLowerCase() !== "all") params.append("memory_type", category);
  if (search && search.trim()) params.append("search", search.trim());

  const url = `${API}/memory/${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch memories");
  return data;
}

export async function createMemory(memory: MemoryCreate): Promise<Memory> {
  const res = await fetch(`${API}/memory/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(memory),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to create memory");
  return data;
}

export async function updateMemory(memoryId: number, memory: MemoryUpdate): Promise<Memory> {
  const res = await fetch(`${API}/memory/${memoryId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(memory),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to update memory");
  return data;
}

export async function deleteMemory(memoryId: number) {
  const res = await fetch(`${API}/memory/${memoryId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to delete memory");
  return data;
}

export async function processExplicitMemory(userMessage: string) {
  const res = await fetch(`${API}/memory/explicit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ user_message: userMessage }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to process memory intent");
  return data;
}

export async function searchMemory(query: string, limit = 5, memoryType?: string) {
  const res = await fetch(`${API}/memory/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ query, limit, memory_type: memoryType }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to search memories");
  return data;
}

export async function getMemoryStats(): Promise<MemoryStats> {
  const res = await fetch(`${API}/memory/stats`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to get memory stats");
  return data;
}
