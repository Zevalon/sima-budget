import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AdministrationHomePage } from "../src/features/administration/pages/AdministrationHomePage";
import { AuthContext, type AuthContextValue } from "../src/features/auth/auth-context";

describe("foundation administration navigation", () => {
  it("shows audit and settings according to permissions", () => {
    const context: AuthContextValue = {
      status: "authenticated",
      user: {
        id: "user-1",
        username: "auditor",
        email: null,
        full_name: "Auditor",
        organization_id: "org-1",
        organization_name: "Organization",
        roles: [],
        permissions: ["settings.view", "audit.view"],
        unit_memberships: [],
        session_expires_at: new Date().toISOString(),
        csrf_token: "csrf",
      },
      login: () => Promise.resolve(),
      logout: () => Promise.resolve(),
    };

    render(
      <AuthContext.Provider value={context}>
        <MemoryRouter>
          <AdministrationHomePage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByRole("heading", { name: "Pengaturan Aplikasi" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Audit Log" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Pengguna" })).not.toBeInTheDocument();
  });
});
