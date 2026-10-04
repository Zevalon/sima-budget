import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { BudgetPlanApprovalPage } from "../src/features/budget-plans/pages/BudgetPlanApprovalPage";

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => {
  const selectedFiscalYear = { id: "fy-2026", code: "FY2026", status: "PLANNING" };
  return { useFiscalYear: () => ({ selectedFiscalYear }) };
});

vi.mock("../src/features/budget-plans/api/budgetPlans", () => ({
  listPendingBudgetPlanApprovals: vi.fn().mockResolvedValue([
    {
      budget_plan: {
        id: "plan-1",
        fiscal_year_id: "fy-2026",
        fiscal_year_code: "FY2026",
        unit_allocation_id: "alloc-1",
        organization_unit_id: "unit-it",
        organization_unit_code: "IT",
        organization_unit_name: "UPT Teknologi Informasi",
        allocation_amount: "120000000000.00",
        plan_number: "DEV-FY2026-IT-001",
        status: "PENDING_APPROVAL",
        current_version_no: 1,
        row_version: 2,
        title: "Modernisasi Infrastruktur TI",
        description: null,
        total_amount: "15000000000.00",
        items: [],
        created_by: "user-pic",
        submitted_by: "user-pic",
        submitted_at: "2026-10-04T08:00:00Z",
        approved_by: null,
        approved_at: null,
        rejection_reason: null,
        created_at: "2026-10-04T07:00:00Z",
        updated_at: "2026-10-04T08:00:00Z",
      },
      approval: {
        id: "approval-1",
        budget_plan_id: "plan-1",
        plan_version_id: "version-1",
        submission_no: 1,
        version_no: 1,
        status: "PENDING",
        requested_by: "user-pic",
        requested_at: "2026-10-04T08:00:00Z",
        decided_by: null,
        decided_at: null,
        decision_note: null,
        created_at: "2026-10-04T08:00:00Z",
        updated_at: "2026-10-04T08:00:00Z",
      },
    },
  ]),
  approveBudgetPlan: vi.fn(),
  rejectBudgetPlan: vi.fn(),
}));

describe("BudgetPlanApprovalPage", () => {
  it("shows scoped pending budget plan approvals", async () => {
    render(
      <MemoryRouter>
        <BudgetPlanApprovalPage />
      </MemoryRouter>,
    );

    await waitFor(() => expect(screen.getByText("DEV-FY2026-IT-001")).toBeInTheDocument());
    expect(screen.getByText(/UPT Teknologi Informasi/)).toBeInTheDocument();
    expect(screen.getByText("Submission 1 · Versi 1")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Setujui" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Tolak" })).toBeInTheDocument();
  });
});
