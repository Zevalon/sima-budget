export type UnitAllocation = {
  id: string;
  fiscal_year_id: string;
  annual_budget_id: string;
  organization_unit_id: string;
  organization_unit_code: string;
  organization_unit_name: string;
  amount: string;
  notes: string | null;
  version: number;
  created_at: string;
  updated_at: string;
};

export type UnitAllocationOverview = {
  fiscal_year_id: string;
  fiscal_year_code: string;
  fiscal_year_status: "DRAFT" | "PLANNING" | "ACTIVE" | "CLOSED" | "ARCHIVED";
  annual_budget_id: string | null;
  annual_budget_status: "DRAFT" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | null;
  annual_budget_amount: string;
  allocated_amount: string;
  remaining_amount: string;
  allocations: UnitAllocation[];
};
