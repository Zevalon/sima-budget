export type ReportUnitSummary = {
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  allocated_amount: string;
  committed_amount: string;
  draft_pipeline_amount: string;
  available_amount: string;
  realized_amount: string;
  realization_draft_pipeline_amount: string;
  remaining_to_realize_amount: string;
  utilization_percent: string;
};

export type ReportMonthlyRealization = {
  month: number;
  month_label: string;
  realized_amount: string;
};

export type ReportCategoryPlanSummary = {
  budget_category_id: string;
  budget_category_code: string;
  budget_category_name: string;
  committed_amount: string;
  draft_pipeline_amount: string;
};

export type FinancialSummary = {
  fiscal_year_id: string;
  fiscal_year_code: string;
  fiscal_year_status: string;
  annual_budget_id: string | null;
  annual_budget_status: string | null;
  organization_annual_budget_amount: string | null;
  scope_budget_amount: string;
  allocated_amount: string;
  unallocated_amount: string;
  committed_amount: string;
  draft_pipeline_amount: string;
  available_amount: string;
  realized_amount: string;
  realization_draft_pipeline_amount: string;
  remaining_to_realize_amount: string;
  utilization_percent: string;
  allocation_count: number;
  approved_plan_count: number;
  realization_count: number;
  unit_summaries: ReportUnitSummary[];
  monthly_realization: ReportMonthlyRealization[];
  category_plan_summaries: ReportCategoryPlanSummary[];
};
