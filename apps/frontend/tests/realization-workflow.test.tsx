import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RealizationsPage } from "../src/features/realizations/pages/RealizationsPage";

vi.mock("../src/features/auth/auth-context", () => ({
  useAuth: () => ({
    user: {
      permissions: [
        "realizations.view",
        "realizations.create",
        "realizations.update",
        "realizations.post",
        "realizations.cancel",
        "realizations.reverse",
      ],
    },
  }),
}));

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => ({
  useFiscalYear: () => ({
    selectedFiscalYear: { id: "fy-2025", code: "FY2025", status: "ACTIVE" },
  }),
}));

vi.mock("../src/features/realizations/api/realizations", () => {
  const base = {
    fiscal_year_id: "fy-2025",
    fiscal_year_code: "FY2025",
    budget_plan_id: "plan-1",
    plan_version_id: "version-1",
    plan_number: "BP-FY2025-IT-001",
    plan_title: "Operasional TI",
    plan_approved_amount: "1000.00",
    plan_realized_amount: "250.00",
    plan_draft_pipeline_amount: "0.00",
    plan_remaining_amount: "750.00",
    organization_unit_id: "unit-it",
    organization_unit_code: "IT",
    organization_unit_name: "UPT Teknologi Informasi",
    realization_date: "2025-04-01",
    reference_number: "DOC-001",
    description: "Verification realization",
    vendor_name: null,
    amount: "250.00",
    created_by: "user-1",
    posted_by: "user-1",
    posted_at: "2025-04-01T00:00:00Z",
    correction_of_id: null,
    correction_id: null,
    cancelled_by: null,
    cancelled_at: null,
    cancellation_reason: null,
    reversed_by: null,
    reversed_at: null,
    reversal_reason: null,
    created_at: "2025-04-01T00:00:00Z",
    updated_at: "2025-04-01T00:00:00Z",
  };

  return {
    getRealizationContext: vi.fn().mockResolvedValue({
      fiscal_year_id: "fy-2025",
      fiscal_year_code: "FY2025",
      fiscal_year_status: "ACTIVE",
      scope_approved_amount: "1000.00",
      scope_realized_amount: "250.00",
      scope_draft_pipeline_amount: "0.00",
      scope_utilization_percent: "25.00",
      scope_remaining_amount: "750.00",
      plans: [],
    }),
    listRealizations: vi.fn().mockResolvedValue([
      {
        ...base,
        id: "realization-posted",
        realization_number: "RLZ-POSTED",
        status: "POSTED",
        row_version: 2,
      },
      {
        ...base,
        id: "realization-reversed",
        realization_number: "RLZ-REVERSED",
        status: "REVERSED",
        row_version: 3,
        reversed_by: "user-1",
        reversed_at: "2025-04-02T00:00:00Z",
        reversal_reason: "Nominal perlu dikoreksi.",
      },
    ]),
    createRealization: vi.fn(),
    updateRealization: vi.fn(),
    postRealization: vi.fn(),
    cancelRealization: vi.fn(),
    reverseRealization: vi.fn(),
    createCorrectionDraft: vi.fn(),
  };
});

describe("Realization correction workflow", () => {
  it("shows reversal and correction actions for eligible records", async () => {
    render(<RealizationsPage />);

    expect(await screen.findByText("RLZ-POSTED")).toBeInTheDocument();
    expect(screen.getByText("Reversal Posting")).toBeInTheDocument();
    expect(screen.getByText("Buat Draft Koreksi")).toBeInTheDocument();
    expect(screen.getByText(/Nominal perlu dikoreksi/)).toBeInTheDocument();
  });
});
