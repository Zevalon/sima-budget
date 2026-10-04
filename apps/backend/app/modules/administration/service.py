from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.administration.repository import get_user_detail
from app.modules.administration.schemas import (
    AdminRoleSummary,
    AdminUserDetail,
    OrganizationUnitCreateRequest,
    OrganizationUnitUpdateRequest,
    RoleAssignmentInput,
    RoleCreateRequest,
    RoleUpdateRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from app.modules.audit.service import record_audit
from app.modules.auth.models import UserSession
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    OrganizationUnitType,
    UserUnitMembership,
)
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.users.models import User


def conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


async def get_default_organization(session: AsyncSession) -> Organization:
    organization = await session.scalar(select(Organization).where(Organization.code == "DEFAULT"))
    if organization is None:
        raise RuntimeError("Default organization belum tersedia.")
    return organization


async def ensure_user_identity_available(
    session: AsyncSession,
    *,
    username: str,
    email: str | None,
    exclude_user_id: UUID | None = None,
) -> None:
    conditions = [User.username == username]
    if email:
        conditions.append(User.email == email)

    query = select(User).where(or_(*conditions))
    if exclude_user_id is not None:
        query = query.where(User.id != exclude_user_id)

    existing = await session.scalar(query.limit(1))
    if existing is not None:
        if existing.username == username:
            raise conflict("Username sudah digunakan.")
        raise conflict("Email sudah digunakan.")


async def validate_scope_assignment(
    session: AsyncSession,
    *,
    organization_id: UUID,
    assignment: RoleAssignmentInput,
) -> None:
    role = await session.scalar(
        select(Role).where(
            Role.id == assignment.role_id,
            Role.organization_id == organization_id,
            Role.is_active.is_(True),
        )
    )
    if role is None:
        raise not_found("Role tidak ditemukan atau tidak aktif.")

    if assignment.scope_type == "ALL":
        if assignment.scope_unit_id is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Scope ALL tidak menggunakan scope unit.",
            )
        return

    if assignment.scope_type == "OWN":
        if assignment.scope_unit_id is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Scope OWN tidak menggunakan scope unit.",
            )
        return

    if assignment.scope_unit_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Scope unit wajib untuk OWN_UNIT dan OWN_UNIT_AND_CHILDREN.",
        )

    unit = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.id == assignment.scope_unit_id,
            OrganizationUnit.organization_id == organization_id,
            OrganizationUnit.is_active.is_(True),
        )
    )
    if unit is None:
        raise not_found("Scope unit tidak ditemukan atau tidak aktif.")


async def replace_user_role_assignments(
    session: AsyncSession,
    *,
    organization_id: UUID,
    user: User,
    assignments: list[RoleAssignmentInput],
) -> None:
    for assignment in assignments:
        await validate_scope_assignment(
            session,
            organization_id=organization_id,
            assignment=assignment,
        )

    await session.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id))
    for assignment in assignments:
        session.add(
            UserRoleAssignment(
                user_id=user.id,
                role_id=assignment.role_id,
                scope_type=assignment.scope_type,
                scope_unit_id=assignment.scope_unit_id,
            )
        )


async def set_primary_membership(
    session: AsyncSession,
    *,
    organization_id: UUID,
    user: User,
    unit_id: UUID,
    job_title: str | None,
) -> None:
    unit = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.id == unit_id,
            OrganizationUnit.organization_id == organization_id,
            OrganizationUnit.is_active.is_(True),
        )
    )
    if unit is None:
        raise not_found("Unit organisasi tidak ditemukan atau tidak aktif.")

    memberships = (
        await session.scalars(
            select(UserUnitMembership).where(UserUnitMembership.user_id == user.id)
        )
    ).all()

    target: UserUnitMembership | None = None
    for membership in memberships:
        membership.is_primary = membership.organization_unit_id == unit_id
        if membership.organization_unit_id == unit_id:
            target = membership

    if target is None:
        session.add(
            UserUnitMembership(
                user_id=user.id,
                organization_unit_id=unit_id,
                job_title=job_title,
                is_primary=True,
            )
        )
    else:
        target.job_title = job_title
        target.is_primary = True


