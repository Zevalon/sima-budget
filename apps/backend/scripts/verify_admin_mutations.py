import asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    UserUnitMembership,
)
from app.modules.roles.models import Role, RolePermission, UserRoleAssignment
from app.modules.users.models import User

ADMIN_USERNAME = "phase1c2_admin"
CREATED_USERNAME = "phase1c2_user"
CUSTOM_ROLE_CODE = "PHASE1C2_TEST_ROLE"
CUSTOM_UNIT_CODE = "P1C2_TEST"
PASSWORD = "Phase1C2-Verification!"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        created_user = await session.scalar(select(User).where(User.username == CREATED_USERNAME))
        admin_user = await session.scalar(select(User).where(User.username == ADMIN_USERNAME))
        custom_role = await session.scalar(select(Role).where(Role.code == CUSTOM_ROLE_CODE))
        custom_unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == CUSTOM_UNIT_CODE)
        )

        user_ids = [user.id for user in (created_user, admin_user) if user is not None]
        if user_ids:
            await session.execute(delete(UserSession).where(UserSession.user_id.in_(user_ids)))
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id.in_(user_ids))
            )
            await session.execute(
                delete(UserUnitMembership).where(UserUnitMembership.user_id.in_(user_ids))
            )
            await session.execute(delete(AuditLog).where(AuditLog.actor_user_id.in_(user_ids)))
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
            full_name="Phase 1C2 Verification Admin",
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


async def verify() -> None:
    await create_admin()

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
        follow_redirects=True,
    ) as client:
        login = await client.post(
            "/api/v1/auth/login",
            json={"username": ADMIN_USERNAME, "password": PASSWORD},
        )
        assert login.status_code == 200, login.text
        csrf = login.json()["csrf_token"]
        headers = {"X-CSRF-Token": csrf}

        units_response = await client.get("/api/v1/admin/organization-units")
        unit_types_response = await client.get("/api/v1/admin/organization-unit-types")
        permissions_response = await client.get("/api/v1/admin/permissions")

        assert units_response.status_code == 200, units_response.text
        assert unit_types_response.status_code == 200, unit_types_response.text
        assert permissions_response.status_code == 200, permissions_response.text

        units = units_response.json()
        unit_types = unit_types_response.json()
        root_unit = next(item for item in units if item["code"] == "ROOT")
        other_type = next(item for item in unit_types if item["code"] == "OTHER")

        create_unit = await client.post(
            "/api/v1/admin/organization-units",
            headers=headers,
            json={
                "parent_id": root_unit["id"],
                "unit_type_id": other_type["id"],
                "code": CUSTOM_UNIT_CODE,
                "name": "Phase 1C2 Test Unit",
                "can_receive_budget": True,
                "can_create_budget_plan": True,
            },
        )
        assert create_unit.status_code == 201, create_unit.text
        created_unit = create_unit.json()

        create_role = await client.post(
            "/api/v1/admin/roles",
            headers=headers,
            json={
                "code": CUSTOM_ROLE_CODE,
                "name": "Phase 1C2 Test Role",
                "description": "Temporary verification role",
                "permission_codes": ["organization_units.view"],
            },
        )
        assert create_role.status_code == 201, create_role.text
        created_role = create_role.json()

        create_user = await client.post(
            "/api/v1/admin/users",
            headers=headers,
            json={
                "username": CREATED_USERNAME,
                "email": None,
                "full_name": "Phase 1C2 Test User",
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
        assert create_user.status_code == 201, create_user.text
        created_user = create_user.json()

        user_detail = await client.get(f"/api/v1/admin/users/{created_user['id']}")
        assert user_detail.status_code == 200, user_detail.text
        assert user_detail.json()["roles"][0]["role_code"] == CUSTOM_ROLE_CODE

        deactivate_user = await client.post(
            f"/api/v1/admin/users/{created_user['id']}/deactivate",
            headers=headers,
        )
        assert deactivate_user.status_code == 204, deactivate_user.text

        deactivate_unit = await client.post(
            f"/api/v1/admin/organization-units/{created_unit['id']}/deactivate",
            headers=headers,
        )
        assert deactivate_unit.status_code == 204, deactivate_unit.text

    await cleanup()
    await get_engine().dispose()
    print("Administration mutation verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
