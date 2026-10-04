from pydantic import BaseModel, Field


class ApplicationSettingResponse(BaseModel):
    application_name: str
    application_short_name: str
    organization_display_name: str
    primary_color: str | None
    secondary_color: str | None
    currency_code: str
    timezone: str
    date_format: str
    allow_annual_budget_revision: bool
    allow_budget_transfer: bool
    allow_self_approval: bool


class ApplicationSettingUpdateRequest(BaseModel):
    application_name: str | None = Field(default=None, min_length=2, max_length=150)
    application_short_name: str | None = Field(default=None, min_length=2, max_length=50)
    organization_display_name: str | None = Field(default=None, min_length=2, max_length=200)
    primary_color: str | None = Field(default=None, max_length=20)
    secondary_color: str | None = Field(default=None, max_length=20)
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    date_format: str | None = Field(default=None, min_length=1, max_length=32)
    allow_annual_budget_revision: bool | None = None
    allow_budget_transfer: bool | None = None
    allow_self_approval: bool | None = None
