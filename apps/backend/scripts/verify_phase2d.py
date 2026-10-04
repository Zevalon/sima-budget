import asyncio
from datetime import date
from decimal import Decimal

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.annual_budgets.models import AnnualBudget
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import FiscalYear
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    OrganizationUnitType,
    UserUnitMembership,
)
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

USERNAME = "phase2d_system_admin"
PASSWORD = "Phase2D-Verification!"
FISCAL_CODE = "P2D-2194"
UNIT_CODE = "P2D-UNIT"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        fiscal_year = await session.scalar(select(FiscalYear).where(FiscalYear.code == FISCAL_CODE))
        unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == UNIT_CODE)
        )

        entity_ids = []
        if fiscal_year is not None:
            entity_ids.append(fiscal_year.id)
            budget = await session.scalar(
                select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fiscal_year.id)
            )
            if budget is not None:
                entity_ids.append(budget.id)
                allocations = (
                    await session.scalars(
                        select(UnitAllocation).where(UnitAllocation.annual_budget_id == budget.id)
                    )
                ).all()
                entity_ids.extend(item.id for item in allocations)
                await session.execute(
                    delete(UnitAllocation).where(UnitAllocation.annual_budget_id == budget.id)
                )
                await session.delete(budget)

        if unit is not None:
            entity_ids.append(unit.id)

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
        if unit is not None:
            await session.delete(unit)
        if user is not None:
            await session.delete(user)

        await session.commit()


async def setup() -> None:
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
        unit_type = await session.scalar(
            select(OrganizationUnitType).where(
                OrganizationUnitType.organization_id == organization.id,
                OrganizationUnitType.code == "OTHER",
            )
        )
        system_admin_role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "SYSTEM_ADMIN",
            )
        )
        if root_unit is None or unit_type is None or system_admin_role is None:
            raise RuntimeError("Bootstrap Phase 2D belum lengkap.")

        admin = User(
            username=USERNAME,
            email=None,
            full_name="Phase 2D System Admin",
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
                role_id=system_admin_role.id,
                scope_type="ALL",
                scope_unit_id=None,
            )
        )

        fiscal_year = FiscalYear(
            organization_id=organization.id,
            code=FISCAL_CODE,
            year=2194,
            start_date=date(2194, 1, 1),
            end_date=date(2194, 12, 31),
            status="PLANNING",
        )
        unit = OrganizationUnit(
            organization_id=organization.id,
            unit_type_id=unit_type.id,
            parent_id=root_unit.id,
            code=UNIT_CODE,
            name="Phase 2D Protected Allocation Unit",
            can_receive_budget=True,
            can_create_budget_plan=True,
            is_active=True,
        )
        session.add_all([fiscal_year, unit])
        await session.flush()

        budget = AnnualBudget(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            amount=Decimal("1000.00"),
            notes="Phase 2D hardening verification budget",
            status="APPROVED",
            version=1,
        )
        session.add(budget)
        await session.flush()

        session.add(
            UnitAllocation(
                organization_id=organization.id,
                fiscal_year_id=fiscal_year.id,
                annual_budget_id=budget.id,
                organization_unit_id=unit.id,
                amount=Decimal("400.00"),
                notes="Open-year allocation protection",
                version=1,
            )
        )
        await session.commit()


async def verify() -> None:
    await setup()
    try:
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
            headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            units = await client.get("/api/v1/admin/organization-units")
            assert units.status_code == 200, units.text
            unit = next(item for item in units.json() if item["code"] == UNIT_CODE)

            disable_receiver = await client.patch(
                f"/api/v1/admin/organization-units/{unit['id']}",
                headers=headers,
                json={"can_receive_budget": False},
            )
            assert disable_receiver.status_code == 409, disable_receiver.text

            deactivate_open = await client.post(
                f"/api/v1/admin/organization-units/{unit['id']}/deactivate",
                headers=headers,
            )
            assert deactivate_open.status_code == 409, deactivate_open.text

        session_factory = get_session_factory()
        async with session_factory() as session:
            fiscal_year = await session.scalar(
                select(FiscalYear).where(FiscalYear.code == FISCAL_CODE)
            )
            assert fiscal_year is not None
            fiscal_year.status = "CLOSED"
            await session.commit()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://localhost",
            follow_redirects=True,
        ) as client:
            login = await client.post(
                "/api/v1/auth/login",
                json={"username": USERNAME, "password": PASSWORD},
            )
            assert login.status_code == 200, login.text
            headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            units = await client.get("/api/v1/admin/organization-units")
            unit = next(item for item in units.json() if item["code"] == UNIT_CODE)
            disable_receiver = await client.patch(
                f"/api/v1/admin/organization-units/{unit['id']}",
                headers=headers,
                json={"can_receive_budget": False},
            )
            assert disable_receiver.status_code == 200, disable_receiver.text

            deactivate_closed = await client.post(
                f"/api/v1/admin/organization-units/{unit['id']}/deactivate",
                headers=headers,
            )
            assert deactivate_closed.status_code == 204, deactivate_closed.text
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 2D budget foundation hardening verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
