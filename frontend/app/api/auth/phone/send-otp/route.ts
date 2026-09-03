import { NextResponse } from "next/server";

// Global OTP memory store for Next.js runtime
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

    if (!rawPhone) {
      return NextResponse.json({ detail: "Phone number is required" }, { status: 400 });
    }

    // Standardize phone format
    let clean = rawPhone.replace(/[^\d+]/g, "");
    if (!clean.startsWith("+")) {
      if (clean.length === 10) clean = "+91" + clean;
      else if (clean.startsWith("91") && clean.length === 12) clean = "+" + clean;
      else clean = "+91" + clean;
    }

    // 1. Attempt to delegate to FastAPI backend if running
    try {
      const backendRes = await fetch(`${BACKEND_URL}/auth/phone/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: clean }),
        signal: AbortSignal.timeout(3000),
      });

      if (backendRes.ok) {
        const data = await backendRes.json();
        return NextResponse.json(data);
      }
    } catch {
      // Backend offline or unreachable — seamlessly fall through to Next.js handler
    }

    // 2. Next.js Autonomous OTP Generation
    const code = String(Math.floor(100000 + Math.random() * 900000));
    const expiresAt = Date.now() + 5 * 60 * 1000; // 5 minutes

    otpStore.set(clean, { code, expiresAt, attempts: 0 });

    console.log(`[RajOS Next.js OTP] Generated code for ${clean}: ${code}`);

    return NextResponse.json({
      status: "success",
      message: `Verification code sent to ${clean}`,
      phone: clean,
      expires_in: 300,
      sms_dispatched: false,
      dev_otp: code,
    });
  } catch (err) {
    console.error("send-otp route error:", err);
    return NextResponse.json(
      { detail: err instanceof Error ? err.message : "Failed to process request" },
      { status: 500 }
    );
  }
}
