from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.budget_foundation.schemas import FiscalYearStatus


class BudgetPlanStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class BudgetPlanApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class BudgetPlanItemRequest(BaseModel):
    budget_category_id: UUID
    unit_of_measure_id: UUID
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    unit_price: Decimal = Field(gt=0, max_digits=20, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)


class BudgetPlanCreateRequest(BaseModel):
    unit_allocation_id: UUID
    title: str = Field(min_length=1, max_length=250)
    description: str | None = Field(default=None, max_length=4000)
    items: list[BudgetPlanItemRequest] = Field(min_length=1, max_length=200)


class BudgetPlanUpdateRequest(BaseModel):
    expected_row_version: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=250)
    description: str | None = Field(default=None, max_length=4000)
    items: list[BudgetPlanItemRequest] = Field(min_length=1, max_length=200)


class BudgetPlanRevisionRequest(BudgetPlanUpdateRequest):
    pass


class BudgetPlanSubmitRequest(BaseModel):
    expected_row_version: int = Field(ge=1)


class BudgetPlanApproveRequest(BaseModel):
    expected_row_version: int = Field(ge=1)
    expected_submission_no: int = Field(ge=1)
    expected_version_no: int = Field(ge=1)
    decision_note: str | None = Field(default=None, max_length=2000)


class BudgetPlanRejectRequest(BaseModel):
    expected_row_version: int = Field(ge=1)
    expected_submission_no: int = Field(ge=1)
    expected_version_no: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=2000)


class BudgetPlanItemResponse(BaseModel):
    id: UUID
    line_no: int
    budget_category_id: UUID
    budget_category_code: str
    budget_category_name: str
    unit_of_measure_id: UUID
    unit_of_measure_code: str
    unit_of_measure_name: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    notes: str | None


class BudgetPlanResponse(BaseModel):
    id: UUID
    fiscal_year_id: UUID
    fiscal_year_code: str
    unit_allocation_id: UUID
    organization_unit_id: UUID
    organization_unit_code: str
    organization_unit_name: str
    allocation_amount: Decimal
    allocation_committed_amount: Decimal
    allocation_draft_pipeline_amount: Decimal
    allocation_available_amount: Decimal
    plan_number: str
    status: BudgetPlanStatus
    current_version_no: int
    row_version: int
    title: str
    description: str | None
    total_amount: Decimal
    items: list[BudgetPlanItemResponse]
    created_by: UUID
    submitted_by: UUID | None
    submitted_at: datetime | None
    approved_by: UUID | None
    approved_at: datetime | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime


class BudgetPlanApprovalResponse(BaseModel):
    id: UUID
    budget_plan_id: UUID
    plan_version_id: UUID
    submission_no: int
    version_no: int
    status: BudgetPlanApprovalStatus
    requested_by: UUID
    requested_at: datetime
    decided_by: UUID | None
    decided_at: datetime | None
    decision_note: str | None
    created_at: datetime
    updated_at: datetime


class BudgetPlanPendingApprovalResponse(BaseModel):
    budget_plan: BudgetPlanResponse
    approval: BudgetPlanApprovalResponse


class BudgetPlanAllocationOption(BaseModel):
    unit_allocation_id: UUID
    organization_unit_id: UUID
    organization_unit_code: str
    organization_unit_name: str
    allocation_amount: Decimal
    committed_amount: Decimal
    draft_pipeline_amount: Decimal
    available_amount: Decimal


class BudgetPlanLookupOption(BaseModel):
    id: UUID
    code: str
    name: str


class BudgetPlanContextResponse(BaseModel):
    fiscal_year_id: UUID
    fiscal_year_code: str
    fiscal_year_status: FiscalYearStatus
    scope_allocation_amount: Decimal
    scope_committed_amount: Decimal
    scope_draft_pipeline_amount: Decimal
    scope_available_amount: Decimal
    allocations: list[BudgetPlanAllocationOption]
    budget_categories: list[BudgetPlanLookupOption]
    units_of_measure: list[BudgetPlanLookupOption]
