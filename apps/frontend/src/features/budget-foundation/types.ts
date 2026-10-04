export type FiscalYearStatus = "DRAFT" | "PLANNING" | "ACTIVE" | "CLOSED" | "ARCHIVED";

export type FiscalYear = {
  id: string;
  code: string;
  year: number | null;
  start_date: string;
  end_date: string;
  status: FiscalYearStatus;
  reopened_at: string | null;
  reopened_by: string | null;
  reopen_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type BudgetCategory = {
  id: string;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type UnitOfMeasure = {
  id: string;
  code: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};
