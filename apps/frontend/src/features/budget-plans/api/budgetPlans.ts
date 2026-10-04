import { apiRequest } from "../../../lib/api/client";
import type {
  BudgetPlan,
  BudgetPlanApproval,
  BudgetPlanContext,
  BudgetPlanItemInput,
  BudgetPlanPendingApproval,
} from "../types";

export function getBudgetPlanContext(fiscalYearId: string): Promise<BudgetPlanContext> {
  return apiRequest<BudgetPlanContext>(
    `/budget-plans/context?fiscal_year_id=${encodeURIComponent(fiscalYearId)}`,
  );
}

export function listBudgetPlans(fiscalYearId: string): Promise<BudgetPlan[]> {
  return apiRequest<BudgetPlan[]>(
    `/budget-plans?fiscal_year_id=${encodeURIComponent(fiscalYearId)}`,
  );
}

export function createBudgetPlan(payload: {
  unit_allocation_id: string;
  title: string;
  description: string | null;
  items: BudgetPlanItemInput[];
}): Promise<BudgetPlan> {
  return apiRequest<BudgetPlan>(
    "/budget-plans",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function updateBudgetPlan(
  planId: string,
  payload: {
    expected_row_version: number;
    title: string;
    description: string | null;
    items: BudgetPlanItemInput[];
  },
): Promise<BudgetPlan> {
  return apiRequest<BudgetPlan>(
    `/budget-plans/${planId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function submitBudgetPlan(planId: string, expectedRowVersion: number): Promise<BudgetPlan> {
  return apiRequest<BudgetPlan>(
    `/budget-plans/${planId}/submit`,
    {
      method: "POST",
      body: JSON.stringify({ expected_row_version: expectedRowVersion }),
    },
    { csrf: true },
  );
}

export function reviseBudgetPlan(
  planId: string,
  payload: {
    expected_row_version: number;
    title: string;
    description: string | null;
    items: BudgetPlanItemInput[];
  },
): Promise<BudgetPlan> {
  return apiRequest<BudgetPlan>(
    `/budget-plans/${planId}/revise`,
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function listBudgetPlanApprovals(planId: string): Promise<BudgetPlanApproval[]> {
  return apiRequest<BudgetPlanApproval[]>(`/budget-plans/${planId}/approvals`);
}

export function listPendingBudgetPlanApprovals(
  fiscalYearId?: string,
): Promise<BudgetPlanPendingApproval[]> {
  const query = fiscalYearId ? `?fiscal_year_id=${encodeURIComponent(fiscalYearId)}` : "";
  return apiRequest<BudgetPlanPendingApproval[]>(`/budget-plan-approvals/pending${query}`);
}

export function approveBudgetPlan(
  planId: string,
  payload: {
    expected_row_version: number;
    expected_submission_no: number;
    expected_version_no: number;
    decision_note: string | null;
  },
): Promise<BudgetPlan> {
  return apiRequest<BudgetPlan>(
    `/budget-plans/${planId}/approve`,
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function rejectBudgetPlan(
  planId: string,
  payload: {
    expected_row_version: number;
    expected_submission_no: number;
    expected_version_no: number;
    reason: string;
  },
): Promise<BudgetPlan> {
  return apiRequest<BudgetPlan>(
    `/budget-plans/${planId}/reject`,
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}
