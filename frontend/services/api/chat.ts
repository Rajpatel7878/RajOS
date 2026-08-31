import API from "./client";

export async function sendMessage(
  message: string,
  conversationId: number | null = null,
  agentId: string | null = null
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
      agent_id: agentId,
    }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Chat request failed");
  }

  return data;
}

export async function searchConversations(query: string) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API}/chat/history`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) throw new Error("Failed to load conversations");

  const data = await res.json();

  if (!query.trim()) return data;

  return data.filter(
    (conv: { title: string; messages: { content: string }[] }) =>
      conv.title?.toLowerCase().includes(query.toLowerCase()) ||
      conv.messages?.some((m) =>
        m.content?.toLowerCase().includes(query.toLowerCase())
      )
  );
}