async def create_user(
    session: AsyncSession,
    *,
    payload: UserCreateRequest,
    actor_user_id: UUID,
) -> AdminUserDetail:
    organization = await get_default_organization(session)
    username = payload.username.strip().lower()
    email = payload.email.strip().lower() if payload.email else None

    await ensure_user_identity_available(
        session,
        username=username,
        email=email,
    )

    user = User(
        username=username,
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        is_active=True,
        is_locked=False,
        failed_login_attempts=0,
    )
    session.add(user)
    await session.flush()

    await set_primary_membership(
        session,
        organization_id=organization.id,
        user=user,
        unit_id=payload.primary_unit_id,
        job_title=payload.job_title,
    )
    await replace_user_role_assignments(
        session,
        organization_id=organization.id,
        user=user,
        assignments=payload.role_assignments,
    )

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="USER_CREATED",
        entity_type="user",
        entity_id=user.id,
        after_data={
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        },
    )
    await session.commit()

    detail = await get_user_detail(session, user.id)
    if detail is None:
        raise RuntimeError("User baru tidak dapat dibaca kembali.")
    return detail


async def update_user(
    session: AsyncSession,
    *,
    user_id: UUID,
    payload: UserUpdateRequest,
    actor_user_id: UUID,
) -> AdminUserDetail:
    organization = await get_default_organization(session)
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise not_found("User tidak ditemukan.")

    before = {
        "email": user.email,
        "full_name": user.full_name,
    }

    next_email = user.email
    if payload.email is not None:
        next_email = payload.email.strip().lower() or None

    await ensure_user_identity_available(
        session,
        username=user.username,
        email=next_email,
        exclude_user_id=user.id,
    )

    if payload.email is not None:
        user.email = next_email
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()

    if payload.primary_unit_id is not None:
        await set_primary_membership(
            session,
            organization_id=organization.id,
            user=user,
            unit_id=payload.primary_unit_id,
            job_title=payload.job_title,
        )

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="USER_UPDATED",
        entity_type="user",
        entity_id=user.id,
        before_data=before,
        after_data={
            "email": user.email,
            "full_name": user.full_name,
        },
    )
    await session.commit()

    detail = await get_user_detail(session, user.id)
    if detail is None:
        raise RuntimeError("User tidak dapat dibaca kembali.")
    return detail


async def deactivate_user(
    session: AsyncSession,
    *,
    user_id: UUID,
    actor_user_id: UUID,
) -> None:
    organization = await get_default_organization(session)
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise not_found("User tidak ditemukan.")
    if user.id == actor_user_id:
        raise conflict("Administrator tidak dapat menonaktifkan akunnya sendiri.")

    user.is_active = False
    await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="USER_DEACTIVATED",
        entity_type="user",
        entity_id=user.id,
    )
    await session.commit()


async def reset_user_password(
    session: AsyncSession,
    *,
    user_id: UUID,
    password: str,
    actor_user_id: UUID,
) -> None:
    organization = await get_default_organization(session)
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise not_found("User tidak ditemukan.")

    user.password_hash = hash_password(password)
    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_until = None
    await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="USER_PASSWORD_RESET",
        entity_type="user",
        entity_id=user.id,
    )
    await session.commit()


async def update_user_roles(
    session: AsyncSession,
    *,
    user_id: UUID,
    assignments: list[RoleAssignmentInput],
    actor_user_id: UUID,
) -> AdminUserDetail:
    organization = await get_default_organization(session)
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise not_found("User tidak ditemukan.")

    await replace_user_role_assignments(
        session,
        organization_id=organization.id,
        user=user,
        assignments=assignments,
    )
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="USER_ROLES_UPDATED",
        entity_type="user",
        entity_id=user.id,
    )
    await session.commit()

    detail = await get_user_detail(session, user.id)
    if detail is None:
        raise RuntimeError("User tidak dapat dibaca kembali.")
    return detail


async def set_role_permissions(
    session: AsyncSession,
    *,
    role: Role,
    permission_codes: list[str],
) -> None:
    unique_codes = sorted(set(permission_codes))
    permissions = (
        await session.scalars(select(Permission).where(Permission.code.in_(unique_codes)))
    ).all()
    if len(permissions) != len(unique_codes):
        found_codes = {permission.code for permission in permissions}
        missing = sorted(set(unique_codes) - found_codes)
        raise not_found(f"Permission tidak ditemukan: {', '.join(missing)}")

    await session.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
    for permission in permissions:
        session.add(
            RolePermission(
                role_id=role.id,
                permission_id=permission.id,
            )
        )


