import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { UnitAllocationsPage } from "../src/features/unit-allocations/pages/UnitAllocationsPage";

vi.mock("../src/features/auth/auth-context", () => {
  const user = {
    permissions: ["unit_allocations.view", "unit_allocations.create", "unit_allocations.update"],
  };
  return { useAuth: () => ({ user }) };
});

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => {
  const selectedFiscalYear = {
    id: "fy-1",
    code: "FY2027",
    status: "PLANNING",
  };
  return {
    useFiscalYear: () => ({ selectedFiscalYear }),
  };
});

vi.mock("../src/features/administration/api/admin", () => ({
  listOrganizationUnits: vi.fn().mockResolvedValue([
    {
      id: "unit-1",
      parent_id: null,
      code: "IT",
      name: "Unit IT",
      unit_type_id: "type-1",
      unit_type_code: "BUREAU",
      unit_type_name: "Bureau",
      can_receive_budget: true,
      can_create_budget_plan: true,
      is_active: true,
    },
  ]),
}));

vi.mock("../src/features/unit-allocations/api/unitAllocations", () => ({
  getUnitAllocationOverview: vi.fn().mockResolvedValue({
    fiscal_year_id: "fy-1",
    fiscal_year_code: "FY2027",
    fiscal_year_status: "PLANNING",
    annual_budget_id: "budget-1",
    annual_budget_status: "APPROVED",
    annual_budget_amount: "1000.00",
    allocated_amount: "0.00",
    remaining_amount: "1000.00",
    allocations: [],
  }),
  createUnitAllocation: vi.fn(),
  updateUnitAllocation: vi.fn(),
}));

describe("UnitAllocationsPage", () => {
  it("shows allocation form when approved budget and permissions are available", async () => {
    render(<UnitAllocationsPage />);

    expect(await screen.findByText("Alokasi Unit Baru")).toBeInTheDocument();
    expect(screen.getByText("Sisa Belum Dialokasikan")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "IT · Unit IT" })).toBeInTheDocument();
  });
});
