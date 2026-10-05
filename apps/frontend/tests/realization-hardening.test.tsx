import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RealizationsPage } from "../src/features/realizations/pages/RealizationsPage";

const mocks = vi.hoisted(() => ({
  selectedFiscalYear: {
    id: "fy-2025",
    code: "FY2025",
    status: "ACTIVE",
  },
  getRealizationContext: vi.fn(),
  listRealizations: vi.fn(),
  reverseRealization: vi.fn(),
}));

vi.mock("../src/features/auth/auth-context", () => ({
  useAuth: () => ({
    user: {
      permissions: ["realizations.view", "realizations.reverse"],
    },
  }),
}));

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => ({
  useFiscalYear: () => ({
    selectedFiscalYear: mocks.selectedFiscalYear,
  }),
}));

vi.mock("../src/features/realizations/api/realizations", () => ({
  getRealizationContext: mocks.getRealizationContext,
  listRealizations: mocks.listRealizations,
  createRealization: vi.fn(),
  updateRealization: vi.fn(),
  postRealization: vi.fn(),
  cancelRealization: vi.fn(),
  reverseRealization: mocks.reverseRealization,
  createCorrectionDraft: vi.fn(),
}));

afterEach(() => {
  vi.restoreAllMocks();
  mocks.getRealizationContext.mockReset();
  mocks.listRealizations.mockReset();
  mocks.reverseRealization.mockReset();
});

describe("Realization workflow identity", () => {
  it("sends the exact row, status, and plan-version snapshot for reversal", async () => {
    const context = {
      fiscal_year_id: "fy-2025",
      fiscal_year_code: "FY2025",
      fiscal_year_status: "ACTIVE",
      scope_approved_amount: "1000.00",
      scope_realized_amount: "250.00",
      scope_draft_pipeline_amount: "0.00",
      scope_remaining_amount: "750.00",
      scope_utilization_percent: "25.00",
      plans: [],
    };

    const postedRealization = {
      id: "realization-posted",
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
      realization_number: "RLZ-POSTED",
      status: "POSTED",
      realization_date: "2025-04-01",
      reference_number: "DOC-001",
      description: "Verification realization",
      vendor_name: null,
      amount: "250.00",
      row_version: 2,
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

    const reversedRealization = {
      ...postedRealization,
      status: "REVERSED",
      row_version: 3,
      reversed_by: "user-1",
      reversed_at: "2025-04-02T00:00:00Z",
      reversal_reason: "Dokumen perlu dikoreksi.",
    };

    mocks.getRealizationContext.mockResolvedValue(context);
    mocks.listRealizations
      .mockResolvedValueOnce([postedRealization])
      .mockResolvedValue([reversedRealization]);
    mocks.reverseRealization.mockResolvedValue({});

    vi.spyOn(window, "prompt").mockReturnValue("Dokumen perlu dikoreksi.");
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<RealizationsPage />);

    fireEvent.click(await screen.findByText("Reversal Posting"));

    await waitFor(() => {
      expect(mocks.reverseRealization).toHaveBeenCalledWith(
        "realization-posted",
        2,
        "POSTED",
        "version-1",
        "Dokumen perlu dikoreksi.",
      );
    });

    expect(await screen.findByText("REVERSED")).toBeInTheDocument();
    expect(
      await screen.findByText("Alasan reversal: Dokumen perlu dikoreksi."),
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(mocks.getRealizationContext).toHaveBeenCalledTimes(2);
      expect(mocks.listRealizations).toHaveBeenCalledTimes(2);
    });
  });
});
