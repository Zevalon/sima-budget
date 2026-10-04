import { apiRequest } from "../../../lib/api/client";
import type { AnnualBudget, AnnualBudgetApproval } from "../types";

export function listAnnualBudgets(fiscalYearId?: string): Promise<AnnualBudget[]> {
  const query = fiscalYearId ? `?fiscal_year_id=${encodeURIComponent(fiscalYearId)}` : "";
  return apiRequest<AnnualBudget[]>(`/annual-budgets${query}`);
}

export function listPendingAnnualBudgets(): Promise<AnnualBudget[]> {
  return apiRequest<AnnualBudget[]>("/annual-budget-approvals/pending");
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

export function approveAnnualBudget(
  annualBudgetId: string,
  decisionNote: string | null,
): Promise<AnnualBudget> {
  return apiRequest<AnnualBudget>(
    `/annual-budgets/${annualBudgetId}/approve`,
    { method: "POST", body: JSON.stringify({ decision_note: decisionNote }) },
    { csrf: true },
  );
}

export function rejectAnnualBudget(annualBudgetId: string, reason: string): Promise<AnnualBudget> {
  return apiRequest<AnnualBudget>(
    `/annual-budgets/${annualBudgetId}/reject`,
    { method: "POST", body: JSON.stringify({ reason }) },
    { csrf: true },
  );
}

export function listAnnualBudgetApprovals(annualBudgetId: string): Promise<AnnualBudgetApproval[]> {
  return apiRequest<AnnualBudgetApproval[]>(`/annual-budgets/${annualBudgetId}/approvals`);
}
