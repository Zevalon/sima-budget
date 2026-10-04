export type BudgetPlanStatus = "DRAFT" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "CANCELLED";

export type BudgetPlanApprovalStatus = "PENDING" | "APPROVED" | "REJECTED";

export type BudgetPlanItem = {
  id: string;
  line_no: number;
  budget_category_id: string;
  budget_category_code: string;
  budget_category_name: string;
  unit_of_measure_id: string;
  unit_of_measure_code: string;
  unit_of_measure_name: string;
  description: string;
  quantity: string;
  unit_price: string;
  amount: string;
  notes: string | null;
};

export type BudgetPlan = {
  id: string;
  fiscal_year_id: string;
  fiscal_year_code: string;
  unit_allocation_id: string;
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  allocation_amount: string;
  allocation_committed_amount: string;
  allocation_draft_pipeline_amount: string;
  allocation_available_amount: string;
  plan_number: string;
  status: BudgetPlanStatus;
  current_version_no: number;
  row_version: number;
  title: string;
  description: string | null;
  total_amount: string;
  items: BudgetPlanItem[];
  created_by: string;
  submitted_by: string | null;
  submitted_at: string | null;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type BudgetPlanApproval = {
  id: string;
  budget_plan_id: string;
  plan_version_id: string;
  submission_no: number;
  version_no: number;
  status: BudgetPlanApprovalStatus;
  requested_by: string;
  requested_at: string;
  decided_by: string | null;
  decided_at: string | null;
  decision_note: string | null;
  created_at: string;
  updated_at: string;
};

export type BudgetPlanPendingApproval = {
  budget_plan: BudgetPlan;
  approval: BudgetPlanApproval;
};

export type BudgetPlanAllocationOption = {
  unit_allocation_id: string;
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  allocation_amount: string;
  committed_amount: string;
  draft_pipeline_amount: string;
  available_amount: string;
};

export type BudgetPlanLookupOption = {
  id: string;
  code: string;
  name: string;
};

export type BudgetPlanContext = {
  fiscal_year_id: string;
  fiscal_year_code: string;
  fiscal_year_status: "DRAFT" | "PLANNING" | "ACTIVE" | "CLOSED" | "ARCHIVED";
  scope_allocation_amount: string;
  scope_committed_amount: string;
  scope_draft_pipeline_amount: string;
  scope_available_amount: string;
  allocations: BudgetPlanAllocationOption[];
  budget_categories: BudgetPlanLookupOption[];
  units_of_measure: BudgetPlanLookupOption[];
};

export type BudgetPlanItemInput = {
  budget_category_id: string;
  unit_of_measure_id: string;
  description: string;
  quantity: string;
  unit_price: string;
  notes: string | null;
};
