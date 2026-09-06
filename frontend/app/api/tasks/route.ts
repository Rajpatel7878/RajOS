import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// In-memory persistent task store for resilient fallback
let _MEMORY_TASKS = [
  {
    id: 1,
    title: "Morning Routine: 50 Pushups & Hydration",
    description: "3 sets (20-15-15) with 60s rest. 500ml water.",
    completed: false,
    priority: "high",
    due_date: new Date().toISOString().split("T")[0],
    user_id: 1,
  },
  {
    id: 2,
    title: "Deep Work Study Block (2 Hours)",
    description: "Focus on primary learning topics with 50m/10m Pomodoro blocks.",
    completed: false,
    priority: "high",
    due_date: new Date().toISOString().split("T")[0],
    user_id: 1,
  },
  {
    id: 3,
    title: "RajOS Task Telemetry Review",
    description: "Review automated agent outputs and sync with mobile phone notifications.",
    completed: true,
    priority: "normal",
    due_date: new Date().toISOString().split("T")[0],
    user_id: 1,
  },
];

export async function GET(request: Request) {
  const authHeader = request.headers.get("authorization") || "";

  // 1. Try FastAPI backend
  try {
    const backendRes = await fetch(`${BACKEND_URL}/tasks/`, {
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

  return NextResponse.json(_MEMORY_TASKS);
}

export async function POST(request: Request) {
  const authHeader = request.headers.get("authorization") || "";
  try {
    const body = await request.json();

    // 1. Try FastAPI backend
    try {
      const backendRes = await fetch(`${BACKEND_URL}/tasks/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(3000),
      });
      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fall through
    }

    // 2. Memory store
    const newTask = {
      id: Date.now(),
      title: body.title || "Untitled Task",
      description: body.description || "",
      completed: false,
      priority: body.priority || "normal",
      due_date: body.due_date || new Date().toISOString().split("T")[0],
      user_id: 1,
    };
    _MEMORY_TASKS.unshift(newTask);
    return NextResponse.json(newTask);
  } catch (err) {
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Failed to create task" },
      { status: 500 }
    );
  }
}
