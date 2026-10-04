import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AuthContext, type AuthContextValue } from "../src/features/auth/auth-context";
import { PermissionRoute } from "../src/features/auth/PermissionRoute";

const context: AuthContextValue = {
  status: "authenticated",
  user: {
    id: "user-1",
    username: "viewer",
    email: null,
    full_name: "Viewer",
    organization_id: "org-1",
    organization_name: "Organization",
    application_name: "Sistem Informasi Monitoring Anggaran",
    application_short_name: "SIMA",
    organization_display_name: "Organization",
    roles: [],
    permissions: ["settings.view"],
    unit_memberships: [],
    session_expires_at: new Date().toISOString(),
    csrf_token: "csrf",
  },
  login: () => Promise.resolve(),
  logout: () => Promise.resolve(),
};

describe("PermissionRoute", () => {
  it("shows an explicit access denied state when permission is missing", () => {
    render(
      <AuthContext.Provider value={context}>
        <MemoryRouter initialEntries={["/restricted"]}>
          <Routes>
            <Route element={<PermissionRoute anyOf={["users.view"]} />}>
              <Route path="/restricted" element={<div>Restricted content</div>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByRole("heading", { name: /tidak memiliki permission/i })).toBeInTheDocument();
    expect(screen.queryByText("Restricted content")).not.toBeInTheDocument();
  });
});
