const API_URL = "http://127.0.0.1:8000";

export interface DashboardStats {
  tasks: number;
  completed_tasks: number;
  notes: number;
  memories: number;
}

export async function getDashboardStats(token: string) {
  const res = await fetch(`${API_URL}/dashboard/stats`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch dashboard stats");
  }

  return res.json() as Promise<DashboardStats>;
}
