'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Mail, Lock, ArrowRight, Loader2, Eye, EyeOff, User, CheckCircle2, AlertCircle, Smartphone, KeyRound } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { login, register, googleLogin } from '@/services/api/auth';

type Mode = 'signin' | 'signup';

export const dynamic = 'force-dynamic';

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>('signin');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Phone OTP state
  const [phoneMode, setPhoneMode] = useState(false);
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [phoneLoading, setPhoneLoading] = useState(false);

  useEffect(() => {
    if (sessionStorage.getItem('rajos_guest') === '1') {
      router.push('/dashboard');
    }
  }, [router]);

  const handleGuest = useCallback(() => {
    sessionStorage.setItem('rajos_guest', '1');
    router.push('/dashboard');
  }, [router]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      if (mode === 'signup') {
        await register(username, email, password);
        setSuccess('Account created! Please sign in.');
        setMode('signin');
        setPassword('');
      } else {
        await login(email, password);
        setSuccess('Welcome back! Redirecting...');
        setTimeout(() => router.push('/dashboard'), 800);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong';

      if (message === 'User not found') {
        setError('No account found with this email. Please sign up first.');
      } else if (message === 'Wrong password') {
        setError('Incorrect password. Please try again.');
      } else if (message.includes('Email already registered')) {
        setError('An account with this email already exists. Try signing in instead.');
      } else if (message.includes('fetch') || message.includes('Failed to fetch')) {
        setError('Cannot reach the RajOS backend. Make sure the backend is running on port 8000.');
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  }, [mode, username, email, password, router]);

  const handleGoogleLogin = useCallback(async () => {
    setError(null);
    setSuccess(null);
    setGoogleLoading(true);
    try {
      await googleLogin();
      // googleLogin() redirects the browser to Google — page will navigate away
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Google sign-in failed';
      if (message.includes('fetch') || message.includes('Failed to fetch')) {
        setError('Cannot reach sign-in provider. Check your internet connection.');
      } else {
        setError(message);
      }
      setGoogleLoading(false);
    }
  }, []);

  const handleSendOTP = useCallback(async () => {
    setError(null);
    setPhoneLoading(true);
    try {
      const supabase = (await import('@/lib/supabase-client')).getSupabase();
      const formatted = phone.startsWith('+') ? phone : `+91${phone}`;
      const { error: otpError } = await supabase.auth.signInWithOtp({ phone: formatted });
      if (otpError) throw otpError;
      setOtpSent(true);
      setSuccess(`OTP sent to ${formatted}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to send OTP';
      setError(msg.includes('Phone') || msg.includes('provider') 
        ? 'Phone auth not enabled. Enable SMS in Supabase dashboard.' 
        : msg);
    } finally {
      setPhoneLoading(false);
    }
  }, [phone]);

  const handleVerifyOTP = useCallback(async () => {
    setError(null);
    setPhoneLoading(true);
    try {
      const supabase = (await import('@/lib/supabase-client')).getSupabase();
      const formatted = phone.startsWith('+') ? phone : `+91${phone}`;
      const { data, error: verifyError } = await supabase.auth.verifyOtp({
        phone: formatted,
        token: otp,
        type: 'sms',
      });
      if (verifyError) throw verifyError;
      const userId = data.user?.id || '';
      // Sync with RajOS backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${apiUrl}/auth/phone/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: formatted, supabase_user_id: userId, name: '' }),
      });
      if (res.ok) {
        const d = await res.json();
        localStorage.setItem('token', d.access_token);
        localStorage.setItem('access_token', d.access_token);
      }
      setSuccess('Verified! Redirecting...');
      setTimeout(() => router.push('/dashboard'), 800);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OTP verification failed');
    } finally {
      setPhoneLoading(false);
    }
  }, [phone, otp, router]);

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-6 py-12">
      {/* Background layers */}
      <div className="pointer-events-none fixed inset-0 z-0 grid-bg opacity-[0.12]" />
      <div className="pointer-events-none fixed inset-0 z-0 bg-gradient-to-b from-sky-950/30 via-transparent to-background" />

      {/* Animated background orbs */}
      <motion.div
        className="pointer-events-none fixed left-[-10%] top-[10%] z-0 h-[500px] w-[500px] rounded-full bg-sky-500/15 blur-[140px]"
        animate={{ x: [0, 80, -30, 0], y: [0, 40, 60, 0], scale: [1, 1.1, 0.95, 1] }}
        transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="pointer-events-none fixed right-[-10%] bottom-[5%] z-0 h-[400px] w-[400px] rounded-full bg-cyan-500/10 blur-[120px]"
        animate={{ x: [0, -60, 30, 0], y: [0, -40, 20, 0], scale: [1, 0.9, 1.15, 1] }}
        transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Logo / back link */}
      <Link
        href="/"
        className="absolute left-6 top-6 z-20 flex items-center gap-2.5"
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 shadow-lg shadow-sky-500/30">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <span className="text-lg font-bold tracking-tight text-white">RajOS</span>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="glass-card relative overflow-hidden p-8 sm:p-10">
          {/* Top accent line */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-400/60 to-transparent" />

          {/* Heading */}
          <div className="mb-8 text-center">
            <motion.h1
              key={mode}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="text-2xl font-bold tracking-tight text-white"
            >
              {mode === 'signin' ? 'Welcome back' : 'Create your account'}
            </motion.h1>
            <motion.p
              key={`${mode}-sub`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="mt-2 text-sm text-muted-foreground"
            >
              {mode === 'signin'
                ? 'Sign in to your AI operating system'
                : 'Start building with your intelligent workspace'}
            </motion.p>
          </div>

          {/* Mode toggle */}
          <div className="mb-7 flex rounded-xl border border-white/[0.06] bg-white/[0.02] p-1">
            {(['signin', 'signup'] as Mode[]).map((m) => (
              <button
                key={m}
                onClick={() => {
                  setMode(m);
                  setError(null);
                  setSuccess(null);
                }}
                className={cn(
                  'relative flex-1 rounded-lg py-2 text-sm font-medium transition-colors',
                  mode === m ? 'text-white' : 'text-muted-foreground hover:text-white'
                )}
              >
                {mode === m && (
                  <motion.div
                    layoutId="mode-pill"
                    className="absolute inset-0 rounded-lg bg-gradient-to-r from-sky-500/20 to-cyan-500/20 ring-1 ring-sky-400/30"
                    transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                  />
                )}
                <span className="relative z-10">
                  {m === 'signin' ? 'Sign In' : 'Sign Up'}
                </span>
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                  animate={{ opacity: 1, height: 'auto', marginBottom: 20 }}
                  exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                  className="flex items-start gap-3 overflow-hidden rounded-xl border border-rose-500/20 bg-rose-500/[0.08] px-4 py-3"
                >
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" />
                  <p className="text-sm text-rose-300">{error}</p>
                </motion.div>
              )}
              {success && (
                <motion.div
                  initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                  animate={{ opacity: 1, height: 'auto', marginBottom: 20 }}
                  exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                  className="flex items-start gap-3 overflow-hidden rounded-xl border border-emerald-500/20 bg-emerald-500/[0.08] px-4 py-3"
                >
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                  <p className="text-sm text-emerald-300">{success}</p>
                </motion.div>
              )}
            </AnimatePresence>

            {mode === 'signup' && (
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium text-muted-foreground">
                  Username
                </Label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    autoComplete="username"
                    className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50 focus:ring-sky-400/20"
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-muted-foreground">
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
                  autoComplete="email"
                  className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50 focus:ring-sky-400/20"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-muted-foreground">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={mode === 'signup' ? 'At least 6 characters' : 'Enter your password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                  className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 pr-11 text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50 focus:ring-sky-400/20"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-white"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {mode === 'signin' && (
              <div className="flex justify-end">
                <button
                  type="button"
                  className="text-xs font-medium text-muted-foreground transition-colors hover:text-sky-400"
                >
                  Forgot password?
                </button>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="group relative h-11 w-full gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-sm font-semibold text-white shadow-lg shadow-sky-500/20 transition-all hover:shadow-sky-500/40 hover:from-sky-400 hover:to-cyan-400 disabled:opacity-60"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Please wait...
                </>
              ) : (
                <>
                  {mode === 'signin' ? 'Sign In' : 'Create Account'}
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </Button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center gap-4">
            <div className="h-px flex-1 bg-white/[0.06]" />
            <span className="text-xs text-muted-foreground">or</span>
            <div className="h-px flex-1 bg-white/[0.06]" />
          </div>

          {/* Social buttons */}
          {!phoneMode ? (
            <div className="space-y-3">
              <button
                type="button"
                onClick={handleGoogleLogin}
                disabled={googleLoading || loading}
                className="flex h-11 w-full items-center justify-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.03] text-sm font-medium text-white transition-colors hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {googleLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                ) : (
                  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                  </svg>
                )}
                {googleLoading ? 'Connecting to Google...' : 'Continue with Google'}
              </button>

              <button
                type="button"
                onClick={() => { setPhoneMode(true); setError(null); setSuccess(null); }}
                className="flex h-11 w-full items-center justify-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.03] text-sm font-medium text-white transition-colors hover:bg-white/[0.06]"
              >
                <Smartphone className="h-4 w-4 text-emerald-400" />
                Continue with Phone (OTP)
              </button>
            </div>
          ) : (
            /* Phone OTP panel */
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-white">
                <Smartphone className="h-4 w-4 text-emerald-400" />
                <span className="font-medium">Phone Sign-In</span>
                <button
                  onClick={() => { setPhoneMode(false); setOtpSent(false); setPhone(''); setOtp(''); setError(null); setSuccess(null); }}
                  className="ml-auto text-xs text-muted-foreground hover:text-white"
                >
                  ← Back
                </button>
              </div>

              {!otpSent ? (
                <>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-muted-foreground">Phone Number</Label>
                    <div className="relative flex gap-2">
                      <span className="flex h-11 items-center rounded-xl border border-white/[0.08] bg-white/[0.03] px-3 text-sm text-muted-foreground">
                        +91
                      </span>
                      <Input
                        type="tel"
                        placeholder="9876543210"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
                        maxLength={10}
                        className="h-11 flex-1 border-white/[0.08] bg-white/[0.03] text-white placeholder:text-muted-foreground/60 focus:border-sky-400/50"
                      />
                    </div>
                    <p className="text-[11px] text-muted-foreground">OTP will be encrypted and sent via SMS</p>
                  </div>
                  <Button
                    onClick={handleSendOTP}
                    disabled={phoneLoading || phone.length < 10}
                    className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-semibold text-white hover:from-emerald-400 hover:to-teal-400 disabled:opacity-60"
                  >
                    {phoneLoading ? <><Loader2 className="h-4 w-4 animate-spin" /> Sending...</> : <><Smartphone className="h-4 w-4" /> Send OTP</>}
                  </Button>
                </>
              ) : (
                <>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-muted-foreground">Enter 6-digit OTP</Label>
                    <div className="relative">
                      <KeyRound className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        type="text"
                        placeholder="123456"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        maxLength={6}
                        className="h-11 border-white/[0.08] bg-white/[0.03] pl-11 text-center text-lg font-bold tracking-[0.5em] text-white placeholder:text-muted-foreground/40 focus:border-emerald-400/50"
                      />
                    </div>
                    <p className="text-[11px] text-muted-foreground">
                      Sent to +91{phone} ·{' '}
                      <button
                        onClick={() => setOtpSent(false)}
                        className="text-sky-400 hover:underline"
                      >
                        Change number
                      </button>
                    </p>
                  </div>
                  <Button
                    onClick={handleVerifyOTP}
                    disabled={phoneLoading || otp.length < 6}
                    className="h-11 w-full gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-sm font-semibold text-white hover:from-emerald-400 hover:to-teal-400 disabled:opacity-60"
                  >
                    {phoneLoading ? <><Loader2 className="h-4 w-4 animate-spin" /> Verifying...</> : <><CheckCircle2 className="h-4 w-4" /> Verify & Sign In</>}
                  </Button>
                </>
              )}
            </div>
          )}

          {/* Guest mode */}
          <div className="mt-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-white/[0.06]" />
            <span className="text-xs text-muted-foreground">or</span>
            <div className="h-px flex-1 bg-white/[0.06]" />
          </div>
          <button
            onClick={handleGuest}
            className="mt-5 flex h-11 w-full items-center justify-center gap-2 rounded-xl border border-sky-400/20 bg-sky-400/[0.06] text-sm font-medium text-sky-300 transition-all hover:border-sky-400/40 hover:bg-sky-400/10 hover:text-sky-200"
          >
            <Sparkles className="h-4 w-4" />
            Continue as Guest
          </button>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            {mode === 'signin' ? "Don't have an account? " : 'Already have an account? '}
            <button
              onClick={() => {
                setMode(mode === 'signin' ? 'signup' : 'signin');
                setError(null);
                setSuccess(null);
              }}
              className="font-medium text-sky-400 transition-colors hover:text-sky-300"
            >
              {mode === 'signin' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>

        {/* Floating decorative icons */}
        <motion.div
          className="pointer-events-none absolute -left-12 -top-12 hidden lg:block"
          animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
          transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] backdrop-blur-md">
            <User className="h-5 w-5 text-sky-400/50" />
          </div>
        </motion.div>
        <motion.div
          className="pointer-events-none absolute -right-10 top-20 hidden lg:block"
          animate={{ y: [0, 12, 0], rotate: [0, -5, 0] }}
          transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] backdrop-blur-md">
            <Lock className="h-5 w-5 text-cyan-400/50" />
          </div>
        </motion.div>
        <motion.div
          className="pointer-events-none absolute -bottom-8 -right-6 hidden lg:block"
          animate={{ y: [0, -8, 0], rotate: [0, 8, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/[0.08] bg-white/[0.03] backdrop-blur-md">
            <Sparkles className="h-5 w-5 text-sky-400/50" />
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
