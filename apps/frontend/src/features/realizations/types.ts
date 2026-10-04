export type RealizationStatus = "DRAFT" | "POSTED" | "REVERSED" | "CANCELLED";

export type RealizationPlanOption = {
  budget_plan_id: string;
  plan_version_id: string;
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  plan_number: string;
  title: string;
  approved_amount: string;
  realized_amount: string;
  draft_pipeline_amount: string;
  remaining_amount: string;
};

export type RealizationContext = {
  fiscal_year_id: string;
  fiscal_year_code: string;
  fiscal_year_status: "DRAFT" | "PLANNING" | "ACTIVE" | "CLOSED" | "ARCHIVED";
  scope_approved_amount: string;
  scope_realized_amount: string;
  scope_draft_pipeline_amount: string;
  scope_remaining_amount: string;
  plans: RealizationPlanOption[];
};

export type Realization = {
  id: string;
  fiscal_year_id: string;
  fiscal_year_code: string;
  budget_plan_id: string;
  plan_version_id: string;
  plan_number: string;
  plan_title: string;
  plan_approved_amount: string;
  plan_realized_amount: string;
  plan_draft_pipeline_amount: string;
  plan_remaining_amount: string;
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  realization_number: string;
  status: RealizationStatus;
  realization_date: string;
  reference_number: string;
  description: string;
  vendor_name: string | null;
  amount: string;
  row_version: number;
  created_by: string;
  posted_by: string | null;
  posted_at: string | null;
  created_at: string;
  updated_at: string;
};
