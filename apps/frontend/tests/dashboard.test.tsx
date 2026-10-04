import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { DashboardPage } from "../src/features/dashboard/pages/DashboardPage";

vi.mock("../src/features/auth/auth-context", () => {
  const user = {
    permissions: ["unit_allocations.view"],
  };
  return { useAuth: () => ({ user }) };
});

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => {
  const selectedFiscalYear = {
    id: "fy-2026",
    code: "FY2026",
    status: "PLANNING",
  };
  return {
    useFiscalYear: () => ({ selectedFiscalYear }),
  };
});

vi.mock("../src/features/unit-allocations/api/unitAllocations", () => ({
  getUnitAllocationOverview: vi.fn().mockResolvedValue({
    fiscal_year_id: "fy-2026",
    fiscal_year_code: "FY2026",
    fiscal_year_status: "PLANNING",
    annual_budget_id: "budget-1",
    annual_budget_status: "APPROVED",
    annual_budget_amount: "600000000000.00",
    allocated_amount: "300000000000.00",
    remaining_amount: "300000000000.00",
    allocations: [
      {
        id: "allocation-1",
        fiscal_year_id: "fy-2026",
        annual_budget_id: "budget-1",
        organization_unit_id: "unit-1",
        organization_unit_code: "IT",
        organization_unit_name: "UPT Teknologi Informasi",
        amount: "120000000000.00",
        notes: null,
        version: 1,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
    ],
  }),
}));

describe("DashboardPage", () => {
  it("renders the selected fiscal-year budget summary", async () => {
    render(<DashboardPage />);

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(await screen.findByText("Rp 600.000.000.000,00")).toBeInTheDocument();
    expect(screen.getAllByText("Rp 300.000.000.000,00")).toHaveLength(2);
    expect(screen.getByText("50.0% dari pagu")).toBeInTheDocument();
  });
});
