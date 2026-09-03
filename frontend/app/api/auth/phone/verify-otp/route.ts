import { NextResponse } from "next/server";

declare global {
  var __rajos_otp_store: Map<string, { code: string; expiresAt: number; attempts: number }> | undefined;
}

const otpStore = globalThis.__rajos_otp_store ?? new Map<string, { code: string; expiresAt: number; attempts: number }>();
globalThis.__rajos_otp_store = otpStore;

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const rawPhone = String(body.phone || "").trim();
    const otp = String(body.otp || "").trim();

    if (!rawPhone || !otp) {
      return NextResponse.json({ detail: "Phone and verification code are required" }, { status: 400 });
    }

    let clean = rawPhone.replace(/[^\d+]/g, "");
    if (!clean.startsWith("+")) {
      if (clean.length === 10) clean = "+91" + clean;
      else if (clean.startsWith("91") && clean.length === 12) clean = "+" + clean;
      else clean = "+91" + clean;
    }

    // 1. Attempt delegation to FastAPI backend
    try {
      const backendRes = await fetch(`${BACKEND_URL}/auth/phone/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: clean, otp }),
        signal: AbortSignal.timeout(3000),
      });

      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Backend offline — fall through to autonomous verification
    }

    // 2. Autonomous Next.js verification
    const record = otpStore.get(clean);
    if (!record) {
      return NextResponse.json(
        { detail: "No active verification code found for this number. Please request a new code." },
        { status: 400 }
      );
    }

    if (Date.now() > record.expiresAt) {
      otpStore.delete(clean);
      return NextResponse.json(
        { detail: "Verification code has expired. Please request a new code." },
        { status: 400 }
      );
    }

    if (record.code !== otp) {
      record.attempts += 1;
      const remaining = Math.max(0, 5 - record.attempts);
      return NextResponse.json(
        { detail: `Invalid verification code. ${remaining} attempt(s) remaining.` },
        { status: 400 }
      );
    }

    // Code matched -> delete
    otpStore.delete(clean);

    // Generate local JWT token (base64 encoded JSON for self-contained auth)
    const payload = {
      sub: `phone_${clean.replace("+", "")}@rajos.phone`,
      username: `user_${clean.slice(-4)}`,
      phone: clean,
      exp: Math.floor(Date.now() / 1000) + 7 * 24 * 3600,
    };
    const token = "rajos_jwt_" + Buffer.from(JSON.stringify(payload)).toString("base64");

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: {
        id: 99,
        username: payload.username,
        email: payload.sub,
        phone: clean,
      },
      is_new: false,
      message: `Welcome back, ${payload.username}!`,
    });
  } catch (err) {
    console.error("verify-otp route error:", err);
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Verification error" },
      { status: 500 }
    );
  }
}
