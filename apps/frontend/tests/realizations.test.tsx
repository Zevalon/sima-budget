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

vi.mock("../src/features/realizations/api/realizations", () => ({
  getRealizationContext: vi.fn().mockResolvedValue({
    fiscal_year_id: "fy-2025",
    fiscal_year_code: "FY2025",
    fiscal_year_status: "ACTIVE",
    scope_approved_amount: "1000.00",
    scope_realized_amount: "250.00",
    scope_draft_pipeline_amount: "100.00",
    scope_utilization_percent: "25.00",
    scope_remaining_amount: "750.00",
    plans: [
      {
        budget_plan_id: "plan-1",
        plan_version_id: "version-1",
        organization_unit_id: "unit-it",
        organization_unit_code: "IT",
        organization_unit_name: "UPT Teknologi Informasi",
        plan_number: "BP-FY2025-IT-001",
        title: "Operasional TI",
        approved_amount: "1000.00",
        realized_amount: "250.00",
        draft_pipeline_amount: "100.00",
        remaining_amount: "750.00",
        utilization_percent: "25.00",
      },
    ],
  }),
  listRealizations: vi.fn().mockResolvedValue([]),
  createRealization: vi.fn(),
  updateRealization: vi.fn(),
  postRealization: vi.fn(),
  cancelRealization: vi.fn(),
  reverseRealization: vi.fn(),
  createCorrectionDraft: vi.fn(),
}));

describe("RealizationsPage", () => {
  it("shows realization form for an active fiscal year with approved plans", async () => {
    render(<RealizationsPage />);

    expect(await screen.findByText("Draft Realisasi Baru")).toBeInTheDocument();
    expect(screen.getByText("Rp 1.000,00")).toBeInTheDocument();
    expect(screen.getByText("Rp 750,00")).toBeInTheDocument();
    expect(screen.getByText("0 record")).toBeInTheDocument();
  });
});
