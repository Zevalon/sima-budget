from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.modules.annual_budgets.schemas import AnnualBudgetStatus
from app.modules.budget_foundation.schemas import FiscalYearStatus


class ReportUnitSummary(BaseModel):
    organization_unit_id: UUID
    organization_unit_code: str
    organization_unit_name: str
    allocated_amount: Decimal
    committed_amount: Decimal
    draft_pipeline_amount: Decimal
    available_amount: Decimal
    realized_amount: Decimal
    realization_draft_pipeline_amount: Decimal
    remaining_to_realize_amount: Decimal
    utilization_percent: Decimal


class ReportMonthlyRealization(BaseModel):
    month: int
    month_label: str
    realized_amount: Decimal


class ReportCategoryPlanSummary(BaseModel):
    budget_category_id: UUID
    budget_category_code: str
    budget_category_name: str
    committed_amount: Decimal
    draft_pipeline_amount: Decimal


class FinancialSummaryResponse(BaseModel):
    fiscal_year_id: UUID
    fiscal_year_code: str
    fiscal_year_status: FiscalYearStatus
    annual_budget_id: UUID | None
    annual_budget_status: AnnualBudgetStatus | None
    organization_annual_budget_amount: Decimal | None
    scope_budget_amount: Decimal
    allocated_amount: Decimal
    unallocated_amount: Decimal
    committed_amount: Decimal
    draft_pipeline_amount: Decimal
    available_amount: Decimal
    realized_amount: Decimal
    realization_draft_pipeline_amount: Decimal
    remaining_to_realize_amount: Decimal
    utilization_percent: Decimal
    allocation_count: int
    approved_plan_count: int
    realization_count: int
    unit_summaries: list[ReportUnitSummary]
    monthly_realization: list[ReportMonthlyRealization]
    category_plan_summaries: list[ReportCategoryPlanSummary]
