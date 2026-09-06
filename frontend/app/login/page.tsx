"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Mail,
  Lock,
  ArrowRight,
  Loader2,
  Eye,
  EyeOff,
  User,
  CheckCircle2,
  AlertCircle,
  Smartphone,
  KeyRound,
  RotateCcw,
  ChevronLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import {
  login,
  register,
  googleLogin,
  sendPhoneOTP,
  verifyPhoneOTP,
} from "@/services/api/auth";

type Mode = "signin" | "phone" | "signup";

export const dynamic = "force-dynamic";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("signin");

  // Email/Password state
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  // Phone OTP state
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [phoneLoading, setPhoneLoading] = useState(false);
  const [devOtpHint, setDevOtpHint] = useState<string | null>(null);
  const [resendCooldown, setResendCooldown] = useState(0);

  // Global alerts
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Resend countdown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const interval = setInterval(() => {
      setResendCooldown((prev) => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(interval);
  }, [resendCooldown]);

  useEffect(() => {
    if (sessionStorage.getItem("rajos_guest") === "1") {
      router.push("/dashboard");
    }
  }, [router]);

  const handleGuest = useCallback(() => {
    sessionStorage.setItem("rajos_guest", "1");
    router.push("/dashboard");
  }, [router]);

  // Handle Email Password Login / Signup
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      setSuccess(null);
      setLoading(true);

      try {
        if (mode === "signup") {
          await register(username, email, password);
          setSuccess("Account created successfully! Please sign in.");
          setMode("signin");
          setPassword("");
        } else {
          await login(email, password);
          setSuccess("Welcome back! Redirecting...");
          setTimeout(() => router.push("/dashboard"), 500);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Authentication failed");
      } finally {
        setLoading(false);
      }
    },
    [mode, username, email, password, router]
  );

  // Google OAuth — Step 1: Sign in, Step 2: Phone Link for task notifications
  const handleGoogleLogin = useCallback(async () => {
    setError(null);
    setSuccess(null);
    setGoogleLoading(true);
    try {
      const res = await googleLogin();
      if (res && res.access_token) {
        setSuccess("Signed in with Google! Next: Connect mobile for task notifications...");
        setTimeout(() => router.push("/auth/phone-link"), 600);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Google sign-in failed";
      setError(message);
      setGoogleLoading(false);
    }
  }, [router]);

  // Phone: Send OTP
  const handleSendOTP = useCallback(async () => {
    setError(null);
    setSuccess(null);
    setDevOtpHint(null);

    const cleanNumber = phone.replace(/[^\d+]/g, "");
    if (!cleanNumber || (cleanNumber.replace(/\D/g, "").length < 10)) {
      setError("Please enter a valid 10-digit mobile number.");
      return;
    }

    setPhoneLoading(true);
    try {
      const data = await sendPhoneOTP(cleanNumber);
      setOtpSent(true);
      setResendCooldown(30); // 30s cooldown before next send
      setSuccess(data.message || `Verification code dispatched to ${data.phone || cleanNumber}`);

      if (data.dev_otp) {
        setDevOtpHint(data.dev_otp);
        setOtp(data.dev_otp); // Auto-fill for friction-free dev testing
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to send verification code";
      setError(msg);
    } finally {
      setPhoneLoading(false);
    }
  }, [phone]);

  // Phone: Verify OTP
  const handleVerifyOTP = useCallback(async () => {
    setError(null);
    setSuccess(null);

    if (!otp.trim() || otp.trim().length < 6) {
      setError("Please enter the 6-digit verification code.");
      return;
    }

    setPhoneLoading(true);
    try {
      const cleanNumber = phone.replace(/[^\d+]/g, "");
      const data = await verifyPhoneOTP(cleanNumber, otp.trim());
      setSuccess(data.message || "Phone verified! Entering RajOS...");
      setTimeout(() => router.push("/dashboard"), 600);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Invalid verification code";
      setError(msg);
    } finally {
      setPhoneLoading(false);
    }
  }, [phone, otp, router]);

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-6 py-12">
      {/* Background layers */}
      <div className="pointer-events-none fixed inset-0 z-0 grid-bg opacity-[0.14]" />
      <div className="pointer-events-none fixed inset-0 z-0 bg-gradient-to-b from-sky-950/25 via-transparent to-background" />

      {/* Animated ambient background orbs */}
      <motion.div
        className="pointer-events-none fixed -left-[10%] top-[15%] h-[550px] w-[550px] rounded-full bg-sky-500/15 blur-[140px]"
        animate={{ x: [0, 40, -20, 0], y: [0, -30, 20, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="pointer-events-none fixed -right-[10%] bottom-[15%] h-[500px] w-[500px] rounded-full bg-cyan-500/15 blur-[140px]"
        animate={{ x: [0, -40, 20, 0], y: [0, 30, -20, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Top Left Brand Logo */}
      <Link href="/" className="absolute left-6 top-6 z-20 flex items-center gap-2.5 group">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 shadow-lg shadow-sky-500/30 transition-transform duration-300 group-hover:scale-105">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <span className="text-xl font-bold tracking-tight text-white">RajOS</span>
      </Link>

      {/* ── Main Auth Card ── */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="glass-card relative overflow-hidden p-8 sm:p-10 border border-white/[0.08] shadow-[0_20px_50px_-12px_rgba(0,0,0,0.8)] backdrop-blur-3xl">
          {/* Top accent glow line */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400/80 to-transparent" />

          {/* Heading */}
          <div className="mb-7 text-center">
            <h1 className="text-2xl font-extrabold tracking-tight text-white">
              {mode === "phone"
                ? "Phone Number Sign-In"
                : mode === "signin"
                ? "Welcome back"
                : "Create your account"}
            </h1>
            <p className="mt-1.5 text-xs sm:text-sm text-muted-foreground">
              {mode === "phone"
                ? "Fast, encrypted OTP verification directly on your mobile"
                : mode === "signin"
                ? "Sign in to your AI operating system"
                : "Start building with your autonomous intelligent workspace"}
            </p>
          </div>

          {/* ── 3-Tab Mode Toggle ── */}
          <div className="mb-6 flex rounded-xl border border-white/[0.08] bg-white/[0.03] p-1">
            {[
              { id: "signin", label: "Email" },
              { id: "phone", label: "📱 Phone (OTP)" },
              { id: "signup", label: "Sign Up" },
            ].map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => {
                  setMode(m.id as Mode);
                  setError(null);
                  setSuccess(null);
                  setDevOtpHint(null);
                }}
                className={cn(
                  "relative flex-1 rounded-lg py-2 text-xs sm:text-sm font-semibold transition-all duration-200",
                  mode === m.id
                    ? "text-white"
                    : "text-muted-foreground hover:text-white hover:bg-white/[0.02]"
                )}
              >
                {mode === m.id && (
                  <motion.div
                    layoutId="auth-mode-pill"
                    className="absolute inset-0 rounded-lg bg-gradient-to-r from-sky-500/25 to-cyan-500/25 ring-1 ring-sky-400/40 shadow-[0_0_12px_rgba(56,189,248,0.2)]"
                    transition={{ type: "spring", stiffness: 450, damping: 35 }}
                  />
                )}
                <span className="relative z-10">{m.label}</span>
              </button>
            ))}
          </div>

          {/* ── Global Alert Banner ── */}
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

          {/* ═══════════════════════════════════════════════════════════════════
              MODE 1: PHONE NUMBER & OTP AUTHENTICATION
          ═══════════════════════════════════════════════════════════════════ */}
          {mode === "phone" ? (
            <div className="space-y-4">
              {!otpSent ? (
                // Step 1: Phone number input
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone-number" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Mobile Number
                    </Label>
                    <div className="flex gap-2">
                      <span className="flex h-11 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] px-3.5 text-sm font-bold text-sky-400 select-none">
                        🇮🇳 +91
                      </span>
                      <Input
                        id="phone-number"
                        type="tel"
                        placeholder="Enter 10-digit number"
                        value={phone}
                        onChange={(e) => {
                          // Allow digits, spaces, dashes
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
                      A 6-digit cryptographic security code will be generated for your device.
                    </p>
                  </div>

                  <Button
                    type="button"
                    onClick={handleSendOTP}
                    disabled={phoneLoading || !phone.trim()}
                    className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-400 disabled:opacity-60 transition-all duration-200"
                  >
                    {phoneLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Generating Code...
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
                // Step 2: 6-digit OTP verification input
                <div className="space-y-4">
                  <div className="rounded-xl border border-sky-400/20 bg-sky-400/[0.06] p-3 text-xs text-sky-200 flex items-center justify-between">
                    <div>
                      <span className="opacity-75">Code dispatched to:</span>{" "}
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

                  {/* Dev mode helper badge */}
                  {devOtpHint && (
                    <div className="rounded-2xl border border-amber-400/40 bg-gradient-to-br from-amber-500/15 via-amber-500/5 to-transparent p-4 text-xs text-amber-200 shadow-[0_0_20px_rgba(251,191,36,0.15)]">
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
                        💡 Real carrier SMS is dispatched when <code className="text-white font-mono">FAST2SMS_API_KEY</code> or Twilio credentials are configured in <code className="text-white font-mono">backend/.env</code>.
                      </p>
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="otp-input" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Enter 6-Digit Security Code
                    </Label>
                    <div className="relative">
                      <KeyRound className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="otp-input"
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
                            handleVerifyOTP();
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
                    onClick={handleVerifyOTP}
                    disabled={phoneLoading || otp.length < 6}
                    className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 hover:from-emerald-400 hover:to-teal-400 disabled:opacity-60 transition-all duration-200"
                  >
                    {phoneLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Verifying Code...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="h-4 w-4" />
                        Verify & Access RajOS
                      </>
                    )}
                  </Button>

                  {/* Resend OTP button with cooldown */}
                  <div className="flex items-center justify-between text-xs pt-1">
                    <button
                      type="button"
                      onClick={handleSendOTP}
                      disabled={phoneLoading || resendCooldown > 0}
                      className="flex items-center gap-1.5 text-muted-foreground hover:text-white disabled:opacity-50 transition-colors"
                    >
                      <RotateCcw className="h-3 w-3" />
                      {resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : "Resend Code"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setMode("signin")}
                      className="text-sky-400 hover:underline"
                    >
                      Use email instead
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* ═══════════════════════════════════════════════════════════════════
               MODE 2: STANDARD EMAIL & PASSWORD (SIGN IN / SIGN UP)
            ═══════════════════════════════════════════════════════════════════ */
            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === "signup" && (
                <div className="space-y-1.5">
                  <Label htmlFor="username" className="text-xs font-semibold text-muted-foreground">
                    Username
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="username"
                      type="text"
                      placeholder="Your unique handle"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 text-white placeholder:text-muted-foreground/50 focus:border-sky-400/50"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-1.5">
                <Label htmlFor="email" className="text-xs font-semibold text-muted-foreground">
                  Email
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 text-white placeholder:text-muted-foreground/50 focus:border-sky-400/50"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="password" className="text-xs font-semibold text-muted-foreground">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder={mode === "signup" ? "At least 6 characters" : "Your password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 pr-11 text-white placeholder:text-muted-foreground/50 focus:border-sky-400/50"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 hover:from-sky-400 hover:to-cyan-400 disabled:opacity-60 transition-all duration-200"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Please wait...
                  </>
                ) : (
                  <>
                    {mode === "signin" ? "Sign In with Email" : "Create Account"}
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          )}

          {/* ── Social & Guest Divider ── */}
          <div className="my-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-white/[0.06]" />
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground/60 font-semibold">
              or connect with
            </span>
            <div className="h-px flex-1 bg-white/[0.06]" />
          </div>

          {/* Google OAuth Button */}
          <div className="space-y-2.5">
            <button
              type="button"
              onClick={handleGoogleLogin}
              disabled={googleLoading || loading}
              className="flex h-11 w-full items-center justify-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.03] text-sm font-medium text-white transition-colors hover:bg-white/[0.06] disabled:opacity-50"
            >
              {googleLoading ? (
                <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
              ) : (
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                </svg>
              )}
              <span>{googleLoading ? "Connecting..." : "Continue with Google"}</span>
            </button>

            {/* Guest Sandbox Access */}
            <button
              type="button"
              onClick={handleGuest}
              className="flex h-11 w-full items-center justify-center gap-2 rounded-xl border border-sky-400/20 bg-sky-400/[0.05] text-xs font-semibold text-sky-300 transition-colors hover:bg-sky-400/10 hover:text-sky-200"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Explore Sandbox as Guest
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
