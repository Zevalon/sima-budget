from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.administration.schemas import (
    AdminOrganizationUnitSummary,
    AdminOrganizationUnitTypeSummary,
    AdminPermissionSummary,
    AdminRoleGrant,
    AdminRoleSummary,
    AdminUserDetail,
    AdminUserMembership,
    AdminUserSummary,
)
from app.modules.organizations.models import (
    OrganizationUnit,
    OrganizationUnitType,
    UserUnitMembership,
)
from app.modules.roles.models import Permission, Role, UserRoleAssignment
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


async def get_user_detail(session: AsyncSession, user_id: UUID) -> AdminUserDetail | None:
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        return None

    role_rows = (
        await session.execute(
            select(UserRoleAssignment, Role)
            .join(Role, Role.id == UserRoleAssignment.role_id)
            .where(UserRoleAssignment.user_id == user.id)
            .order_by(Role.name.asc())
        )
    ).all()

    membership_rows = (
        await session.execute(
            select(UserUnitMembership, OrganizationUnit)
            .join(
                OrganizationUnit,
                OrganizationUnit.id == UserUnitMembership.organization_unit_id,
            )
            .where(UserUnitMembership.user_id == user.id)
            .order_by(UserUnitMembership.is_primary.desc(), OrganizationUnit.name.asc())
        )
    ).all()

    return AdminUserDetail(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_locked=user.is_locked,
        last_login_at=user.last_login_at,
        roles=[
            AdminRoleGrant(
                role_id=role.id,
                role_code=role.code,
                role_name=role.name,
                scope_type=assignment.scope_type,
                scope_unit_id=assignment.scope_unit_id,
            )
            for assignment, role in role_rows
        ],
        memberships=[
            AdminUserMembership(
                unit_id=unit.id,
                unit_code=unit.code,
                unit_name=unit.name,
                job_title=membership.job_title,
                is_primary=membership.is_primary,
            )
            for membership, unit in membership_rows
        ],
    )


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
            unit_type_id=unit.unit_type_id,
            unit_type_code=unit_type.code,
            unit_type_name=unit_type.name,
            can_receive_budget=unit.can_receive_budget,
            can_create_budget_plan=unit.can_create_budget_plan,
            is_active=unit.is_active,
        )
        for unit, unit_type in rows
    ]


async def list_organization_unit_types(
    session: AsyncSession,
) -> list[AdminOrganizationUnitTypeSummary]:
    rows = (
        await session.scalars(
            select(OrganizationUnitType).order_by(
                OrganizationUnitType.sort_order.asc(),
                OrganizationUnitType.name.asc(),
            )
        )
    ).all()

    return [
        AdminOrganizationUnitTypeSummary(
            id=unit_type.id,
            code=unit_type.code,
            name=unit_type.name,
            sort_order=unit_type.sort_order,
            is_active=unit_type.is_active,
        )
        for unit_type in rows
    ]