async def create_role(
    session: AsyncSession,
    *,
    payload: RoleCreateRequest,
    actor_user_id: UUID,
) -> AdminRoleSummary:
    organization = await get_default_organization(session)
    code = payload.code.strip().upper()

    existing = await session.scalar(
        select(Role).where(
            Role.organization_id == organization.id,
            Role.code == code,
        )
    )
    if existing is not None:
        raise conflict("Kode role sudah digunakan.")

    role = Role(
        organization_id=organization.id,
        code=code,
        name=payload.name.strip(),
        description=payload.description,
        is_system_role=False,
        is_active=True,
    )
    session.add(role)
    await session.flush()

    await set_role_permissions(
        session,
        role=role,
        permission_codes=payload.permission_codes,
    )
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ROLE_CREATED",
        entity_type="role",
        entity_id=role.id,
        after_data={"code": role.code, "name": role.name},
    )
    await session.commit()

    return AdminRoleSummary(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        is_system_role=role.is_system_role,
        is_active=role.is_active,
    )


async def update_role(
    session: AsyncSession,
    *,
    role_id: UUID,
    payload: RoleUpdateRequest,
    actor_user_id: UUID,
) -> AdminRoleSummary:
    organization = await get_default_organization(session)
    role = await session.scalar(
        select(Role).where(
            Role.id == role_id,
            Role.organization_id == organization.id,
        )
    )
    if role is None:
        raise not_found("Role tidak ditemukan.")

    before = {
        "name": role.name,
        "description": role.description,
        "is_active": role.is_active,
    }

    if payload.name is not None:
        role.name = payload.name.strip()
    if payload.description is not None:
        role.description = payload.description
    if payload.is_active is not None:
        role.is_active = payload.is_active

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ROLE_UPDATED",
        entity_type="role",
        entity_id=role.id,
        before_data=before,
        after_data={
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
        },
    )
    await session.commit()

    return AdminRoleSummary(
        id=role.id,
        code=role.code,
        name=role.name,
        description=role.description,
        is_system_role=role.is_system_role,
        is_active=role.is_active,
    )


async def replace_role_permissions(
    session: AsyncSession,
    *,
    role_id: UUID,
    permission_codes: list[str],
    actor_user_id: UUID,
) -> None:
    organization = await get_default_organization(session)
    role = await session.scalar(
        select(Role).where(
            Role.id == role_id,
            Role.organization_id == organization.id,
        )
    )
    if role is None:
        raise not_found("Role tidak ditemukan.")

    await set_role_permissions(
        session,
        role=role,
        permission_codes=permission_codes,
    )
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ROLE_PERMISSIONS_UPDATED",
        entity_type="role",
        entity_id=role.id,
        after_data={"permission_codes": sorted(set(permission_codes))},
    )
    await session.commit()


async def ensure_parent_is_valid(
    session: AsyncSession,
    *,
    organization_id: UUID,
    unit_id: UUID | None,
    parent_id: UUID | None,
) -> None:
    if parent_id is None:
        return
    if unit_id is not None and unit_id == parent_id:
        raise conflict("Unit tidak dapat menjadi parent untuk dirinya sendiri.")

    parent = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.id == parent_id,
            OrganizationUnit.organization_id == organization_id,
            OrganizationUnit.is_active.is_(True),
        )
    )
    if parent is None:
        raise not_found("Parent unit tidak ditemukan atau tidak aktif.")

    if unit_id is None:
        return

    units = (
        await session.execute(
            select(OrganizationUnit.id, OrganizationUnit.parent_id).where(
                OrganizationUnit.organization_id == organization_id
            )
        )
    ).all()
    parent_by_id = {row.id: row.parent_id for row in units}

    current_id: UUID | None = parent_id
    visited: set[UUID] = set()
    while current_id is not None and current_id not in visited:
        if current_id == unit_id:
            raise conflict("Parent unit akan membuat siklus hierarchy.")
        visited.add(current_id)
        current_id = parent_by_id.get(current_id)


