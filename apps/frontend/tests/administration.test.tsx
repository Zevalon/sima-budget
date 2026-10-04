import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AdministrationHomePage } from "../src/features/administration/pages/AdministrationHomePage";
import { AuthContext, type AuthContextValue } from "../src/features/auth/auth-context";

const baseUser = {
  id: "user-1",
  username: "admin",
  email: null,
  full_name: "System Admin",
  organization_id: "org-1",
  organization_name: "Universitas / Organisasi",
  application_name: "Sistem Informasi Monitoring Anggaran",
  application_short_name: "SIMA",
  organization_display_name: "Universitas / Organisasi",
  roles: [],
  permissions: ["users.view", "organization_units.view"],
  unit_memberships: [],
  session_expires_at: new Date().toISOString(),
  csrf_token: "csrf",
};

describe("AdministrationHomePage", () => {
  it("shows only sections allowed by permissions", () => {
    const context: AuthContextValue = {
      status: "authenticated",
      user: baseUser,
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

    expect(screen.getByRole("heading", { name: "Pengguna" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Unit Organisasi" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Role & Permission" })).not.toBeInTheDocument();
  });
});
