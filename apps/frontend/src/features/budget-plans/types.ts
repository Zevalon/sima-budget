export type BudgetPlanStatus = "DRAFT" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "CANCELLED";

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
  plan_number: string;
  status: BudgetPlanStatus;
  current_version_no: number;
  row_version: number;
  title: string;
  description: string | null;
  total_amount: string;
  items: BudgetPlanItem[];
  created_by: string;
  created_at: string;
  updated_at: string;
};

export type BudgetPlanAllocationOption = {
  unit_allocation_id: string;
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  allocation_amount: string;
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
