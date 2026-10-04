from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.administration.repository import (
    get_user_detail,
    list_organization_unit_types,
    list_organization_units,
    list_permissions,
    list_roles,
    list_users,
)
from app.modules.administration.schemas import (
    AdminOrganizationUnitSummary,
    AdminOrganizationUnitTypeSummary,
    AdminPermissionSummary,
    AdminRoleSummary,
    AdminUserDetail,
    AdminUserSummary,
    OrganizationUnitCreateRequest,
    OrganizationUnitUpdateRequest,
    RoleCreateRequest,
    RolePermissionsRequest,
    RoleUpdateRequest,
    UserCreateRequest,
    UserPasswordResetRequest,
    UserRoleAssignmentsRequest,
    UserUpdateRequest,
)
from app.modules.administration.service import (
    create_organization_unit,
    create_role,
    create_user,
    deactivate_organization_unit,
    deactivate_user,
    not_found,
    replace_role_permissions,
    reset_user_password,
    update_organization_unit,
    update_role,
    update_user,
    update_user_roles,
)
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/users", response_model=list[AdminUserSummary])
async def users_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("users.view"))],
) -> list[AdminUserSummary]:
    return await list_users(session)


@router.get("/users/{user_id}", response_model=AdminUserDetail)
async def user_detail_endpoint(
    user_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("users.view"))],
) -> AdminUserDetail:
    detail = await get_user_detail(session, user_id)
    if detail is None:
        raise not_found("User tidak ditemukan.")
    return detail


@router.post("/users", response_model=AdminUserDetail, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    payload: UserCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("users.create", require_all_scope=True)),
    ],
) -> AdminUserDetail:
    return await create_user(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.patch("/users/{user_id}", response_model=AdminUserDetail)
async def update_user_endpoint(
    user_id: UUID,
    payload: UserUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("users.update", require_all_scope=True)),
    ],
) -> AdminUserDetail:
    return await update_user(
        session,
        user_id=user_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/users/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user_endpoint(
    user_id: UUID,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("users.deactivate", require_all_scope=True)),
    ],
) -> None:
    await deactivate_user(
        session,
        user_id=user_id,
        actor_user_id=context.user.id,
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_user_password_endpoint(
    user_id: UUID,
    payload: UserPasswordResetRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("users.update", require_all_scope=True)),
    ],
) -> None:
    await reset_user_password(
        session,
        user_id=user_id,
        password=payload.password,
        actor_user_id=context.user.id,
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@router.put("/users/{user_id}/roles", response_model=AdminUserDetail)
async def update_user_roles_endpoint(
    user_id: UUID,
    payload: UserRoleAssignmentsRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("roles.assign", require_all_scope=True)),
    ],
) -> AdminUserDetail:
    return await update_user_roles(
        session,
        user_id=user_id,
        assignments=payload.assignments,
        actor_user_id=context.user.id,
    )


@router.get("/roles", response_model=list[AdminRoleSummary])
async def roles_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("roles.view"))],
) -> list[AdminRoleSummary]:
    return await list_roles(session)


@router.post("/roles", response_model=AdminRoleSummary, status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    payload: RoleCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("roles.create", require_all_scope=True)),
    ],
) -> AdminRoleSummary:
    return await create_role(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.patch("/roles/{role_id}", response_model=AdminRoleSummary)
async def update_role_endpoint(
    role_id: UUID,
    payload: RoleUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("roles.update", require_all_scope=True)),
    ],
) -> AdminRoleSummary:
    return await update_role(
        session,
        role_id=role_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.put("/roles/{role_id}/permissions", status_code=status.HTTP_204_NO_CONTENT)
async def update_role_permissions_endpoint(
    role_id: UUID,
    payload: RolePermissionsRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("roles.update", require_all_scope=True)),
    ],
) -> None:
    await replace_role_permissions(
        session,
        role_id=role_id,
        permission_codes=payload.permission_codes,
        actor_user_id=context.user.id,
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@router.get("/permissions", response_model=list[AdminPermissionSummary])
async def permissions_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("permissions.view"))],
) -> list[AdminPermissionSummary]:
    return await list_permissions(session)


@router.get(
    "/organization-unit-types",
    response_model=list[AdminOrganizationUnitTypeSummary],
)
async def organization_unit_types_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("organization_units.view")),
    ],
) -> list[AdminOrganizationUnitTypeSummary]:
    return await list_organization_unit_types(session)


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


@router.post(
    "/organization-units",
    response_model=AdminOrganizationUnitSummary,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_unit_endpoint(
    payload: OrganizationUnitCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("organization_units.create", require_all_scope=True)),
    ],
) -> AdminOrganizationUnitSummary:
    unit = await create_organization_unit(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )
    units = await list_organization_units(session)
    return next(item for item in units if item.id == unit.id)


@router.patch(
    "/organization-units/{unit_id}",
    response_model=AdminOrganizationUnitSummary,
)
async def update_organization_unit_endpoint(
    unit_id: UUID,
    payload: OrganizationUnitUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("organization_units.update", require_all_scope=True)),
    ],
) -> AdminOrganizationUnitSummary:
    unit = await update_organization_unit(
        session,
        unit_id=unit_id,
        payload=payload,
        actor_user_id=context.user.id,
    )
    units = await list_organization_units(session)
    return next(item for item in units if item.id == unit.id)


@router.post(
    "/organization-units/{unit_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_organization_unit_endpoint(
    unit_id: UUID,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(
            RequirePermission(
                "organization_units.deactivate",
                require_all_scope=True,
            )
        ),
    ],
) -> None:
    await deactivate_organization_unit(
        session,
        unit_id=unit_id,
        actor_user_id=context.user.id,
    )
    response.status_code = status.HTTP_204_NO_CONTENT
