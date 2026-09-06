import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function GET(request: Request) {
  const authHeader = request.headers.get("authorization") || "";

  // 1. Try FastAPI backend
  try {
    const backendRes = await fetch(`${BACKEND_URL}/chat/history`, {
      headers: { Authorization: authHeader },
      signal: AbortSignal.timeout(3000),
    });
    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch {
    // Fall through
  }

  // 2. Default sample conversations for instant offline experience
  return NextResponse.json([
    {
      conversation_id: 1,
      title: "Daily Pushup & Study Routine",
      messages: [
        { role: "user", content: "Help me set up a daily routine with 50 pushups and 2 hours of study." },
        { role: "assistant", content: "I have created your 50-pushup progression protocol and 2-hour Pomodoro study blocks! You can add them directly to your task schedule." },
      ],
    },
    {
      conversation_id: 2,
      title: "RajOS System Introduction",
      messages: [
        { role: "user", content: "What can RajOS do for me?" },
        { role: "assistant", content: "RajOS is your 3D personal AI Operating System, coordinating Atlas, Nova, Sage, Echo, and Pulse across memory, documents, and mobile task notifications." },
      ],
    },
  ]);
}
