const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function getDashboardActivity(token: string) {
  const res = await fetch(`${API}/dashboard/activity`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to load activity");
  }

  return res.json();
}