async def create_organization_unit(
    session: AsyncSession,
    *,
    payload: OrganizationUnitCreateRequest,
    actor_user_id: UUID,
) -> OrganizationUnit:
    organization = await get_default_organization(session)
    code = payload.code.strip().upper()

    existing = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.organization_id == organization.id,
            OrganizationUnit.code == code,
        )
    )
    if existing is not None:
        raise conflict("Kode unit sudah digunakan.")

    unit_type = await session.scalar(
        select(OrganizationUnitType).where(
            OrganizationUnitType.id == payload.unit_type_id,
            OrganizationUnitType.organization_id == organization.id,
            OrganizationUnitType.is_active.is_(True),
        )
    )
    if unit_type is None:
        raise not_found("Tipe unit tidak ditemukan atau tidak aktif.")

    await ensure_parent_is_valid(
        session,
        organization_id=organization.id,
        unit_id=None,
        parent_id=payload.parent_id,
    )

    unit = OrganizationUnit(
        organization_id=organization.id,
        unit_type_id=payload.unit_type_id,
        parent_id=payload.parent_id,
        code=code,
        name=payload.name.strip(),
        can_receive_budget=payload.can_receive_budget,
        can_create_budget_plan=payload.can_create_budget_plan,
        is_active=True,
    )
    session.add(unit)
    await session.flush()

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ORGANIZATION_UNIT_CREATED",
        entity_type="organization_unit",
        entity_id=unit.id,
        after_data={"code": unit.code, "name": unit.name},
    )
    await session.commit()
    return unit


async def update_organization_unit(
    session: AsyncSession,
    *,
    unit_id: UUID,
    payload: OrganizationUnitUpdateRequest,
    actor_user_id: UUID,
) -> OrganizationUnit:
    organization = await get_default_organization(session)
    unit = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.id == unit_id,
            OrganizationUnit.organization_id == organization.id,
        )
    )
    if unit is None:
        raise not_found("Unit organisasi tidak ditemukan.")

    before = {
        "name": unit.name,
        "parent_id": str(unit.parent_id) if unit.parent_id else None,
        "unit_type_id": str(unit.unit_type_id),
        "can_receive_budget": unit.can_receive_budget,
        "can_create_budget_plan": unit.can_create_budget_plan,
    }

    if payload.parent_id is not None:
        await ensure_parent_is_valid(
            session,
            organization_id=organization.id,
            unit_id=unit.id,
            parent_id=payload.parent_id,
        )
        unit.parent_id = payload.parent_id

    if payload.unit_type_id is not None:
        unit_type = await session.scalar(
            select(OrganizationUnitType).where(
                OrganizationUnitType.id == payload.unit_type_id,
                OrganizationUnitType.organization_id == organization.id,
                OrganizationUnitType.is_active.is_(True),
            )
        )
        if unit_type is None:
            raise not_found("Tipe unit tidak ditemukan atau tidak aktif.")
        unit.unit_type_id = payload.unit_type_id

    if payload.name is not None:
        unit.name = payload.name.strip()
    if payload.can_receive_budget is not None:
        unit.can_receive_budget = payload.can_receive_budget
    if payload.can_create_budget_plan is not None:
        unit.can_create_budget_plan = payload.can_create_budget_plan

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ORGANIZATION_UNIT_UPDATED",
        entity_type="organization_unit",
        entity_id=unit.id,
        before_data=before,
        after_data={
            "name": unit.name,
            "parent_id": str(unit.parent_id) if unit.parent_id else None,
            "unit_type_id": str(unit.unit_type_id),
            "can_receive_budget": unit.can_receive_budget,
            "can_create_budget_plan": unit.can_create_budget_plan,
        },
    )
    await session.commit()
    return unit


async def deactivate_organization_unit(
    session: AsyncSession,
    *,
    unit_id: UUID,
    actor_user_id: UUID,
) -> None:
    organization = await get_default_organization(session)
    unit = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.id == unit_id,
            OrganizationUnit.organization_id == organization.id,
        )
    )
    if unit is None:
        raise not_found("Unit organisasi tidak ditemukan.")
    if unit.code == "ROOT":
        raise conflict("Root organization unit tidak dapat dinonaktifkan.")

    active_child = await session.scalar(
        select(OrganizationUnit.id).where(
            OrganizationUnit.parent_id == unit.id,
            OrganizationUnit.is_active.is_(True),
        )
    )
    if active_child is not None:
        raise conflict("Unit masih memiliki child aktif.")

    unit.is_active = False
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ORGANIZATION_UNIT_DEACTIVATED",
        entity_type="organization_unit",
        entity_id=unit.id,
    )
    await session.commit()
