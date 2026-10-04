import asyncio

from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.administration.service import _ensure_system_admin_continuity
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    UserUnitMembership,
)
from app.modules.roles.models import Role, RolePermission, UserRoleAssignment
from app.modules.users.models import User

ADMIN_USERNAME = "phase1d2_admin"
TARGET_USERNAME = "phase1d2_target"
CUSTOM_ROLE_CODE = "PHASE1D2_TEST_ROLE"
CUSTOM_UNIT_CODE = "P1D2_TEST"
PASSWORD = "Phase1D2-Verification!"
GUARD_ORG_CODE = "P1D2_GUARD"
GUARD_USERNAME = "phase1d2_guard_admin"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        users = (
            await session.scalars(
                select(User).where(User.username.in_([ADMIN_USERNAME, TARGET_USERNAME]))
            )
        ).all()
        user_ids = [user.id for user in users]

        custom_role = await session.scalar(select(Role).where(Role.code == CUSTOM_ROLE_CODE))
        custom_unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == CUSTOM_UNIT_CODE)
        )

        if user_ids:
            await session.execute(delete(AuditLog).where(AuditLog.actor_user_id.in_(user_ids)))
            await session.execute(delete(UserSession).where(UserSession.user_id.in_(user_ids)))
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id.in_(user_ids))
            )
            await session.execute(
                delete(UserUnitMembership).where(UserUnitMembership.user_id.in_(user_ids))
            )
            await session.execute(delete(User).where(User.id.in_(user_ids)))

        if custom_role is not None:
            await session.execute(
                delete(RolePermission).where(RolePermission.role_id == custom_role.id)
            )
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.role_id == custom_role.id)
            )
            await session.delete(custom_role)

        if custom_unit is not None:
            await session.execute(
                delete(UserUnitMembership).where(
                    UserUnitMembership.organization_unit_id == custom_unit.id
                )
            )
            await session.delete(custom_unit)

        await session.commit()


async def create_admin() -> None:
    await cleanup()
    session_factory = get_session_factory()

    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            raise RuntimeError("Foundation bootstrap is missing.")

        root_unit = await session.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.code == "ROOT",
            )
        )
        system_admin = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "SYSTEM_ADMIN",
            )
        )
        if root_unit is None or system_admin is None:
            raise RuntimeError("Required foundation data is missing.")

        admin = User(
            username=ADMIN_USERNAME,
            email=None,
            full_name="Phase 1D2 Verification Admin",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        session.add(admin)
        await session.flush()

        session.add(
            UserUnitMembership(
                user_id=admin.id,
                organization_unit_id=root_unit.id,
                job_title="Verification",
                is_primary=True,
            )
        )
        session.add(
            UserRoleAssignment(
                user_id=admin.id,
                role_id=system_admin.id,
                scope_type="ALL",
                scope_unit_id=None,
            )
        )
        await session.commit()


async def verify_isolated_last_admin_guard() -> None:
    """Verify the last-admin invariant without touching the real DEFAULT organization."""
    session_factory = get_session_factory()

    async with session_factory() as session:
        stale_user = await session.scalar(select(User).where(User.username == GUARD_USERNAME))
        stale_organization = await session.scalar(
            select(Organization).where(Organization.code == GUARD_ORG_CODE)
        )

        if stale_user is not None:
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id == stale_user.id)
            )
            await session.delete(stale_user)

        if stale_organization is not None:
            await session.execute(delete(Role).where(Role.organization_id == stale_organization.id))
            await session.delete(stale_organization)

        await session.commit()

        organization = Organization(
            code=GUARD_ORG_CODE,
            name="Phase 1D2 Guard Verification",
            legal_name=None,
            is_active=True,
        )
        session.add(organization)
        await session.flush()

        role = Role(
            organization_id=organization.id,
            code="SYSTEM_ADMIN",
            name="System Administrator",
            description="Temporary isolated continuity verification role",
            is_system_role=True,
            is_active=True,
        )
        user = User(
            username=GUARD_USERNAME,
            email=None,
            full_name="Phase 1D2 Guard Admin",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        session.add_all([role, user])
        await session.flush()

        session.add(
            UserRoleAssignment(
                user_id=user.id,
                role_id=role.id,
                scope_type="ALL",
                scope_unit_id=None,
            )
        )
        await session.commit()

        try:
            try:
                await _ensure_system_admin_continuity(
                    session,
                    organization_id=organization.id,
                    user_id=user.id,
                    keeps_system_admin_all=False,
                )
            except HTTPException as exc:
                assert exc.status_code == 409, exc.detail
            else:
                raise AssertionError("Last System Administrator guard did not reject role removal.")
        finally:
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)
            )
            await session.delete(user)
            await session.delete(role)
            await session.delete(organization)
            await session.commit()


