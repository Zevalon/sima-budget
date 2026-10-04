import asyncio
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.annual_budgets.models import AnnualBudget, AnnualBudgetApproval
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import FiscalYear
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.users.models import User

USERNAME = "phase2b1_budget_admin"
PASSWORD = "Phase2B1-Verification!"
FISCAL_CODE = "P2B1-2197"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        fiscal_year = await session.scalar(select(FiscalYear).where(FiscalYear.code == FISCAL_CODE))
        budget = None
        if fiscal_year is not None:
            budget = await session.scalar(
                select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fiscal_year.id)
            )

        entity_ids = []
        if budget is not None:
            entity_ids.append(budget.id)
        if fiscal_year is not None:
            entity_ids.append(fiscal_year.id)

        if budget is not None:
            await session.execute(
                delete(AnnualBudgetApproval).where(
                    AnnualBudgetApproval.annual_budget_id == budget.id
                )
            )
            await session.delete(budget)

        if user is not None:
            await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user.id))
            await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)
            )
            await session.execute(
                delete(UserUnitMembership).where(UserUnitMembership.user_id == user.id)
            )

        if entity_ids:
            await session.execute(delete(AuditLog).where(AuditLog.entity_id.in_(entity_ids)))

        if fiscal_year is not None:
            await session.delete(fiscal_year)
        if user is not None:
            await session.delete(user)

        await session.commit()


async def create_budget_admin() -> None:
    await cleanup()
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            raise RuntimeError("Default organization belum tersedia.")

        root_unit = await session.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.code == "ROOT",
            )
        )
        role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "BUDGET_ADMIN",
            )
        )
        if root_unit is None or role is None:
            raise RuntimeError("Bootstrap BUDGET_ADMIN belum tersedia.")

        user = User(
            username=USERNAME,
            email=None,
            full_name="Phase 2B1 Budget Admin",
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
                scope_type="ALL",
                scope_unit_id=None,
            )
        )
        await session.commit()


async def verify_role_separation() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            raise RuntimeError("Default organization belum tersedia.")

        async def permission_codes(role_code: str) -> set[str]:
            return set(
                (
                    await session.scalars(
                        select(Permission.code)
                        .join(RolePermission, RolePermission.permission_id == Permission.id)
                        .join(Role, Role.id == RolePermission.role_id)
                        .where(
                            Role.organization_id == organization.id,
                            Role.code == role_code,
                        )
                    )
                ).all()
            )

        system_admin = await permission_codes("SYSTEM_ADMIN")
        budget_admin = await permission_codes("BUDGET_ADMIN")
        assert "annual_budgets.view" in system_admin
        assert "annual_budgets.create" not in system_admin
        assert {
            "annual_budgets.view",
            "annual_budgets.create",
            "annual_budgets.update",
            "annual_budgets.submit",
        } <= budget_admin


async def verify() -> None:
    await create_budget_admin()
    await verify_role_separation()
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
        login_data = login.json()
        csrf = login_data["csrf_token"]
        permissions = set(login_data["permissions"])
        assert {
            "annual_budgets.view",
            "annual_budgets.create",
            "annual_budgets.update",
            "annual_budgets.submit",
        } <= permissions
        headers = {"X-CSRF-Token": csrf}

        fiscal_year = await client.post(
            "/api/v1/fiscal-years",
            headers=headers,
            json={
                "code": FISCAL_CODE,
                "year": 2197,
                "start_date": "2197-01-01",
                "end_date": "2197-12-31",
            },
        )
        assert fiscal_year.status_code == 201, fiscal_year.text
        fiscal_year_id = fiscal_year.json()["id"]

        planning = await client.post(
            f"/api/v1/fiscal-years/{fiscal_year_id}/transition",
            headers=headers,
            json={"target_status": "PLANNING"},
        )
        assert planning.status_code == 200, planning.text

        no_csrf = await client.post(
            "/api/v1/annual-budgets",
            json={
                "fiscal_year_id": fiscal_year_id,
                "amount": "500000000000.00",
                "notes": "Phase 2B1 verification",
            },
        )
        assert no_csrf.status_code == 403, no_csrf.text

        created = await client.post(
            "/api/v1/annual-budgets",
            headers=headers,
            json={
                "fiscal_year_id": fiscal_year_id,
                "amount": "500000000000.00",
                "notes": "Phase 2B1 verification",
            },
        )
        assert created.status_code == 201, created.text
        created_data = created.json()
        budget_id = created_data["id"]
        assert created_data["status"] == "DRAFT"
        assert Decimal(created_data["amount"]) == Decimal("500000000000.00")

        duplicate = await client.post(
            "/api/v1/annual-budgets",
            headers=headers,
            json={
                "fiscal_year_id": fiscal_year_id,
                "amount": "1.00",
            },
        )
        assert duplicate.status_code == 409, duplicate.text

        updated = await client.patch(
            f"/api/v1/annual-budgets/{budget_id}",
            headers=headers,
            json={
                "amount": "510000000000.25",
                "notes": "Updated verification budget",
            },
        )
        assert updated.status_code == 200, updated.text
        assert Decimal(updated.json()["amount"]) == Decimal("510000000000.25")

        submitted = await client.post(
            f"/api/v1/annual-budgets/{budget_id}/submit",
            headers=headers,
        )
        assert submitted.status_code == 200, submitted.text
        assert submitted.json()["status"] == "PENDING_APPROVAL"

        locked_update = await client.patch(
            f"/api/v1/annual-budgets/{budget_id}",
            headers=headers,
            json={"amount": "520000000000.00"},
        )
        assert locked_update.status_code == 409, locked_update.text

        approvals = await client.get(f"/api/v1/annual-budgets/{budget_id}/approvals")
        assert approvals.status_code == 200, approvals.text
        approval_rows = approvals.json()
        assert len(approval_rows) == 1
        assert approval_rows[0]["submission_no"] == 1
        assert approval_rows[0]["status"] == "PENDING"

        listed = await client.get(
            "/api/v1/annual-budgets",
            params={"fiscal_year_id": fiscal_year_id},
        )
        assert listed.status_code == 200, listed.text
        assert len(listed.json()) == 1

    session_factory = get_session_factory()
    async with session_factory() as session:
        audit_event = await session.scalar(
            select(AuditLog).where(
                AuditLog.action == "ANNUAL_BUDGET_SUBMITTED",
                AuditLog.entity_id == budget_id,
            )
        )
        assert audit_event is not None

    await cleanup()
    await get_engine().dispose()
    print("Phase 2B1 annual budget core verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
