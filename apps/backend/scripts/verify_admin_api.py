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

ADMIN_USERNAME = "phase1c1_admin"
VIEWER_USERNAME = "phase1c1_viewer"
PASSWORD = "Phase1C1-Verification!"


async def cleanup_user(username: str) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == username))
        if user is None:
            return
        await session.execute(delete(AuditLog).where(AuditLog.entity_id == user.id))
        await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
        await session.delete(user)
        await session.commit()


async def create_user(username: str, role_code: str) -> None:
    await cleanup_user(username)

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
                Role.code == role_code,
            )
        )
        if root_unit is None or role is None:
            raise RuntimeError("Required foundation data is missing.")

        user = User(
            username=username,
            email=None,
            full_name=f"Verification {role_code}",
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
                role_id=role.id,
                scope_type="ALL" if role_code == "SYSTEM_ADMIN" else "OWN_UNIT",
                scope_unit_id=None if role_code == "SYSTEM_ADMIN" else root_unit.id,
            )
        )
        await session.commit()


async def login_client(username: str) -> AsyncClient:
    transport = ASGITransport(app=app)
    client = AsyncClient(
        transport=transport,
        base_url="http://localhost",
        follow_redirects=True,
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return client


async def verify() -> None:
    await create_user(ADMIN_USERNAME, "SYSTEM_ADMIN")
    await create_user(VIEWER_USERNAME, "VIEWER")

    admin = await login_client(ADMIN_USERNAME)
    viewer = await login_client(VIEWER_USERNAME)

    admin_users = await admin.get("/api/v1/admin/users")
    assert admin_users.status_code == 200, admin_users.text

    admin_roles = await admin.get("/api/v1/admin/roles")
    assert admin_roles.status_code == 200, admin_roles.text

    admin_permissions = await admin.get("/api/v1/admin/permissions")
    assert admin_permissions.status_code == 200, admin_permissions.text

    admin_units = await admin.get("/api/v1/admin/organization-units")
    assert admin_units.status_code == 200, admin_units.text

    viewer_users = await viewer.get("/api/v1/admin/users")
    assert viewer_users.status_code == 403, viewer_users.text

    viewer_units = await viewer.get("/api/v1/admin/organization-units")
    assert viewer_units.status_code == 200, viewer_units.text

    await admin.aclose()
    await viewer.aclose()

    await cleanup_user(ADMIN_USERNAME)
    await cleanup_user(VIEWER_USERNAME)
    await get_engine().dispose()

    print("Administration authorization verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
