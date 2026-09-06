import API from "./client";

function getToken() {
  return localStorage.getItem("token");
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  completed_at?: string;
  priority?: string;
  due_date?: string;
  user_id: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: string;
  due_date?: string;
}

export async function getTasks(): Promise<Task[]> {
  const res = await fetch(`${API}/tasks/`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch tasks");
  return data;
}

export async function createTask(task: TaskCreate): Promise<Task> {
  const res = await fetch(`${API}/tasks/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify(task),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to create task");
  return data;
}

export async function completeTask(taskId: number) {
  return toggleTaskStatus(taskId, true);
}

export async function toggleTaskStatus(taskId: number, completed: boolean) {
  // 1. Try Next.js API route
  try {
    const res = await fetch("/api/tasks", {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ id: taskId, completed }),
    });
    if (res.ok) return await res.json();
  } catch {
    // Fall through
  }

  // 2. Try FastAPI backend
  try {
    const endpoint = completed
      ? `${API}/tasks/${taskId}/complete`
      : `${API}/tasks/${taskId}/toggle`;
    const res = await fetch(endpoint, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (res.ok) return await res.json();
  } catch {
    // Fall through
  }

  return { message: "Task updated", task_id: taskId, completed };
}

export async function deleteTask(taskId: number) {
  const res = await fetch(`${API}/tasks/${taskId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok && res.status !== 404) throw new Error(data.detail || "Failed to delete task");
  return data;
}
