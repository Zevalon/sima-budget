import { apiRequest } from "../../../lib/api/client";
import type { FinancialSummary } from "../types";

export function getFinancialSummary(fiscalYearId: string): Promise<FinancialSummary> {
  return apiRequest<FinancialSummary>(
    `/reports/financial-summary?fiscal_year_id=${encodeURIComponent(fiscalYearId)}`,
  );
}
