import API from "./client";
import { getSupabase } from "@/lib/supabase-client";

export async function login(email: string, password: string) {
  const response = await fetch(`${API}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  localStorage.setItem("token", data.access_token);
  localStorage.setItem("access_token", data.access_token);

  return data;
}

export async function register(
  username: string,
  email: string,
  password: string
) {
  const response = await fetch(`${API}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Registration failed");
  }

  return data;
}

export async function googleLogin() {
  const supabase = getSupabase();

  const redirectTo =
    typeof window !== "undefined"
      ? `${window.location.origin}/auth/callback`
      : "http://localhost:3000/auth/callback";

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo,
      queryParams: {
        access_type: "offline",
        prompt: "consent",
      },
    },
  });

  if (error) {
    throw new Error(error.message || "Google sign-in failed");
  }

  return data;
}

export async function logout() {
  const supabase = getSupabase();
  await supabase.auth.signOut();
  localStorage.removeItem("token");
  localStorage.removeItem("access_token");
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function isLoggedIn(): boolean {
  return !!getToken();
}
