from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class FiscalYearStatus(StrEnum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class FiscalYearResponse(BaseModel):
    id: UUID
    code: str
    year: int | None
    start_date: date
    end_date: date
    status: FiscalYearStatus
    reopened_at: datetime | None
    reopened_by: UUID | None
    reopen_reason: str | None
    created_at: datetime
    updated_at: datetime


class FiscalYearCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2200)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> FiscalYearCreateRequest:
        if self.start_date >= self.end_date:
            raise ValueError("Tanggal mulai harus lebih awal daripada tanggal selesai.")
        return self


class FiscalYearUpdateRequest(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2200)
    start_date: date | None = None
    end_date: date | None = None


class FiscalYearTransitionRequest(BaseModel):
    target_status: FiscalYearStatus
    reason: str | None = Field(default=None, max_length=1000)


class FiscalYearReopenRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class BudgetCategoryResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BudgetCategoryCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)


class BudgetCategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)


class UnitOfMeasureResponse(BaseModel):
    id: UUID
    code: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UnitOfMeasureCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)


class UnitOfMeasureUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
