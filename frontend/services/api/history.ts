import API from "./client";

export async function getHistory() {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API}/chat/history`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to load history");
  }

  return await res.json();
}
