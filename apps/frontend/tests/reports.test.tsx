import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ReportsPage } from "../src/features/reports/pages/ReportsPage";

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => {
  const selectedFiscalYear = {
    id: "fy-2025",
    code: "FY2025",
    status: "ACTIVE",
  };
  return { useFiscalYear: () => ({ selectedFiscalYear }) };
});

vi.mock("../src/features/reports/api/reports", () => ({
  getFinancialSummary: vi.fn().mockResolvedValue({
    fiscal_year_id: "fy-2025",
    fiscal_year_code: "FY2025",
    fiscal_year_status: "ACTIVE",
    annual_budget_id: "budget-1",
    annual_budget_status: "APPROVED",
    organization_annual_budget_amount: "500000000000.00",
    scope_budget_amount: "120000000000.00",
    allocated_amount: "120000000000.00",
    unallocated_amount: "0.00",
    committed_amount: "30000000000.00",
    draft_pipeline_amount: "5000000000.00",
    available_amount: "90000000000.00",
    realized_amount: "12000000000.00",
    realization_draft_pipeline_amount: "1000000000.00",
    remaining_to_realize_amount: "18000000000.00",
    utilization_percent: "40.00",
    allocation_count: 1,
    approved_plan_count: 1,
    realization_count: 2,
    unit_summaries: [
      {
        organization_unit_id: "unit-it",
        organization_unit_code: "IT",
        organization_unit_name: "UPT Teknologi Informasi",
        allocated_amount: "120000000000.00",
        committed_amount: "30000000000.00",
        draft_pipeline_amount: "5000000000.00",
        available_amount: "90000000000.00",
        realized_amount: "12000000000.00",
        realization_draft_pipeline_amount: "1000000000.00",
        remaining_to_realize_amount: "18000000000.00",
        utilization_percent: "40.00",
      },
    ],
    monthly_realization: Array.from({ length: 12 }, (_, index) => ({
      month: index + 1,
      month_label: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "Mei",
        "Jun",
        "Jul",
        "Agu",
        "Sep",
        "Okt",
        "Nov",
        "Des",
      ][index],
      realized_amount: index === 0 ? "12000000000.00" : "0.00",
    })),
    category_plan_summaries: [],
  }),
}));

describe("ReportsPage", () => {
  it("renders canonical financial summary for selected fiscal year", async () => {
    render(<ReportsPage />);

    expect(screen.getByRole("heading", { name: "Laporan Anggaran" })).toBeInTheDocument();
    expect((await screen.findAllByText("Rp 120.000.000.000,00")).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Rp 30.000.000.000,00").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Rp 12.000.000.000,00").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("UPT Teknologi Informasi")).toBeInTheDocument();
    expect(screen.getAllByText("40.00%").length).toBeGreaterThanOrEqual(2);
  });
});
