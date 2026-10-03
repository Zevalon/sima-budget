from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.administration.schemas import (
    AdminOrganizationUnitSummary,
    AdminPermissionSummary,
    AdminRoleSummary,
    AdminUserSummary,
)
from app.modules.organizations.models import OrganizationUnit, OrganizationUnitType
from app.modules.roles.models import Permission, Role
from app.modules.users.models import User


async def list_users(session: AsyncSession) -> list[AdminUserSummary]:
    users = (
        await session.scalars(select(User).order_by(User.full_name.asc(), User.username.asc()))
    ).all()

    return [
        AdminUserSummary(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_locked=user.is_locked,
            last_login_at=user.last_login_at,
        )
        for user in users
    ]


async def list_roles(session: AsyncSession) -> list[AdminRoleSummary]:
    roles = (await session.scalars(select(Role).order_by(Role.name.asc(), Role.code.asc()))).all()

    return [
        AdminRoleSummary(
            id=role.id,
            code=role.code,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
        )
        for role in roles
    ]


async def list_permissions(session: AsyncSession) -> list[AdminPermissionSummary]:
    permissions = (
        await session.scalars(
            select(Permission).order_by(Permission.module.asc(), Permission.code.asc())
        )
    ).all()

    return [
        AdminPermissionSummary(
            id=permission.id,
            code=permission.code,
            name=permission.name,
            module=permission.module,
            description=permission.description,
        )
        for permission in permissions
    ]


async def list_organization_units(
    session: AsyncSession,
) -> list[AdminOrganizationUnitSummary]:
    rows = (
        await session.execute(
            select(OrganizationUnit, OrganizationUnitType)
            .join(
                OrganizationUnitType,
                OrganizationUnitType.id == OrganizationUnit.unit_type_id,
            )
            .order_by(OrganizationUnit.name.asc())
        )
    ).all()

    return [
        AdminOrganizationUnitSummary(
            id=unit.id,
            parent_id=unit.parent_id,
            code=unit.code,
            name=unit.name,
            unit_type_code=unit_type.code,
            unit_type_name=unit_type.name,
            can_receive_budget=unit.can_receive_budget,
            can_create_budget_plan=unit.can_create_budget_plan,
            is_active=unit.is_active,
        )
        for unit, unit_type in rows
    ]
