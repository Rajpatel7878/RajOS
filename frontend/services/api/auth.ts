import API from "./client";

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
