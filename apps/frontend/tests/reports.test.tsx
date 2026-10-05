import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ReportsPage } from "../src/features/reports/pages/ReportsPage";

const mocks = vi.hoisted(() => ({
  getFinancialSummary: vi.fn(),
  selectedFiscalYear: {
    id: "fy-2025",
    code: "FY2025",
    status: "ACTIVE",
  },
}));

vi.mock("../src/features/budget-foundation/fiscal-year-context", () => ({
  useFiscalYear: () => ({
    selectedFiscalYear: mocks.selectedFiscalYear,
  }),
}));

vi.mock("../src/features/reports/api/reports", () => ({
  getFinancialSummary: mocks.getFinancialSummary,
}));

const unitOptions = [
  {
    organization_unit_id: "unit-it",
    organization_unit_code: "IT",
    organization_unit_name: "UPT Teknologi Informasi",
  },
  {
    organization_unit_id: "unit-ft",
    organization_unit_code: "FT",
    organization_unit_name: "Fakultas Teknik",
  },
];

function createSummary(organizationUnitId: string | null) {
  const filtered = organizationUnitId === "unit-it";
  return {
    fiscal_year_id: "fy-2025",
    fiscal_year_code: "FY2025",
    fiscal_year_status: "ACTIVE",
    organization_unit_filter_id: organizationUnitId,
    annual_budget_id: "budget-1",
    annual_budget_status: "APPROVED",
    organization_annual_budget_amount: "500000000000.00",
    scope_budget_amount: filtered ? "120000000000.00" : "500000000000.00",
    allocated_amount: filtered ? "120000000000.00" : "200000000000.00",
    unallocated_amount: filtered ? "0.00" : "300000000000.00",
    committed_amount: filtered ? "30000000000.00" : "50000000000.00",
    draft_pipeline_amount: filtered ? "5000000000.00" : "7000000000.00",
    available_amount: filtered ? "90000000000.00" : "150000000000.00",
    realized_amount: filtered ? "12000000000.00" : "18000000000.00",
    realization_draft_pipeline_amount: filtered ? "1000000000.00" : "1500000000.00",
    remaining_to_realize_amount: filtered ? "18000000000.00" : "32000000000.00",
    utilization_percent: filtered ? "40.00" : "36.00",
    allocation_count: filtered ? 1 : 2,
    approved_plan_count: filtered ? 1 : 2,
    realization_count: filtered ? 2 : 3,
    unit_filter_options: unitOptions,
    unit_summaries: filtered
      ? [
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
        ]
      : [
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
          {
            organization_unit_id: "unit-ft",
            organization_unit_code: "FT",
            organization_unit_name: "Fakultas Teknik",
            allocated_amount: "80000000000.00",
            committed_amount: "20000000000.00",
            draft_pipeline_amount: "2000000000.00",
            available_amount: "60000000000.00",
            realized_amount: "6000000000.00",
            realization_draft_pipeline_amount: "500000000.00",
            remaining_to_realize_amount: "14000000000.00",
            utilization_percent: "30.00",
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
      realized_amount: index === 0 ? (filtered ? "12000000000.00" : "18000000000.00") : "0.00",
    })),
    category_plan_summaries: [
      {
        budget_category_id: "cat-cloud",
        budget_category_code: "CLOUD",
        budget_category_name: "Cloud & Infrastruktur",
        committed_amount: filtered ? "20000000000.00" : "30000000000.00",
        draft_pipeline_amount: filtered ? "3000000000.00" : "4000000000.00",
      },
      {
        budget_category_id: "cat-device",
        budget_category_code: "DEVICE",
        budget_category_name: "Perangkat",
        committed_amount: filtered ? "10000000000.00" : "20000000000.00",
        draft_pipeline_amount: filtered ? "2000000000.00" : "3000000000.00",
      },
    ],
  };
}

describe("ReportsPage", () => {
  it("supports scoped unit, month, and category report filters", async () => {
    mocks.getFinancialSummary.mockImplementation(
      (_fiscalYearId: string, organizationUnitId?: string) =>
        Promise.resolve(createSummary(organizationUnitId ?? null)),
    );

    render(<ReportsPage />);

    expect(screen.getByRole("heading", { name: "Laporan Anggaran" })).toBeInTheDocument();
    expect((await screen.findAllByText("Rp 500.000.000.000,00")).length).toBeGreaterThanOrEqual(1);

    fireEvent.change(screen.getByLabelText("Unit organisasi"), {
      target: { value: "unit-it" },
    });

    await waitFor(() => {
      expect(mocks.getFinancialSummary).toHaveBeenLastCalledWith("fy-2025", "unit-it");
    });
    expect(await screen.findByText("Pagu Unit")).toBeInTheDocument();
    expect(screen.getByText("Filter unit aktif: UPT Teknologi Informasi")).toBeInTheDocument();
    expect(screen.queryByText("Fakultas Teknik")).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Bulan realisasi"), {
      target: { value: "1" },
    });
    expect(screen.getByRole("article", { name: "Realisasi Jan" })).toBeInTheDocument();
    expect(screen.queryByRole("article", { name: "Realisasi Feb" })).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Kategori anggaran"), {
      target: { value: "cat-cloud" },
    });
    expect(screen.getByText("Cloud & Infrastruktur")).toBeInTheDocument();
    expect(screen.queryByText("Perangkat")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Reset Filter" }));
    await waitFor(() => {
      expect(mocks.getFinancialSummary).toHaveBeenLastCalledWith("fy-2025", undefined);
    });
  });
});
