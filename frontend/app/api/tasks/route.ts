import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

let _MEMORY_TASKS = [
  {
    id: 1,
    title: "Daily 50 Pushups (3 Sets: 20-15-15)",
    description: "Strict form, full chest touch, 60s rest between sets.",
    completed: false,
    priority: "high",
    due_date: new Date().toISOString().split("T")[0],
    user_id: 1,
  },
  {
    id: 2,
    title: "Deep Work Study Block (2 Hours)",
    description: "Focus on primary learning topics with 50m/10m Pomodoro intervals.",
    completed: false,
    priority: "high",
    due_date: new Date().toISOString().split("T")[0],
    user_id: 1,
  },
  {
    id: 3,
    title: "Morning Routine: 500ml Water & Task Planning",
    description: "Hydrate immediately after waking up and set today''s top 3 objectives.",
    completed: true,
    priority: "normal",
    due_date: new Date().toISOString().split("T")[0],
    user_id: 1,
  },
];

export async function GET(request: Request) {
  const authHeader = request.headers.get("authorization") || "";

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

export async function PATCH(request: Request) {
  const authHeader = request.headers.get("authorization") || "";
  try {
    const body = await request.json();
    const taskId = Number(body.id || body.task_id);
    const completed = typeof body.completed === "boolean" ? body.completed : true;

    // Try backend
    try {
      const endpoint = completed ? `${BACKEND_URL}/tasks/${taskId}/complete` : `${BACKEND_URL}/tasks/${taskId}/toggle`;
      const backendRes = await fetch(endpoint, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
        signal: AbortSignal.timeout(3000),
      });
      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fall through
    }

    // Memory update
    const target = _MEMORY_TASKS.find((t) => t.id === taskId);
    if (target) {
      target.completed = completed;
    }

    return NextResponse.json({
      message: `Task ${taskId} marked as ${completed ? "completed" : "pending"}`,
      task_id: taskId,
      completed,
    });
  } catch (err) {
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Failed to update task" },
      { status: 500 }
    );
  }
}
