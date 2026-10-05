import { apiRequest } from "../../../lib/api/client";
import type { FinancialSummary } from "../types";

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
