from datetime import date, datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import UserSession
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.users.models import User


async def get_user_by_principal(session: AsyncSession, principal: str) -> User | None:
    normalized = principal.strip().lower()
    result = await session.execute(
        select(User).where(
            or_(
                User.username == normalized,
                User.email == normalized,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_default_organization(session: AsyncSession) -> Organization:
    organization = await session.scalar(select(Organization).where(Organization.code == "DEFAULT"))
    if organization is None:
        raise RuntimeError("Default organization has not been bootstrapped.")
    return organization


async def get_user_organization(
    session: AsyncSession,
    user_id: UUID,
) -> Organization:
    organization = await session.scalar(
        select(Organization)
        .join(Role, Role.organization_id == Organization.id)
        .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
        .where(UserRoleAssignment.user_id == user_id)
        .limit(1)
    )
    if organization is not None:
        return organization
    return await get_default_organization(session)


async def get_active_role_grants(
    session: AsyncSession,
    user_id: UUID,
    now: datetime,
) -> list[tuple[Role, UserRoleAssignment]]:
    rows = (
        await session.execute(
            select(Role, UserRoleAssignment)
            .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
            .where(
                UserRoleAssignment.user_id == user_id,
                Role.is_active.is_(True),
                or_(
                    UserRoleAssignment.valid_from.is_(None),
                    UserRoleAssignment.valid_from <= now,
                ),
                or_(
                    UserRoleAssignment.valid_until.is_(None),
                    UserRoleAssignment.valid_until > now,
                ),
            )
            .order_by(Role.name)
        )
    ).all()
    return [(role, assignment) for role, assignment in rows]


async def get_effective_permission_codes(
    session: AsyncSession,
    user_id: UUID,
    now: datetime,
) -> list[str]:
    values = (
        await session.scalars(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
            .where(
                UserRoleAssignment.user_id == user_id,
                Role.is_active.is_(True),
                or_(
                    UserRoleAssignment.valid_from.is_(None),
                    UserRoleAssignment.valid_from <= now,
                ),
                or_(
                    UserRoleAssignment.valid_until.is_(None),
                    UserRoleAssignment.valid_until > now,
                ),
            )
            .distinct()
            .order_by(Permission.code)
        )
    ).all()
    return list(values)


async def get_unit_memberships(
    session: AsyncSession,
    user_id: UUID,
) -> list[tuple[UserUnitMembership, OrganizationUnit]]:
    rows = (
        await session.execute(
            select(UserUnitMembership, OrganizationUnit)
            .join(
                OrganizationUnit,
                OrganizationUnit.id == UserUnitMembership.organization_unit_id,
            )
            .where(
                UserUnitMembership.user_id == user_id,
                or_(
                    UserUnitMembership.end_at.is_(None),
                    UserUnitMembership.end_at >= date.today(),
                ),
            )
            .order_by(UserUnitMembership.is_primary.desc(), OrganizationUnit.name)
        )
    ).all()
    return [(membership, unit) for membership, unit in rows]


async def get_session_and_user_by_token_hash(
    session: AsyncSession,
    token_hash: str,
) -> tuple[UserSession, User] | None:
    row = (
        await session.execute(
            select(UserSession, User)
            .join(User, User.id == UserSession.user_id)
            .where(UserSession.token_hash == token_hash)
        )
    ).first()
    if row is None:
        return None
    user_session, user = row
    return user_session, user
