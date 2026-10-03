import asyncio
from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.users.models import User

USERNAME = "phase1b_check"
PASSWORD = "Phase1B-Verification-Only!"


async def cleanup_user() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        if user is None:
            return
        await session.execute(delete(AuditLog).where(AuditLog.entity_id == user.id))
        await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
        await session.delete(user)
        await session.commit()


async def create_test_user() -> None:
    await cleanup_user()
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
        role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "SYSTEM_ADMIN",
            )
        )
        if root_unit is None or role is None:
            raise RuntimeError("Required foundation data is missing.")

        user = User(
            username=USERNAME,
            email=None,
            full_name="Phase 1B Verification User",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
            last_login_at=None,
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
                role_id=role.id,
                scope_type="ALL",
                scope_unit_id=None,
            )
        )
        await session.commit()


async def verify() -> None:
    settings = get_settings()
    await create_test_user()

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
        follow_redirects=True,
    ) as client:
        failed = await client.post(
            "/api/v1/auth/login",
            json={"username": USERNAME, "password": "incorrect-password"},
        )
        assert failed.status_code == 401, failed.text

        logged_in = await client.post(
            "/api/v1/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
        )
        assert logged_in.status_code == 200, logged_in.text
        body = logged_in.json()
        assert body["username"] == USERNAME
        assert "settings.update" in body["permissions"]
        assert body["csrf_token"]

        cookie = client.cookies.get(settings.session_cookie_name)
        assert cookie

        me = await client.get("/api/v1/auth/me")
        assert me.status_code == 200, me.text
        assert me.json()["username"] == USERNAME

        no_csrf = await client.post("/api/v1/auth/logout")
        assert no_csrf.status_code == 403, no_csrf.text

        logout_response = await client.post(
            "/api/v1/auth/logout",
            headers={"X-CSRF-Token": body["csrf_token"]},
        )
        assert logout_response.status_code == 204, logout_response.text

        after_logout = await client.get("/api/v1/auth/me")
        assert after_logout.status_code == 401, after_logout.text

    await cleanup_user()
    await get_engine().dispose()
    print(f"Authentication verification: OK ({datetime.now(UTC).isoformat()})")


if __name__ == "__main__":
    asyncio.run(verify())
