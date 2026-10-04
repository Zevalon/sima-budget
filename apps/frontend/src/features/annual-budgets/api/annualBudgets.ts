import { apiRequest } from "../../../lib/api/client";
import type { AnnualBudget, AnnualBudgetApproval } from "../types";

export function listAnnualBudgets(fiscalYearId?: string): Promise<AnnualBudget[]> {
  const query = fiscalYearId ? `?fiscal_year_id=${encodeURIComponent(fiscalYearId)}` : "";
  return apiRequest<AnnualBudget[]>(`/annual-budgets${query}`);
}

export function createAnnualBudget(payload: {
  fiscal_year_id: string;
  amount: string;
  notes: string | null;
}): Promise<AnnualBudget> {
  return apiRequest<AnnualBudget>(
    "/annual-budgets",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function updateAnnualBudget(
  annualBudgetId: string,
  payload: { amount?: string; notes?: string | null },
): Promise<AnnualBudget> {
  return apiRequest<AnnualBudget>(
    `/annual-budgets/${annualBudgetId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function submitAnnualBudget(annualBudgetId: string): Promise<AnnualBudget> {
  return apiRequest<AnnualBudget>(
    `/annual-budgets/${annualBudgetId}/submit`,
    { method: "POST" },
    { csrf: true },
  );
}

export function listAnnualBudgetApprovals(annualBudgetId: string): Promise<AnnualBudgetApproval[]> {
  return apiRequest<AnnualBudgetApproval[]>(`/annual-budgets/${annualBudgetId}/approvals`);
}
