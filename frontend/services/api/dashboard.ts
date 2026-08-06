import API from "./client";

export async function getDashboardStats() {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API}/dashboard/stats`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.detail || "Stats failed");

  return data;
}

export async function getDashboardActivity() {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API}/dashboard/activity`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json();

  if (!res.ok) throw new Error(data.detail || "Activity failed");

  return data;
}
