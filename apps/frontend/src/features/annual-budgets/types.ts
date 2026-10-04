export type AnnualBudgetStatus = "DRAFT" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED";

export type AnnualBudget = {
  id: string;
  fiscal_year_id: string;
  fiscal_year_code: string;
  amount: string;
  notes: string | null;
  status: AnnualBudgetStatus;
  version: number;
  submitted_by: string | null;
  submitted_at: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type AnnualBudgetApproval = {
  id: string;
  annual_budget_id: string;
  submission_no: number;
  status: "PENDING" | "APPROVED" | "REJECTED";
  requested_by: string;
  requested_at: string;
  decided_by: string | null;
  decided_at: string | null;
  decision_note: string | null;
  created_at: string;
  updated_at: string;
};
