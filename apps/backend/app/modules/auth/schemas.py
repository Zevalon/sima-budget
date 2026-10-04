from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


class RoleGrantResponse(BaseModel):
    role_code: str
    role_name: str
    scope_type: str
    scope_unit_id: UUID | None


class UnitMembershipResponse(BaseModel):
    unit_id: UUID
    unit_code: str
    unit_name: str
    job_title: str | None
    is_primary: bool


class CurrentUserResponse(BaseModel):
    id: UUID
    username: str
    email: str | None
    full_name: str
    organization_id: UUID
    organization_name: str
    application_name: str
    application_short_name: str
    organization_display_name: str
    roles: list[RoleGrantResponse]
    permissions: list[str]
    unit_memberships: list[UnitMembershipResponse]
    session_expires_at: datetime
    csrf_token: str


class LoginResponse(CurrentUserResponse):
    pass
