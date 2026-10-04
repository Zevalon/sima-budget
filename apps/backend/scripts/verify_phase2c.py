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
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

BUDGET_USERNAME = "phase2c_budget_admin"
APPROVER_USERNAME = "phase2c_management_approver"
PASSWORD = "Phase2C-Verification!"
FISCAL_CODE = "P2C-2195"
UNIT_CODES = ("P2C-UNIT-A", "P2C-UNIT-B")


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        users = (
            await session.scalars(
                select(User).where(User.username.in_([BUDGET_USERNAME, APPROVER_USERNAME]))
            )
        ).all()
        fiscal_year = await session.scalar(select(FiscalYear).where(FiscalYear.code == FISCAL_CODE))
        units = (
            await session.scalars(
                select(OrganizationUnit).where(OrganizationUnit.code.in_(UNIT_CODES))
            )
        ).all()

        entity_ids = [unit.id for unit in units]
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
                await session.execute(
                    delete(AnnualBudgetApproval).where(
                        AnnualBudgetApproval.annual_budget_id == budget.id
                    )
                )
                await session.delete(budget)

        for user in users:
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

        for unit in units:
            await session.delete(unit)
        if fiscal_year is not None:
            await session.delete(fiscal_year)
        for user in users:
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
        budget_role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "BUDGET_ADMIN",
            )
        )
        approver_role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "MANAGEMENT_APPROVER",
            )
        )
        if root_unit is None or budget_role is None or approver_role is None:
            raise RuntimeError("Bootstrap Phase 2C belum lengkap.")

        units = [
            OrganizationUnit(
                organization_id=organization.id,
                unit_type_id=root_unit.unit_type_id,
                parent_id=root_unit.id,
                code=code,
                name=f"Verification Unit {index}",
                can_receive_budget=True,
                can_create_budget_plan=True,
                is_active=True,
            )
            for index, code in enumerate(UNIT_CODES, start=1)
        ]
        budget_user = User(
            username=BUDGET_USERNAME,
            email=None,
            full_name="Phase 2C Budget Admin",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        approver_user = User(
            username=APPROVER_USERNAME,
            email=None,
            full_name="Phase 2C Management Approver",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        session.add_all([*units, budget_user, approver_user])
        await session.flush()

        for user in (budget_user, approver_user):
            session.add(
                UserUnitMembership(
                    user_id=user.id,
                    organization_unit_id=root_unit.id,
                    job_title="Verification",
                    is_primary=True,
                )
            )

        session.add_all(
            [
                UserRoleAssignment(
                    user_id=budget_user.id,
                    role_id=budget_role.id,
                    scope_type="ALL",
                    scope_unit_id=None,
                ),
                UserRoleAssignment(
                    user_id=approver_user.id,
                    role_id=approver_role.id,
                    scope_type="ALL",
                    scope_unit_id=None,
                ),
            ]
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
        management_approver = await permission_codes("MANAGEMENT_APPROVER")
        unit_pic = await permission_codes("UNIT_PIC")

        assert "unit_allocations.view" in system_admin
        assert "unit_allocations.create" not in system_admin
        assert "unit_allocations.create" in budget_admin
        assert "unit_allocations.update" in budget_admin
        assert "unit_allocations.view" in management_approver
        assert "unit_allocations.create" not in management_approver
        assert "unit_allocations.view" not in unit_pic


async def login(client: AsyncClient, username: str) -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def verify() -> None:
    await setup()
    try:
        await verify_role_separation()
        transport = ASGITransport(app=app)

        async with (
            AsyncClient(
                transport=transport,
                base_url="http://localhost",
                follow_redirects=True,
            ) as budget_client,
            AsyncClient(
                transport=transport,
                base_url="http://localhost",
                follow_redirects=True,
            ) as concurrent_client,
            AsyncClient(
                transport=transport,
                base_url="http://localhost",
                follow_redirects=True,
            ) as approver_client,
        ):
            budget_login = await login(budget_client, BUDGET_USERNAME)
            concurrent_login = await login(concurrent_client, BUDGET_USERNAME)
            approver_login = await login(approver_client, APPROVER_USERNAME)
            budget_headers = {"X-CSRF-Token": budget_login["csrf_token"]}
            concurrent_headers = {"X-CSRF-Token": concurrent_login["csrf_token"]}
            approver_headers = {"X-CSRF-Token": approver_login["csrf_token"]}

            fiscal_year = await budget_client.post(
                "/api/v1/fiscal-years",
                headers=budget_headers,
                json={
                    "code": FISCAL_CODE,
                    "year": 2195,
                    "start_date": "2195-01-01",
                    "end_date": "2195-12-31",
                },
            )
            assert fiscal_year.status_code == 201, fiscal_year.text
            fiscal_year_id = fiscal_year.json()["id"]

            planning = await budget_client.post(
                f"/api/v1/fiscal-years/{fiscal_year_id}/transition",
                headers=budget_headers,
                json={"target_status": "PLANNING"},
            )
            assert planning.status_code == 200, planning.text

            budget = await budget_client.post(
                "/api/v1/annual-budgets",
                headers=budget_headers,
                json={
                    "fiscal_year_id": fiscal_year_id,
                    "amount": "1000.00",
                    "notes": "Phase 2C allocation verification",
                },
            )
            assert budget.status_code == 201, budget.text
            annual_budget_id = budget.json()["id"]

            submitted = await budget_client.post(
                f"/api/v1/annual-budgets/{annual_budget_id}/submit",
                headers=budget_headers,
            )
            assert submitted.status_code == 200, submitted.text
            approved = await approver_client.post(
                f"/api/v1/annual-budgets/{annual_budget_id}/approve",
                headers=approver_headers,
                json={"decision_note": "Approved for allocation verification"},
            )
            assert approved.status_code == 200, approved.text

            session_factory = get_session_factory()
            async with session_factory() as session:
                units = (
                    await session.scalars(
                        select(OrganizationUnit)
                        .where(OrganizationUnit.code.in_(UNIT_CODES))
                        .order_by(OrganizationUnit.code.asc())
                    )
                ).all()
                root_unit = await session.scalar(
                    select(OrganizationUnit).where(OrganizationUnit.code == "ROOT")
                )
            assert len(units) == 2
            assert root_unit is not None
            unit_a, unit_b = units

            no_csrf = await budget_client.post(
                "/api/v1/unit-allocations",
                json={
                    "fiscal_year_id": fiscal_year_id,
                    "organization_unit_id": str(unit_a.id),
                    "amount": "10.00",
                },
            )
            assert no_csrf.status_code == 403, no_csrf.text

            invalid_unit = await budget_client.post(
                "/api/v1/unit-allocations",
                headers=budget_headers,
                json={
                    "fiscal_year_id": fiscal_year_id,
                    "organization_unit_id": str(root_unit.id),
                    "amount": "10.00",
                },
            )
            assert invalid_unit.status_code == 409, invalid_unit.text

            first, second = await asyncio.gather(
                budget_client.post(
                    "/api/v1/unit-allocations",
                    headers=budget_headers,
                    json={
                        "fiscal_year_id": fiscal_year_id,
                        "organization_unit_id": str(unit_a.id),
                        "amount": "600.00",
                    },
                ),
                concurrent_client.post(
                    "/api/v1/unit-allocations",
                    headers=concurrent_headers,
                    json={
                        "fiscal_year_id": fiscal_year_id,
                        "organization_unit_id": str(unit_b.id),
                        "amount": "600.00",
                    },
                ),
            )
            assert sorted([first.status_code, second.status_code]) == [201, 409]

            successful = first if first.status_code == 201 else second
            failed_unit = unit_b if first.status_code == 201 else unit_a
            successful_allocation_id = successful.json()["id"]

            remaining_allocation = await budget_client.post(
                "/api/v1/unit-allocations",
                headers=budget_headers,
                json={
                    "fiscal_year_id": fiscal_year_id,
                    "organization_unit_id": str(failed_unit.id),
                    "amount": "400.00",
                    "notes": "Fill remaining approved budget",
                },
            )
            assert remaining_allocation.status_code == 201, remaining_allocation.text

            overview = await budget_client.get(
                "/api/v1/unit-allocations/overview",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert overview.status_code == 200, overview.text
            overview_data = overview.json()
            assert Decimal(overview_data["annual_budget_amount"]) == Decimal("1000.00")
            assert Decimal(overview_data["allocated_amount"]) == Decimal("1000.00")
            assert Decimal(overview_data["remaining_amount"]) == Decimal("0.00")
            assert len(overview_data["allocations"]) == 2

            over_update = await budget_client.patch(
                f"/api/v1/unit-allocations/{successful_allocation_id}",
                headers=budget_headers,
                json={"amount": "700.00"},
            )
            assert over_update.status_code == 409, over_update.text

            updated = await budget_client.patch(
                f"/api/v1/unit-allocations/{successful_allocation_id}",
                headers=budget_headers,
                json={"amount": "500.25", "notes": "Controlled adjustment"},
            )
            assert updated.status_code == 200, updated.text
            assert Decimal(updated.json()["amount"]) == Decimal("500.25")
            assert updated.json()["version"] == 2

            overview_after_update = await budget_client.get(
                "/api/v1/unit-allocations/overview",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert overview_after_update.status_code == 200, overview_after_update.text
            data = overview_after_update.json()
            assert Decimal(data["allocated_amount"]) == Decimal("900.25")
            assert Decimal(data["remaining_amount"]) == Decimal("99.75")

        session_factory = get_session_factory()
        async with session_factory() as session:
            created_audit = await session.scalar(
                select(AuditLog).where(AuditLog.action == "UNIT_ALLOCATION_CREATED")
            )
            updated_audit = await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "UNIT_ALLOCATION_UPDATED",
                    AuditLog.entity_id == successful_allocation_id,
                )
            )
            assert created_audit is not None
            assert updated_audit is not None
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 2C unit allocation verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
