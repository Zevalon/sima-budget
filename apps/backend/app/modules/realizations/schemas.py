from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.budget_foundation.schemas import FiscalYearStatus


class RealizationStatus(StrEnum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"
    CANCELLED = "CANCELLED"


class RealizationCreateRequest(BaseModel):
    budget_plan_id: UUID
    realization_date: date
    reference_number: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    vendor_name: str | None = Field(default=None, max_length=250)
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=2)


class RealizationUpdateRequest(BaseModel):
    expected_row_version: int = Field(ge=1)
    realization_date: date
    reference_number: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    vendor_name: str | None = Field(default=None, max_length=250)
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=2)


class RealizationPostRequest(BaseModel):
    expected_row_version: int = Field(ge=1)


class RealizationPlanOption(BaseModel):
    budget_plan_id: UUID
    plan_version_id: UUID
    organization_unit_id: UUID
    organization_unit_code: str
    organization_unit_name: str
    plan_number: str
    title: str
    approved_amount: Decimal
    realized_amount: Decimal
    draft_pipeline_amount: Decimal
    remaining_amount: Decimal


class RealizationContextResponse(BaseModel):
    fiscal_year_id: UUID
    fiscal_year_code: str
    fiscal_year_status: FiscalYearStatus
    scope_approved_amount: Decimal
    scope_realized_amount: Decimal
    scope_draft_pipeline_amount: Decimal
    scope_remaining_amount: Decimal
    plans: list[RealizationPlanOption]


class RealizationResponse(BaseModel):
    id: UUID
    fiscal_year_id: UUID
    fiscal_year_code: str
    budget_plan_id: UUID
    plan_version_id: UUID
    plan_number: str
    plan_title: str
    plan_approved_amount: Decimal
    plan_realized_amount: Decimal
    plan_draft_pipeline_amount: Decimal
    plan_remaining_amount: Decimal
    organization_unit_id: UUID
    organization_unit_code: str
    organization_unit_name: str
    realization_number: str
    status: RealizationStatus
    realization_date: date
    reference_number: str
    description: str
    vendor_name: str | None
    amount: Decimal
    row_version: int
    created_by: UUID
    posted_by: UUID | None
    posted_at: datetime | None
    created_at: datetime
    updated_at: datetime
