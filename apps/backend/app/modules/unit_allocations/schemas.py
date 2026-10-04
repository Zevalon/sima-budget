from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.annual_budgets.schemas import AnnualBudgetStatus
from app.modules.budget_foundation.schemas import FiscalYearStatus


class UnitAllocationResponse(BaseModel):
    id: UUID
    fiscal_year_id: UUID
    annual_budget_id: UUID
    organization_unit_id: UUID
    organization_unit_code: str
    organization_unit_name: str
    amount: Decimal
    committed_amount: Decimal
    draft_pipeline_amount: Decimal
    available_amount: Decimal
    notes: str | None
    version: int
    created_at: datetime
    updated_at: datetime


class UnitAllocationCreateRequest(BaseModel):
    fiscal_year_id: UUID
    organization_unit_id: UUID
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)


class UnitAllocationUpdateRequest(BaseModel):
    expected_version: int = Field(ge=1)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=20, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)


class UnitAllocationOverviewResponse(BaseModel):
    fiscal_year_id: UUID
    fiscal_year_code: str
    fiscal_year_status: FiscalYearStatus
    annual_budget_id: UUID | None
    annual_budget_status: AnnualBudgetStatus | None
    annual_budget_amount: Decimal
    allocated_amount: Decimal
    remaining_amount: Decimal
    committed_amount: Decimal
    draft_pipeline_amount: Decimal
    available_amount: Decimal
    allocations: list[UnitAllocationResponse]
