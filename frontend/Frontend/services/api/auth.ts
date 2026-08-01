import api from "./client";

export async function login(email: string, password: string) {
  const response = await api.post("/login", {
    email,
    password,
  });

  return response.data;
}

export async function register(
  username: string,
  email: string,
  password: string
) {
  const response = await api.post("/register", {
    username,
    email,
    password,
  });

  return response.data;
}
