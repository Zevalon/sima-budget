import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AnnualBudgetApprovalPage } from "../src/features/annual-budgets/pages/AnnualBudgetApprovalPage";

vi.mock("../src/features/annual-budgets/api/annualBudgets", () => ({
  listPendingAnnualBudgets: vi.fn().mockResolvedValue([
    {
      id: "budget-1",
      fiscal_year_id: "fy-1",
      fiscal_year_code: "FY2027",
      amount: "500000000000.25",
      notes: null,
      status: "PENDING_APPROVAL",
      version: 1,
      submitted_by: "user-1",
      submitted_at: "2026-10-04T08:00:00Z",
      approved_by: null,
      approved_at: null,
      rejection_reason: null,
      created_at: "2026-10-04T07:00:00Z",
      updated_at: "2026-10-04T08:00:00Z",
    },
  ]),
  approveAnnualBudget: vi.fn(),
  rejectAnnualBudget: vi.fn(),
}));

describe("AnnualBudgetApprovalPage", () => {
  it("shows pending annual budget approvals", async () => {
    render(
      <MemoryRouter>
        <AnnualBudgetApprovalPage />
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText("FY2027")).toBeInTheDocument());
    expect(screen.getByRole("button", { name: "Setujui" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tolak" })).toBeInTheDocument();
  });
});
