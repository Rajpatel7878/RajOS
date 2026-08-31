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
  user_id: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
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
  const res = await fetch(`${API}/tasks/${taskId}/complete`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to complete task");
  return data;
}

export async function deleteTask(taskId: number) {
  const res = await fetch(`${API}/tasks/${taskId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to delete task");
  return data;
}
