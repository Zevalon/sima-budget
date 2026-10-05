import { apiDownload, apiRequest, type ApiDownload } from "../../../lib/api/client";
import type { FinancialSummary } from "../types";

export type ReportExportFormat = "csv" | "xlsx" | "pdf";

export function getFinancialSummary(
  fiscalYearId: string,
  organizationUnitId?: string,
): Promise<FinancialSummary> {
  const params = new URLSearchParams({ fiscal_year_id: fiscalYearId });
  if (organizationUnitId) {
    params.set("organization_unit_id", organizationUnitId);
  }
  return apiRequest<FinancialSummary>(`/reports/financial-summary?${params.toString()}`);
}

export function downloadFinancialSummary(
  fiscalYearId: string,
  format: ReportExportFormat,
  filters: {
    organizationUnitId?: string;
    month?: string;
    budgetCategoryId?: string;
  } = {},
): Promise<ApiDownload> {
  const params = new URLSearchParams({
    fiscal_year_id: fiscalYearId,
    format,
  });
  if (filters.organizationUnitId) {
    params.set("organization_unit_id", filters.organizationUnitId);
  }
  if (filters.month) {
    params.set("month", filters.month);
  }
  if (filters.budgetCategoryId) {
    params.set("budget_category_id", filters.budgetCategoryId);
  }
  return apiDownload(`/reports/financial-summary/export?${params.toString()}`);
}
