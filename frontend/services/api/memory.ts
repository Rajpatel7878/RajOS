import API from "./client";

function getToken() {
  return localStorage.getItem("token");
}

export interface Memory {
  id: number;
  key: string;
  value: string;
  user_id: number;
}

export interface MemoryCreate {
  key: string;
  value: string;
}

export async function getMemories(): Promise<Memory[]> {
  const res = await fetch(`${API}/memory/`, {
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

export async function deleteMemory(memoryId: number) {
  const res = await fetch(`${API}/memory/${memoryId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to delete memory");
  return data;
}

export async function searchMemory(query: string) {
  const res = await fetch(`${API}/memory/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ query }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to search memories");
  return data;
}

export async function getMemoryStats() {
  const res = await fetch(`${API}/memory/stats`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to get memory stats");
  return data;
}
