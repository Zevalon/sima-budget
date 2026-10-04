from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

VALID_SCOPE_TYPES = {"OWN", "OWN_UNIT", "OWN_UNIT_AND_CHILDREN", "ALL"}


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
    unit_type_id: UUID
    unit_type_code: str
    unit_type_name: str
    can_receive_budget: bool
    can_create_budget_plan: bool
    is_active: bool


class AdminOrganizationUnitTypeSummary(BaseModel):
    id: UUID
    code: str
    name: str
    sort_order: int
    is_active: bool


class RoleAssignmentInput(BaseModel):
    role_id: UUID
    scope_type: str
    scope_unit_id: UUID | None = None

    @field_validator("scope_type")
    @classmethod
    def validate_scope_type(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_SCOPE_TYPES:
            raise ValueError("Scope type tidak valid.")
        return normalized


class AdminRoleGrant(BaseModel):
    role_id: UUID
    role_code: str
    role_name: str
    scope_type: str
    scope_unit_id: UUID | None


class AdminUserMembership(BaseModel):
    unit_id: UUID
    unit_code: str
    unit_name: str
    job_title: str | None
    is_primary: bool


class AdminUserDetail(AdminUserSummary):
    roles: list[AdminRoleGrant]
    memberships: list[AdminUserMembership]


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str | None = Field(default=None, max_length=254)
    full_name: str = Field(min_length=2, max_length=200)
    password: str = Field(min_length=12, max_length=1024)
    primary_unit_id: UUID
    job_title: str | None = Field(default=None, max_length=150)
    role_assignments: list[RoleAssignmentInput] = Field(default_factory=list)


class UserUpdateRequest(BaseModel):
    email: str | None = Field(default=None, max_length=254)
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    primary_unit_id: UUID | None = None
    job_title: str | None = Field(default=None, max_length=150)


class UserPasswordResetRequest(BaseModel):
    password: str = Field(min_length=12, max_length=1024)


class UserRoleAssignmentsRequest(BaseModel):
    assignments: list[RoleAssignmentInput]


class RoleCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    permission_codes: list[str] = Field(default_factory=list)


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class RolePermissionsRequest(BaseModel):
    permission_codes: list[str]


class OrganizationUnitCreateRequest(BaseModel):
    parent_id: UUID | None = None
    unit_type_id: UUID
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=200)
    can_receive_budget: bool = False
    can_create_budget_plan: bool = False


class OrganizationUnitUpdateRequest(BaseModel):
    parent_id: UUID | None = None
    unit_type_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=200)
    can_receive_budget: bool | None = None
    can_create_budget_plan: bool | None = None
