import API from "./client";

export interface TaskSummary {
  id: number;
  title: string;
  description?: string;
  priority?: string;
  computed_priority?: string;
  priority_score?: number;
  category?: string;
  due_date?: string;
  estimated_duration?: number;
  reasons?: string[];
}

export interface DailyBrief {
  date: string;
  overdue_count: number;
  overdue_tasks: TaskSummary[];
  due_today_count: number;
  due_today_tasks: any[];
  recommended_focus: any[];
  quick_wins: TaskSummary[];
  total_estimated_workload: string;
}

export interface WeeklySummary {
  period: string;
  tasks_created: number;
  tasks_completed: number;
  completed_on_time: number;
  overdue_count: number;
  completion_rate: number;
  top_categories: Record<string, number>;
  upcoming_important_tasks_count: number;
}

export interface Recommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  reason: string;
  related_task_ids: number[];
  action_suggestion: string;
  priority: string;
}

export interface WorkloadAnalysis {
  total_pending: number;
  total_completed: number;
  total_estimated_workload_minutes: number;
  estimated_workload_formatted: string;
  category_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
}

export interface ProductivityTrends {
  has_sufficient_data: boolean;
  message: string;
  daily_data: Array<{
    date: string;
    day: string;
    tasks_created: number;
    tasks_completed: number;
  }>;
}

function getAuthHeader(): Record<string, string> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function getProductivitySummary() {
  const res = await fetch(`${API}/productivity/summary`, {
    headers: getAuthHeader(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch productivity summary");
  return data;
}

export async function getDailyBrief(): Promise<DailyBrief> {
  const res = await fetch(`${API}/productivity/daily`, {
    headers: getAuthHeader(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch daily brief");
  return data;
}

export async function getWeeklySummary(): Promise<WeeklySummary> {
  const res = await fetch(`${API}/productivity/weekly`, {
    headers: getAuthHeader(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch weekly summary");
  return data;
}

export async function getRecommendations(): Promise<{ count: number; recommendations: Recommendation[] }> {
  const res = await fetch(`${API}/productivity/recommendations`, {
    headers: getAuthHeader(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch recommendations");
  return data;
}

export async function getWorkload(): Promise<WorkloadAnalysis> {
  const res = await fetch(`${API}/productivity/workload`, {
    headers: getAuthHeader(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch workload analysis");
  return data;
}

export async function getTrends(): Promise<ProductivityTrends> {
  const res = await fetch(`${API}/productivity/trends`, {
    headers: getAuthHeader(),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to fetch productivity trends");
  return data;
}

export async function planTasks(available_minutes?: number, constraints?: string) {
  const res = await fetch(`${API}/productivity/plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({ available_minutes, constraints }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to generate plan");
  return data;
}

export async function breakDownTask(title: string, description?: string) {
  const res = await fetch(`${API}/productivity/breakdown`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({ title, description }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to generate task breakdown");
  return data;
}
