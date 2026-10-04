import { act, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AnnualBudgetsPage } from "../src/features/annual-budgets/pages/AnnualBudgetsPage";

vi.mock("../src/features/auth/auth-context", () => {
  const user = {
    permissions: [
      "annual_budgets.view",
      "annual_budgets.create",
      "annual_budgets.update",
      "annual_budgets.submit",
    ],
  };

  const authContext = { user };

  return {
    useAuth: () => authContext,
  };
});

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => {
  const selectedFiscalYear = {
    id: "fy-1",
    code: "FY2027",
    status: "PLANNING",
  };

  const fiscalYearContext = { selectedFiscalYear };

  return {
    useFiscalYear: () => fiscalYearContext,
  };
});

vi.mock("../src/features/annual-budgets/api/annualBudgets", () => ({
  listAnnualBudgets: vi.fn().mockResolvedValue([]),
  listAnnualBudgetApprovals: vi.fn().mockResolvedValue([]),
  createAnnualBudget: vi.fn(),
  updateAnnualBudget: vi.fn(),
  submitAnnualBudget: vi.fn(),
}));

describe("AnnualBudgetsPage", () => {
  it("shows the annual budget draft form for an authorized budget admin", async () => {
    await act(async () => {
      render(
        <MemoryRouter>
          <AnnualBudgetsPage />
        </MemoryRouter>,
      );

      await Promise.resolve();
    });

    expect(screen.getByText("Buat Anggaran Tahunan")).toBeInTheDocument();
    expect(screen.getByText("FY2027")).toBeInTheDocument();
  });
});
