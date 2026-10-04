import { apiRequest } from "../../../lib/api/client";
import type { BudgetPlan, BudgetPlanContext, BudgetPlanItemInput } from "../types";

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
