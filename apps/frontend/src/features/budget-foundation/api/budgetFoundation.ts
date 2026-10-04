import { apiRequest } from "../../../lib/api/client";
import type { BudgetCategory, FiscalYear, FiscalYearStatus, UnitOfMeasure } from "../types";

export function listFiscalYears(): Promise<FiscalYear[]> {
  return apiRequest<FiscalYear[]>("/fiscal-years");
}

export function createFiscalYear(payload: {
  code: string;
  year: number | null;
  start_date: string;
  end_date: string;
}): Promise<FiscalYear> {
  return apiRequest<FiscalYear>(
    "/fiscal-years",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function transitionFiscalYear(
  fiscalYearId: string,
  targetStatus: FiscalYearStatus,
  reason?: string,
): Promise<FiscalYear> {
  return apiRequest<FiscalYear>(
    `/fiscal-years/${fiscalYearId}/transition`,
    {
      method: "POST",
      body: JSON.stringify({ target_status: targetStatus, reason: reason ?? null }),
    },
    { csrf: true },
  );
}

export function reopenFiscalYear(fiscalYearId: string, reason: string): Promise<FiscalYear> {
  return apiRequest<FiscalYear>(
    `/fiscal-years/${fiscalYearId}/reopen`,
    { method: "POST", body: JSON.stringify({ reason }) },
    { csrf: true },
  );
}

export function listBudgetCategories(): Promise<BudgetCategory[]> {
  return apiRequest<BudgetCategory[]>("/master-data/budget-categories");
}

export function createBudgetCategory(payload: {
  code: string;
  name: string;
  description: string | null;
}): Promise<BudgetCategory> {
  return apiRequest<BudgetCategory>(
    "/master-data/budget-categories",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function deactivateBudgetCategory(categoryId: string): Promise<void> {
  return apiRequest<void>(
    `/master-data/budget-categories/${categoryId}/deactivate`,
    { method: "POST" },
    { csrf: true },
  );
}

export function listUnitsOfMeasure(): Promise<UnitOfMeasure[]> {
  return apiRequest<UnitOfMeasure[]>("/master-data/units-of-measure");
}

export function createUnitOfMeasure(payload: {
  code: string;
  name: string;
}): Promise<UnitOfMeasure> {
  return apiRequest<UnitOfMeasure>(
    "/master-data/units-of-measure",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function deactivateUnitOfMeasure(unitId: string): Promise<void> {
  return apiRequest<void>(
    `/master-data/units-of-measure/${unitId}/deactivate`,
    { method: "POST" },
    { csrf: true },
  );
}
