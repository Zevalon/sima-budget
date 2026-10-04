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
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.users.models import User

USERNAME = "phase1d1_admin"
PASSWORD = "Phase1D1-Verification!"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        if user is None:
            return

        await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user.id))
        await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
        await session.execute(
            delete(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)
        )
        await session.execute(
            delete(UserUnitMembership).where(UserUnitMembership.user_id == user.id)
        )
        await session.delete(user)
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

        user = User(
            username=USERNAME,
            email=None,
            full_name="Phase 1D1 Verification Admin",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        session.add(user)
        await session.flush()

        session.add(
            UserUnitMembership(
                user_id=user.id,
                organization_unit_id=root_unit.id,
                job_title="Verification",
                is_primary=True,
            )
        )
        session.add(
            UserRoleAssignment(
                user_id=user.id,
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
            json={"username": USERNAME, "password": PASSWORD},
        )
        assert login.status_code == 200, login.text
        csrf = login.json()["csrf_token"]

        settings_before = await client.get("/api/v1/settings")
        assert settings_before.status_code == 200, settings_before.text
        original = settings_before.json()

        no_csrf = await client.patch(
            "/api/v1/settings",
            json={"application_name": "Should Not Save"},
        )
        assert no_csrf.status_code == 403, no_csrf.text

        updated = await client.patch(
            "/api/v1/settings",
            headers={"X-CSRF-Token": csrf},
            json={"application_name": "SIMA Verification"},
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["application_name"] == "SIMA Verification"

        audit = await client.get(
            "/api/v1/audit",
            params={"action": "APPLICATION_SETTINGS_UPDATED"},
        )
        assert audit.status_code == 200, audit.text
        assert audit.json()["total"] >= 1
        assert any(
            item["action"] == "APPLICATION_SETTINGS_UPDATED" for item in audit.json()["items"]
        )

        restore_payload = {
            "application_name": original["application_name"],
            "application_short_name": original["application_short_name"],
            "organization_display_name": original["organization_display_name"],
            "primary_color": original["primary_color"],
            "secondary_color": original["secondary_color"],
            "currency_code": original["currency_code"],
            "timezone": original["timezone"],
            "date_format": original["date_format"],
            "allow_annual_budget_revision": original["allow_annual_budget_revision"],
            "allow_budget_transfer": original["allow_budget_transfer"],
            "allow_self_approval": original["allow_self_approval"],
        }
        restored = await client.patch(
            "/api/v1/settings",
            headers={"X-CSRF-Token": csrf},
            json=restore_payload,
        )
        assert restored.status_code == 200, restored.text

    await cleanup()
    await get_engine().dispose()
    print("Foundation administration verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
