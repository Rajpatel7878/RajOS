import { NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function GET(request: Request) {
  try {
    const authHeader = request.headers.get("authorization") || "";
    const backendRes = await fetch(`${BACKEND_URL}/agents`, {
      headers: { Authorization: authHeader },
      signal: AbortSignal.timeout(3500),
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch {
    // Fall through
  }

  return NextResponse.json({ detail: "Backend agents endpoint unavailable" }, { status: 503 });
}
