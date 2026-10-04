import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AuthContext, type AuthContextValue } from "../src/features/auth/auth-context";
import { MasterDataHomePage } from "../src/features/budget-foundation/pages/MasterDataHomePage";

const user = {
  id: "user-1",
  username: "budget",
  email: null,
  full_name: "Budget Admin",
  organization_id: "org-1",
  organization_name: "Organization",
  application_name: "SIMA",
  application_short_name: "SIMA",
  organization_display_name: "Organization",
  roles: [],
  permissions: ["fiscal_years.view", "budget_categories.view"],
  unit_memberships: [],
  session_expires_at: new Date().toISOString(),
  csrf_token: "csrf",
};

describe("MasterDataHomePage", () => {
  it("shows only master data allowed by permissions", () => {
    const context: AuthContextValue = {
      status: "authenticated",
      user,
      login: () => Promise.resolve(),
      logout: () => Promise.resolve(),
    };

    render(
      <AuthContext.Provider value={context}>
        <MemoryRouter>
          <MasterDataHomePage />
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByRole("heading", { name: "Tahun Anggaran" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Kategori Anggaran" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Satuan" })).not.toBeInTheDocument();
  });
});
