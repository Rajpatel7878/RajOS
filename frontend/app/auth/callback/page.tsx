"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { getSupabase } from "@/lib/supabase-client";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Completing Google sign-in...");

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const supabase = getSupabase();

        // Exchange the code from URL into a session
        const { data: sessionData, error: sessionError } =
          await supabase.auth.getSession();

        if (sessionError) throw sessionError;

        const session = sessionData?.session;

        if (!session?.user) {
          throw new Error("No session found after Google sign-in.");
        }

        const user = session.user;
        const email = user.email ?? "";
        const name =
          user.user_metadata?.full_name ||
          user.user_metadata?.name ||
          email.split("@")[0];
        const googleId = user.id;

        setMessage("Syncing your account with RajOS...");

        // Call the RajOS backend to create/retrieve the user and get a JWT
        const res = await fetch(`${API}/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            name,
            google_id: googleId,
          }),
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || "Backend sync failed");
        }

        const data = await res.json();
        const token = data.access_token;

        if (token) {
          localStorage.setItem("token", token);
          localStorage.setItem("access_token", token);
          setStatus("success");
          setMessage(
            data.is_new
              ? `Welcome to RajOS, ${name}! 🎉`
              : `Welcome back, ${name}!`
          );
          setTimeout(() => router.push("/dashboard"), 1200);
        } else {
          throw new Error("No access token received from backend");
        }
      } catch (err) {
        console.error("OAuth callback error:", err);
        setStatus("error");
        setMessage(
          err instanceof Error
            ? err.message
            : "Sign-in failed. Please try again."
        );
        setTimeout(() => router.push("/login"), 3000);
      }
    };

    handleCallback();
  }, [router]);

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background">
      {/* Background */}
      <div className="pointer-events-none fixed inset-0 grid-bg opacity-[0.12]" />
      <motion.div
        className="pointer-events-none fixed left-[-10%] top-[10%] h-[500px] w-[500px] rounded-full bg-sky-500/15 blur-[140px]"
        animate={{ x: [0, 40, 0], y: [0, 20, 0] }}
        transition={{ duration: 8, repeat: Infinity }}
      />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 flex flex-col items-center gap-6 px-6 text-center"
      >
        {/* Logo */}
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 to-cyan-500 shadow-lg shadow-sky-500/30">
          <Sparkles className="h-8 w-8 text-white" />
        </div>

        <div className="space-y-2">
          <h1 className="text-2xl font-bold text-white">
            {status === "loading" && "Signing you in..."}
            {status === "success" && "All set!"}
            {status === "error" && "Something went wrong"}
          </h1>
          <p className="max-w-xs text-sm text-muted-foreground">{message}</p>
        </div>

        {/* Animated status icon */}
        <motion.div
          key={status}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          {status === "loading" && (
            <Loader2 className="h-10 w-10 animate-spin text-sky-400" />
          )}
          {status === "success" && (
            <CheckCircle2 className="h-10 w-10 text-emerald-400" />
          )}
          {status === "error" && (
            <AlertCircle className="h-10 w-10 text-rose-400" />
          )}
        </motion.div>

        {status === "error" && (
          <p className="text-xs text-muted-foreground">
            Redirecting back to login in 3 seconds...
          </p>
        )}

        {status === "success" && (
          <p className="text-xs text-muted-foreground">
            Redirecting to dashboard...
          </p>
        )}
      </motion.div>
    </div>
  );
}
