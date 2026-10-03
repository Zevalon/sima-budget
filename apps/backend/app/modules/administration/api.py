from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.administration.repository import (
    list_organization_units,
    list_permissions,
    list_roles,
    list_users,
)
from app.modules.administration.schemas import (
    AdminOrganizationUnitSummary,
    AdminPermissionSummary,
    AdminRoleSummary,
    AdminUserSummary,
)
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/users", response_model=list[AdminUserSummary])
async def users_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("users.view"))],
) -> list[AdminUserSummary]:
    return await list_users(session)


@router.get("/roles", response_model=list[AdminRoleSummary])
async def roles_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("roles.view"))],
) -> list[AdminRoleSummary]:
    return await list_roles(session)


@router.get("/permissions", response_model=list[AdminPermissionSummary])
async def permissions_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("permissions.view"))],
) -> list[AdminPermissionSummary]:
    return await list_permissions(session)


@router.get(
    "/organization-units",
    response_model=list[AdminOrganizationUnitSummary],
)
async def organization_units_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("organization_units.view")),
    ],
) -> list[AdminOrganizationUnitSummary]:
    return await list_organization_units(session)
