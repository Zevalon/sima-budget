from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AnnualBudgetStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AnnualBudgetApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AnnualBudgetResponse(BaseModel):
    id: UUID
    fiscal_year_id: UUID
    fiscal_year_code: str
    amount: Decimal
    notes: str | None
    status: AnnualBudgetStatus
    version: int
    submitted_by: UUID | None
    submitted_at: datetime | None
    approved_by: UUID | None
    approved_at: datetime | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime


class AnnualBudgetCreateRequest(BaseModel):
    fiscal_year_id: UUID
    amount: Decimal = Field(gt=0, max_digits=20, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)


class AnnualBudgetUpdateRequest(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=20, decimal_places=2)
    notes: str | None = Field(default=None, max_length=2000)


class AnnualBudgetApprovalResponse(BaseModel):
    id: UUID
    annual_budget_id: UUID
    submission_no: int
    status: AnnualBudgetApprovalStatus
    requested_by: UUID
    requested_at: datetime
    decided_by: UUID | None
    decided_at: datetime | None
    decision_note: str | None
    created_at: datetime
    updated_at: datetime
