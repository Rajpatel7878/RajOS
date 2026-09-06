"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Smartphone,
  CheckCircle2,
  AlertCircle,
  Bell,
  Clock,
  KeyRound,
  RotateCcw,
  Shield,
  Loader2,
  ArrowRight,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { sendPhoneOTP, verifyPhoneOTP, linkPhone } from "@/services/api/auth";

export const dynamic = "force-dynamic";

export default function PhoneLinkPage() {
  const router = useRouter();

  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [devOtpHint, setDevOtpHint] = useState<string | null>(null);
  const [smsDispatched, setSmsDispatched] = useState<boolean>(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  // Handle Send OTP
  const handleSendOTP = useCallback(async () => {
    setError(null);
    setSuccess(null);
    setDevOtpHint(null);

    const cleanNumber = phone.replace(/[^\d+]/g, "");
    if (!cleanNumber || cleanNumber.replace(/\D/g, "").length < 10) {
      setError("Please enter a valid 10-digit mobile number.");
      return;
    }

    setLoading(true);
    try {
      const data = await sendPhoneOTP(cleanNumber);
      setOtpSent(true);
      setResendCooldown(30);
      setSmsDispatched(Boolean(data.sms_dispatched));

      if (data.dev_otp) {
        setDevOtpHint(data.dev_otp);
        setOtp(data.dev_otp); // Pre-fill for frictionless testing
      }

      setSuccess(
        data.sms_dispatched
          ? `SMS verification code dispatched to ${data.phone || cleanNumber}`
          : `Verification code generated for ${data.phone || cleanNumber}`
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send verification code");
    } finally {
      setLoading(false);
    }
  }, [phone]);

  // Handle Verify & Link Phone
  const handleVerifyAndLink = useCallback(async () => {
    setError(null);
    setSuccess(null);

    if (!otp.trim() || otp.trim().length < 6) {
      setError("Please enter the 6-digit verification code.");
      return;
    }

    setLoading(true);
    try {
      const cleanNumber = phone.replace(/[^\d+]/g, "");
      // Link the phone and activate task notifications
      const data = await linkPhone(cleanNumber, otp.trim());

      setSuccess(`Mobile number ${cleanNumber} connected! Task notifications enabled.`);
      setTimeout(() => router.push("/dashboard"), 700);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid verification code");
    } finally {
      setLoading(false);
    }
  }, [phone, otp, router]);

  // Skip step
  const handleSkip = () => {
    router.push("/dashboard");
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-6 py-12">
      {/* Background Ambience */}
      <div className="pointer-events-none fixed inset-0 grid-bg opacity-[0.12]" />
      <div className="pointer-events-none fixed -left-[10%] top-[15%] h-[550px] w-[550px] rounded-full bg-sky-500/15 blur-[140px]" />
      <div className="pointer-events-none fixed -right-[10%] bottom-[15%] h-[500px] w-[500px] rounded-full bg-cyan-500/15 blur-[140px]" />

      {/* Brand */}
      <Link href="/" className="absolute left-6 top-6 z-20 flex items-center gap-2.5 group">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 shadow-lg shadow-sky-500/30 transition-transform duration-300 group-hover:scale-105">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <span className="text-xl font-bold tracking-tight text-white">RajOS</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-lg"
      >
        <div className="glass-card relative overflow-hidden p-8 sm:p-10 border border-white/[0.1] shadow-[0_20px_50px_rgba(0,0,0,0.8)] backdrop-blur-3xl">
          {/* Top light beam */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400/80 to-transparent" />

          {/* Step Progress Tracker */}
          <div className="mb-6 flex items-center justify-center gap-2">
            <div className="flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 text-[11px] font-semibold text-emerald-300">
              <CheckCircle2 className="h-3.5 w-3.5" />
              1. Google Account
            </div>
            <ChevronRight className="h-3 w-3 text-muted-foreground/40" />
            <div className="flex items-center gap-1.5 rounded-full bg-sky-500/15 border border-sky-400/40 px-3 py-1 text-[11px] font-semibold text-sky-300 shadow-[0_0_12px_rgba(56,189,248,0.25)]">
              <Smartphone className="h-3.5 w-3.5" />
              2. Mobile Task Notifications
            </div>
          </div>

          {/* Heading */}
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-extrabold tracking-tight text-white">
              Connect Your Mobile Phone
            </h1>
            <p className="mt-2 text-xs sm:text-sm text-muted-foreground leading-relaxed">
              Receive real-time task notifications, deadline alerts, and agent progress updates directly on your phone — even when your laptop is closed.
            </p>
          </div>

          {/* Notification feature pills */}
          <div className="mb-6 grid grid-cols-2 gap-2 text-left">
            <div className="flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] p-2.5 text-xs text-muted-foreground">
              <Bell className="h-4 w-4 text-sky-400 shrink-0" />
              <span>Instant Task Reminders</span>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.02] p-2.5 text-xs text-muted-foreground">
              <Clock className="h-4 w-4 text-emerald-400 shrink-0" />
              <span>Laptop Closed Alerts</span>
            </div>
          </div>

          {/* Global Alert Banners */}
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                animate={{ opacity: 1, height: "auto", marginBottom: 16 }}
                exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                className="flex items-start gap-2.5 overflow-hidden rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3"
              >
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" />
                <p className="text-xs text-rose-300 leading-relaxed">{error}</p>
              </motion.div>
            )}
            {success && (
              <motion.div
                initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                animate={{ opacity: 1, height: "auto", marginBottom: 16 }}
                exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                className="flex items-start gap-2.5 overflow-hidden rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3"
              >
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                <p className="text-xs text-emerald-300 leading-relaxed">{success}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step 1: Input Phone */}
          {!otpSent ? (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="phone-input" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Mobile Number
                </Label>
                <div className="flex gap-2">
                  <span className="flex h-11 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] px-3.5 text-sm font-bold text-sky-400 select-none">
                    🇮🇳 +91
                  </span>
                  <Input
                    id="phone-input"
                    type="tel"
                    placeholder="Enter 10-digit phone number"
                    value={phone}
                    onChange={(e) => {
                      setPhone(e.target.value);
                      setError(null);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleSendOTP();
                      }
                    }}
                    autoFocus
                    className="h-11 flex-1 border-white/[0.08] bg-white/[0.03] text-sm text-white placeholder:text-muted-foreground/50 focus:border-sky-400/50"
                  />
                </div>
                <p className="text-[11px] text-muted-foreground">
                  A verification code will be sent to confirm your phone for notifications.
                </p>
              </div>

              <Button
                type="button"
                onClick={handleSendOTP}
                disabled={loading || !phone.trim()}
                className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 hover:from-sky-400 hover:to-cyan-400 disabled:opacity-60 transition-all duration-200"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Sending Code...
                  </>
                ) : (
                  <>
                    <Smartphone className="h-4 w-4" />
                    Send Verification Code
                  </>
                )}
              </Button>
            </div>
          ) : (
            /* Step 2: Verify OTP */
            <div className="space-y-4">
              {/* Phone target indicator */}
              <div className="rounded-xl border border-sky-400/20 bg-sky-400/[0.06] p-3 text-xs text-sky-200 flex items-center justify-between">
                <div>
                  <span className="opacity-75">Target Number:</span>{" "}
                  <span className="font-bold text-white">
                    {phone.startsWith("+") ? phone : `+91 ${phone}`}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setOtpSent(false);
                    setOtp("");
                    setDevOtpHint(null);
                    setError(null);
                  }}
                  className="text-sky-400 hover:underline text-[11px] font-medium"
                >
                  Change
                </button>
              </div>

              {/* Dev Mode High-Visibility Box (Visible when no SMS provider is configured in .env) */}
              {devOtpHint && (
                <div className="rounded-2xl border border-amber-400/40 bg-gradient-to-br from-amber-500/15 via-amber-500/5 to-transparent p-4 text-xs text-amber-200 shadow-[0_0_24px_rgba(251,191,36,0.15)]">
                  <div className="flex items-center justify-between font-semibold text-amber-300 mb-1">
                    <span className="flex items-center gap-1.5">
                      <KeyRound className="h-4 w-4 text-amber-400" />
                      Development Mode Verification Code:
                    </span>
                    <span className="rounded bg-amber-400/20 px-1.5 py-0.5 text-[10px] uppercase tracking-wider">
                      Auto-filled
                    </span>
                  </div>
                  <div className="mt-2 flex items-center justify-between rounded-xl border border-amber-400/30 bg-black/40 px-3.5 py-2">
                    <span className="font-mono text-xl font-extrabold tracking-widest text-white">
                      {devOtpHint}
                    </span>
                    <span className="text-[10px] text-muted-foreground">Ready to verify</span>
                  </div>
                  <p className="mt-2 text-[11px] text-amber-200/70 leading-relaxed">
                    💡 In production, real carrier SMS is sent automatically via Twilio or Fast2SMS. Add <code className="text-white font-mono">FAST2SMS_API_KEY</code> or Twilio keys in <code className="text-white font-mono">backend/.env</code> for live SMS delivery.
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="otp-box" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Enter 6-Digit Code
                </Label>
                <div className="relative">
                  <KeyRound className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="otp-box"
                    type="text"
                    placeholder="123456"
                    value={otp}
                    onChange={(e) => {
                      setOtp(e.target.value.replace(/\D/g, "").slice(0, 6));
                      setError(null);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleVerifyAndLink();
                      }
                    }}
                    maxLength={6}
                    autoFocus
                    className="h-12 border-white/[0.08] bg-white/[0.03] pl-11 text-center font-mono text-xl font-extrabold tracking-[0.4em] text-white placeholder:text-muted-foreground/30 focus:border-emerald-400/50"
                  />
                </div>
              </div>

              <Button
                type="button"
                onClick={handleVerifyAndLink}
                disabled={loading || otp.length < 6}
                className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-400 disabled:opacity-60 transition-all duration-200"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Linking & Activating...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4" />
                    Verify & Activate Task Notifications
                  </>
                )}
              </Button>

              <div className="flex items-center justify-between text-xs pt-1">
                <button
                  type="button"
                  onClick={handleSendOTP}
                  disabled={loading || resendCooldown > 0}
                  className="flex items-center gap-1.5 text-muted-foreground hover:text-white disabled:opacity-50 transition-colors"
                >
                  <RotateCcw className="h-3 w-3" />
                  {resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : "Resend Code"}
                </button>
                <button
                  type="button"
                  onClick={handleSkip}
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  Skip for now
                </button>
              </div>
            </div>
          )}

          {/* Footer skip link */}
          <div className="mt-6 border-t border-white/[0.06] pt-4 text-center">
            <button
              type="button"
              onClick={handleSkip}
              className="text-xs text-muted-foreground hover:text-sky-300 transition-colors"
            >
              Skip phone setup and go directly to Dashboard →
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
