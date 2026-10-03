import { type PropsWithChildren, useEffect, useMemo, useState } from "react";

import { ApiError, setCsrfToken } from "../../lib/api/client";
import * as authApi from "./api/auth";
import { AuthContext, type AuthContextValue, type AuthStatus } from "./auth-context";
import type { AuthUser } from "./types";

export function AuthProvider({ children }: PropsWithChildren) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let active = true;

    void authApi
      .getCurrentUser()
      .then((currentUser) => {
        if (!active) return;
        setUser(currentUser);
        setStatus("authenticated");
      })
      .catch((error: unknown) => {
        if (!active) return;

        if (error instanceof ApiError && error.status === 401) {
          setCsrfToken(null);
          setUser(null);
          setStatus("anonymous");
          return;
        }

        setCsrfToken(null);
        setUser(null);
        setStatus("anonymous");
      });

    return () => {
      active = false;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user,
      async login(username: string, password: string) {
        const loggedInUser = await authApi.login(username, password);
        setUser(loggedInUser);
        setStatus("authenticated");
      },
      async logout() {
        try {
          await authApi.logout();
        } finally {
          setCsrfToken(null);
          setUser(null);
          setStatus("anonymous");
        }
      },
    }),
    [status, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
