import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || "";

interface ChatTaskSuggestion {
  title: string;
  description: string;
  priority: "high" | "normal" | "low";
  due_date: string;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const message = String(body.message || "").trim();
    const conversationId = body.conversation_id || null;
    const agentId = body.agent_id || "atlas";
    const authHeader = request.headers.get("authorization") || "";

    if (!message) {
      return NextResponse.json({ detail: "Message cannot be empty" }, { status: 400 });
    }

    // 1. Try forwarding to FastAPI backend
    try {
      const backendRes = await fetch(`${BACKEND_URL}/chat/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          agent_id: agentId,
        }),
        signal: AbortSignal.timeout(3500),
      });

      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Backend offline or timeout -> proceed with resilient Gemini AI generator
    }

    // 2. Direct AI Processing with Routine & Task Extraction
    const lower = message.toLowerCase();
    const suggestedTasks: ChatTaskSuggestion[] = [];

    // Detect exercise / pushup requests
    if (lower.includes("pushup") || lower.includes("exercise") || lower.includes("workout") || lower.includes("gym") || lower.includes("fitness")) {
      suggestedTasks.push({
        title: "Daily Pushup Target: 50 Reps (3 Sets: 20-15-15)",
        description: "Focus on strict form, full chest touch, and controlled tempo. 60s rest between sets.",
        priority: "high",
        due_date: new Date().toISOString().split("T")[0],
      });
      suggestedTasks.push({
        title: "Post-Workout Stretch & Hydration (10 mins)",
        description: "Target chest, shoulders, and core. Drink 500ml water.",
        priority: "normal",
        due_date: new Date().toISOString().split("T")[0],
      });
    }

    // Detect study / focus requests
    if (lower.includes("study") || lower.includes("read") || lower.includes("exam") || lower.includes("revision") || lower.includes("learn") || lower.includes("code")) {
      suggestedTasks.push({
        title: "Deep Work Study Block 1: 50 Mins Focus",
        description: "Zero distractions, phone on silent. Work through priority chapters / coding modules.",
        priority: "high",
        due_date: new Date().toISOString().split("T")[0],
      });
      suggestedTasks.push({
        title: "Active Recall & Revision Notes (20 mins)",
        description: "Summarize core concepts from memory without looking at reference material.",
        priority: "normal",
        due_date: new Date().toISOString().split("T")[0],
      });
    }

    // Detect general daily routine / task creation requests
    if (lower.includes("daily") || lower.includes("routine") || lower.includes("habit") || lower.includes("plan my day")) {
      if (suggestedTasks.length === 0) {
        suggestedTasks.push({
          title: "Morning Habit: 30 Pushups + Hydration",
          description: "Kickstart metabolism and focus first thing in the morning.",
          priority: "high",
          due_date: new Date().toISOString().split("T")[0],
        });
        suggestedTasks.push({
          title: "2-Hour Deep Study & Skill Practice",
          description: "Focused learning session on high-value subject.",
          priority: "high",
          due_date: new Date().toISOString().split("T")[0],
        });
        suggestedTasks.push({
          title: "Evening Review & Next-Day Planning (15m)",
          description: "Review completed tasks, log pushups/study progress.",
          priority: "normal",
          due_date: new Date().toISOString().split("T")[0],
        });
      }
    }

    // Call live Gemini API if key is available
    let aiResponseText = "";
    if (GEMINI_API_KEY) {
      try {
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`;
        const sysPrompt = `You are RajOS Atlas, the personal AI operating system assistant.
You help the user stay highly disciplined, accomplish daily routines (including pushups, physical fitness, focused study sessions, and high-productivity habits), and organize their life.
Be encouraging, crisp, structured, and actionable. Format responses with clean markdown bullet points.

User query: "${message}"`;

        const geminiRes = await fetch(geminiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: sysPrompt }] }],
          }),
          signal: AbortSignal.timeout(6000),
        });

        if (geminiRes.ok) {
          const geminiData = await geminiRes.json();
          aiResponseText =
            geminiData?.candidates?.[0]?.content?.parts?.[0]?.text || "";
        }
      } catch (geminiErr) {
        console.warn("Gemini direct call warning:", geminiErr);
      }
    }

    // Fallback if Gemini network failed
    if (!aiResponseText) {
      if (suggestedTasks.length > 0) {
        aiResponseText = `I have analyzed your request and created an optimized routine for you:\n\n` +
          `### 🎯 Your Daily Protocol\n` +
          suggestedTasks.map((t, idx) => `${idx + 1}. **${t.title}** (${t.priority.toUpperCase()})\n   *${t.description}*`).join("\n\n") +
          `\n\n💡 **Tip:** Click **"Add to Tasks"** below to automatically add these into your daily dashboard with mobile notification reminders!`;
      } else {
        aiResponseText = `Hello! I am **Atlas**, your RajOS assistant. I can help you coordinate your day, create daily routines (like exercise, 50 pushups, and focused study blocks), analyze documents, and manage your memory engine. How can I assist your workflow today?`;
      }
    }

    return NextResponse.json({
      response: aiResponseText,
      agent_name: "Atlas",
      agent_id: agentId || "atlas",
      model: "Gemini 2.5 Flash",
      conversation_id: conversationId || Date.now(),
      suggested_tasks: suggestedTasks,
      sources: [],
      memory_used: [],
    });
  } catch (err) {
    console.error("Chat API route error:", err);
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Chat service unavailable" },
      { status: 500 }
    );
  }
}
