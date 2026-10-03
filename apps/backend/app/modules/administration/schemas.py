from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminUserSummary(BaseModel):
    id: UUID
    username: str
    email: str | None
    full_name: str
    is_active: bool
    is_locked: bool
    last_login_at: datetime | None


class AdminRoleSummary(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    is_system_role: bool
    is_active: bool


class AdminPermissionSummary(BaseModel):
    id: UUID
    code: str
    name: str
    module: str
    description: str | None


class AdminOrganizationUnitSummary(BaseModel):
    id: UUID
    parent_id: UUID | None
    code: str
    name: str
    unit_type_code: str
    unit_type_name: str
    can_receive_budget: bool
    can_create_budget_plan: bool
    is_active: bool
