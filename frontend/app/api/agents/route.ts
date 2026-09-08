import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const DEFAULT_AGENTS = [
  {
    id: "atlas",
    name: "Atlas",
    description: "General AI assistant and task orchestrator. Coordinates multi-agent workflows and routes complex goals.",
    specialty: "General Conversation & Orchestration",
    status: "Active",
    tools: ["memory", "task_manager", "agent_router", "context_builder"],
    tasksCompleted: 1420,
    successRate: 98.4,
    lastActive: "Just now",
    avatar: "A",
  },
  {
    id: "nova",
    name: "Nova",
    description: "Research & knowledge retrieval specialist. Deep-searches vector memory, documents, and notes.",
    specialty: "Research & Knowledge Retrieval",
    status: "Active",
    tools: ["memory_search", "notes_search", "document_search", "web_search"],
    tasksCompleted: 984,
    successRate: 97.8,
    lastActive: "2m ago",
    avatar: "N",
  },
  {
    id: "sage",
    name: "Sage",
    description: "Planning & productivity specialist. Manages tasks, routines, pushup challenges, and deep study blocks.",
    specialty: "Planning & Productivity",
    status: "Active",
    tools: ["task_manager", "calendar", "workflow_builder", "prioritizer"],
    tasksCompleted: 1120,
    successRate: 99.1,
    lastActive: "5m ago",
    avatar: "S",
  },
  {
    id: "echo",
    name: "Echo",
    description: "Memory & context specialist. Remembers preferences, builds personal knowledge graphs, and tracks habits.",
    specialty: "Memory & Context Management",
    status: "Active",
    tools: ["memory_store", "memory_search", "profile_builder", "preference_tracker"],
    tasksCompleted: 756,
    successRate: 96.5,
    lastActive: "12m ago",
    avatar: "E",
  },
  {
    id: "pulse",
    name: "Pulse",
    description: "Analytics & monitoring specialist. Tracks task velocity, system telemetry, and habit consistency.",
    specialty: "Analytics & Monitoring",
    status: "Active",
    tools: ["activity_tracker", "analytics_engine", "report_generator", "trend_analyzer"],
    tasksCompleted: 643,
    successRate: 98.9,
    lastActive: "1m ago",
    avatar: "P",
  },
];

export async function GET(request: Request) {
  const authHeader = request.headers.get("authorization") || "";

  // 1. Try FastAPI backend
  try {
    const backendRes = await fetch(`${BACKEND_URL}/agents/`, {
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

  return NextResponse.json(DEFAULT_AGENTS);
}
