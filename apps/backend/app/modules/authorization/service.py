from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organizations.models import OrganizationUnit
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment


async def get_permission_scope_assignments(
    session: AsyncSession,
    *,
    user_id: UUID,
    permission_code: str,
    now: datetime | None = None,
) -> list[UserRoleAssignment]:
    current_time = now or datetime.now(UTC)

    assignments = (
        await session.scalars(
            select(UserRoleAssignment)
            .join(Role, Role.id == UserRoleAssignment.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(
                UserRoleAssignment.user_id == user_id,
                Permission.code == permission_code,
                Role.is_active.is_(True),
                or_(
                    UserRoleAssignment.valid_from.is_(None),
                    UserRoleAssignment.valid_from <= current_time,
                ),
                or_(
                    UserRoleAssignment.valid_until.is_(None),
                    UserRoleAssignment.valid_until > current_time,
                ),
            )
        )
    ).all()

    return list(assignments)


async def has_permission(
    session: AsyncSession,
    *,
    user_id: UUID,
    permission_code: str,
) -> bool:
    assignments = await get_permission_scope_assignments(
        session,
        user_id=user_id,
        permission_code=permission_code,
    )
    return bool(assignments)


async def can_access_unit(
    session: AsyncSession,
    *,
    user_id: UUID,
    permission_code: str,
    unit_id: UUID,
) -> bool:
    assignments = await get_permission_scope_assignments(
        session,
        user_id=user_id,
        permission_code=permission_code,
    )
    if not assignments:
        return False

    if any(assignment.scope_type == "ALL" for assignment in assignments):
        return True

    unit = await session.scalar(select(OrganizationUnit).where(OrganizationUnit.id == unit_id))
    if unit is None:
        return False

    unit_rows = (
        await session.execute(
            select(OrganizationUnit.id, OrganizationUnit.parent_id).where(
                OrganizationUnit.organization_id == unit.organization_id
            )
        )
    ).all()
    parent_by_id = {row.id: row.parent_id for row in unit_rows}

    for assignment in assignments:
        scope_unit_id = assignment.scope_unit_id
        if scope_unit_id is None:
            continue

        if assignment.scope_type == "OWN_UNIT" and scope_unit_id == unit_id:
            return True

        if assignment.scope_type == "OWN_UNIT_AND_CHILDREN":
            current_id: UUID | None = unit_id
            visited: set[UUID] = set()

            while current_id is not None and current_id not in visited:
                if current_id == scope_unit_id:
                    return True
                visited.add(current_id)
                current_id = parent_by_id.get(current_id)

    return False
