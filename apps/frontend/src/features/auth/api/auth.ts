import { apiRequest, setCsrfToken } from "../../../lib/api/client";
import type { AuthUser } from "../types";

export async function login(username: string, password: string): Promise<AuthUser> {
  const result = await apiRequest<AuthUser>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setCsrfToken(result.csrf_token);
  return result;
}

export async function getCurrentUser(): Promise<AuthUser> {
  const result = await apiRequest<AuthUser>("/auth/me");
  setCsrfToken(result.csrf_token);
  return result;
}

export async function logout(): Promise<void> {
  await apiRequest<void>(
    "/auth/logout",
    {
      method: "POST",
    },
    { csrf: true },
  );
  setCsrfToken(null);
}