async def verify() -> None:
    await create_admin()

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
        follow_redirects=True,
    ) as admin_client:
        login = await admin_client.post(
            "/api/v1/auth/login",
            json={"username": ADMIN_USERNAME, "password": PASSWORD},
        )
        assert login.status_code == 200, login.text
        admin_data = login.json()
        csrf = admin_data["csrf_token"]
        assert admin_data["application_name"]
        assert admin_data["application_short_name"]
        assert admin_data["organization_display_name"]
        headers = {"X-CSRF-Token": csrf}

        units_response = await admin_client.get("/api/v1/admin/organization-units")
        unit_types_response = await admin_client.get("/api/v1/admin/organization-unit-types")
        roles_response = await admin_client.get("/api/v1/admin/roles")
        assert units_response.status_code == 200, units_response.text
        assert unit_types_response.status_code == 200, unit_types_response.text
        assert roles_response.status_code == 200, roles_response.text

        root_unit = next(item for item in units_response.json() if item["code"] == "ROOT")
        other_type = next(item for item in unit_types_response.json() if item["code"] == "OTHER")
        system_admin = next(
            item for item in roles_response.json() if item["code"] == "SYSTEM_ADMIN"
        )

        system_role_mutation = await admin_client.put(
            f"/api/v1/admin/roles/{system_admin['id']}/permissions",
            headers=headers,
            json={"permission_codes": ["settings.view"]},
        )
        assert system_role_mutation.status_code == 409, system_role_mutation.text

        create_unit = await admin_client.post(
            "/api/v1/admin/organization-units",
            headers=headers,
            json={
                "parent_id": root_unit["id"],
                "unit_type_id": other_type["id"],
                "code": CUSTOM_UNIT_CODE,
                "name": "Phase 1D2 Protected Unit",
                "can_receive_budget": False,
                "can_create_budget_plan": False,
            },
        )
        assert create_unit.status_code == 201, create_unit.text
        created_unit = create_unit.json()

        create_role = await admin_client.post(
            "/api/v1/admin/roles",
            headers=headers,
            json={
                "code": CUSTOM_ROLE_CODE,
                "name": "Phase 1D2 Test Role",
                "description": "Temporary hardening verification role",
                "permission_codes": ["organization_units.view"],
            },
        )
        assert create_role.status_code == 201, create_role.text
        created_role = create_role.json()

        create_target = await admin_client.post(
            "/api/v1/admin/users",
            headers=headers,
            json={
                "username": TARGET_USERNAME,
                "email": None,
                "full_name": "Phase 1D2 Target User",
                "password": PASSWORD,
                "primary_unit_id": created_unit["id"],
                "job_title": "Verification",
                "role_assignments": [
                    {
                        "role_id": created_role["id"],
                        "scope_type": "OWN_UNIT",
                        "scope_unit_id": created_unit["id"],
                    }
                ],
            },
        )
        assert create_target.status_code == 201, create_target.text
        target = create_target.json()

        target_client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://localhost",
            follow_redirects=True,
        )
        target_login = await target_client.post(
            "/api/v1/auth/login",
            json={"username": TARGET_USERNAME, "password": PASSWORD},
        )
        assert target_login.status_code == 200, target_login.text

        protected_unit = await admin_client.post(
            f"/api/v1/admin/organization-units/{created_unit['id']}/deactivate",
            headers=headers,
        )
        assert protected_unit.status_code == 409, protected_unit.text

        revoke = await admin_client.post(
            f"/api/v1/admin/users/{target['id']}/revoke-sessions",
            headers=headers,
        )
        assert revoke.status_code == 204, revoke.text

        revoked_me = await target_client.get("/api/v1/auth/me")
        assert revoked_me.status_code == 401, revoked_me.text
        await target_client.aclose()

        deactivate_target = await admin_client.post(
            f"/api/v1/admin/users/{target['id']}/deactivate",
            headers=headers,
        )
        assert deactivate_target.status_code == 204, deactivate_target.text

        deactivate_unit = await admin_client.post(
            f"/api/v1/admin/organization-units/{created_unit['id']}/deactivate",
            headers=headers,
        )
        assert deactivate_unit.status_code == 204, deactivate_unit.text
        audit = await admin_client.get(
            "/api/v1/audit",
            params={"action": "USER_SESSIONS_REVOKED"},
        )
        assert audit.status_code == 200, audit.text
        assert audit.json()["total"] >= 1

    await verify_isolated_last_admin_guard()
    await cleanup()
    await get_engine().dispose()
    print("Foundation hardening verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
