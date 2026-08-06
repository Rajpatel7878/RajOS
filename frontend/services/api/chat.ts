import API from "./client";

export async function sendMessage(
  message: string,
  conversationId: number | null = null
) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API}/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
    }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Chat request failed");
  }

  return data;
}
