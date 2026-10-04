import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { BudgetPlansPage } from "../src/features/budget-plans/pages/BudgetPlansPage";

vi.mock("../src/features/auth/auth-context", () => {
  const user = {
    permissions: ["budget_plans.view", "budget_plans.create", "budget_plans.update"],
  };
  return { useAuth: () => ({ user }) };
});

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => {
  const selectedFiscalYear = { id: "fy-2026", code: "FY2026", status: "PLANNING" };
  return { useFiscalYear: () => ({ selectedFiscalYear }) };
});

vi.mock("../src/features/budget-plans/api/budgetPlans", () => ({
  getBudgetPlanContext: vi.fn().mockResolvedValue({
    fiscal_year_id: "fy-2026",
    fiscal_year_code: "FY2026",
    fiscal_year_status: "PLANNING",
    allocations: [
      {
        unit_allocation_id: "alloc-it",
        organization_unit_id: "unit-it",
        organization_unit_code: "IT",
        organization_unit_name: "UPT Teknologi Informasi",
        allocation_amount: "120000000000.00",
      },
    ],
    budget_categories: [{ id: "cat-it", code: "IT", name: "Teknologi Informasi" }],
    units_of_measure: [{ id: "uom-unit", code: "UNIT", name: "Unit" }],
  }),
  listBudgetPlans: vi.fn().mockResolvedValue([]),
  createBudgetPlan: vi.fn(),
  updateBudgetPlan: vi.fn(),
}));

describe("BudgetPlansPage", () => {
  it("shows a scoped draft form after planning context loads", async () => {
    render(
      <MemoryRouter>
        <BudgetPlansPage />
      </MemoryRouter>,
    );

    expect(await screen.findByText("Buat Draft Rencana Anggaran")).toBeInTheDocument();
    expect(screen.getByText("0 rencana dalam scope Anda")).toBeInTheDocument();
  });
});
