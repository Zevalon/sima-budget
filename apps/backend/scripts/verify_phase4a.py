import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, func, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.annual_budgets.models import AnnualBudget
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import FiscalYear
from app.modules.budget_plans.models import BudgetPlan, BudgetPlanApproval, BudgetPlanVersion
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.realizations.models import Realization
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

USERNAME = "phase4a_unit_pic"
PASSWORD = "Phase4A-Verification!"
UNIT_CODE = "P4A-UNIT"
PLAN_NUMBER = "P4A-PLAN-001"
TEMP_FISCAL_CODE = "P4A-2197"
TEMP_BUDGET_NOTE = "Phase 4A verification annual budget"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == UNIT_CODE)
        )
        plan = await session.scalar(select(BudgetPlan).where(BudgetPlan.plan_number == PLAN_NUMBER))
        temp_fiscal = await session.scalar(
            select(FiscalYear).where(FiscalYear.code == TEMP_FISCAL_CODE)
        )
        temp_budget = await session.scalar(
            select(AnnualBudget).where(AnnualBudget.notes == TEMP_BUDGET_NOTE)
        )

        if plan is not None:
            realization_ids = (
                await session.scalars(
                    select(Realization.id).where(Realization.budget_plan_id == plan.id)
                )
            ).all()
            if realization_ids:
                await session.execute(
                    delete(AuditLog).where(AuditLog.entity_id.in_(realization_ids))
                )
            await session.execute(delete(Realization).where(Realization.budget_plan_id == plan.id))
            await session.execute(
                delete(BudgetPlanApproval).where(BudgetPlanApproval.budget_plan_id == plan.id)
            )
            await session.execute(delete(AuditLog).where(AuditLog.entity_id == plan.id))
            await session.delete(plan)
            await session.flush()

        if unit is not None:
            await session.execute(
                delete(UnitAllocation).where(UnitAllocation.organization_unit_id == unit.id)
            )

        if user is not None:
            await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user.id))
            await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)
            )
            await session.execute(
                delete(UserUnitMembership).where(UserUnitMembership.user_id == user.id)
            )
            await session.delete(user)

        if unit is not None:
            await session.delete(unit)
        if temp_budget is not None:
            await session.delete(temp_budget)
        if temp_fiscal is not None:
            await session.delete(temp_fiscal)
        await session.commit()


async def setup() -> str:
    await cleanup()
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        root = await session.scalar(select(OrganizationUnit).where(OrganizationUnit.code == "ROOT"))
        unit_pic_role = (
            await session.scalar(
                select(Role).where(
                    Role.organization_id == organization.id,
                    Role.code == "UNIT_PIC",
                )
            )
            if organization is not None
            else None
        )
        if organization is None or root is None or unit_pic_role is None:
            raise RuntimeError("Bootstrap Phase 4A belum lengkap.")

        fiscal_year = await session.scalar(
            select(FiscalYear).where(
                FiscalYear.organization_id == organization.id,
                FiscalYear.status == "ACTIVE",
            )
        )
        if fiscal_year is None:
            fiscal_year = FiscalYear(
                organization_id=organization.id,
                code=TEMP_FISCAL_CODE,
                year=2197,
                start_date=date(2197, 1, 1),
                end_date=date(2197, 12, 31),
                status="ACTIVE",
            )
            session.add(fiscal_year)
            await session.flush()

        annual_budget = await session.scalar(
            select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fiscal_year.id)
        )
        if annual_budget is None:
            annual_budget = AnnualBudget(
                organization_id=organization.id,
                fiscal_year_id=fiscal_year.id,
                amount=Decimal("10000.00"),
                notes=TEMP_BUDGET_NOTE,
                status="APPROVED",
                version=1,
            )
            session.add(annual_budget)
            await session.flush()

        user = User(
            username=USERNAME,
            email=None,
            full_name="Phase 4A Unit PIC",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        unit = OrganizationUnit(
            organization_id=organization.id,
            unit_type_id=root.unit_type_id,
            parent_id=root.id,
            code=UNIT_CODE,
            name="Phase 4A Verification Unit",
            can_receive_budget=True,
            can_create_budget_plan=True,
            is_active=True,
        )
        session.add_all([user, unit])
        await session.flush()
        session.add(
            UserUnitMembership(
                user_id=user.id,
                organization_unit_id=unit.id,
                job_title="Verification PIC",
                is_primary=True,
            )
        )
        session.add(
            UserRoleAssignment(
                user_id=user.id,
                role_id=unit_pic_role.id,
                scope_type="OWN_UNIT",
                scope_unit_id=unit.id,
            )
        )

        allocation = UnitAllocation(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            annual_budget_id=annual_budget.id,
            organization_unit_id=unit.id,
            amount=Decimal("1000.00"),
            notes="Phase 4A verification allocation",
            version=1,
        )
        session.add(allocation)
        await session.flush()

        now = datetime.now(UTC)
        plan = BudgetPlan(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            unit_allocation_id=allocation.id,
            organization_unit_id=unit.id,
            plan_number=PLAN_NUMBER,
            status="APPROVED",
            current_version_no=1,
            row_version=3,
            created_by=user.id,
            submitted_by=user.id,
            submitted_at=now,
            approved_by=user.id,
            approved_at=now,
        )
        session.add(plan)
        await session.flush()
        version = BudgetPlanVersion(
            organization_id=organization.id,
            budget_plan_id=plan.id,
            version_no=1,
            title="Phase 4A Approved Plan",
            description="Approved plan used to verify realization controls.",
            total_amount=Decimal("1000.00"),
            created_by=user.id,
        )
        session.add(version)
        await session.flush()
        session.add(
            BudgetPlanApproval(
                organization_id=organization.id,
                budget_plan_id=plan.id,
                plan_version_id=version.id,
                submission_no=1,
                status="APPROVED",
                requested_by=user.id,
                requested_at=now,
                decided_by=user.id,
                decided_at=now,
                decision_note="Verification fixture",
            )
        )
        await session.commit()
        return str(fiscal_year.id)


async def verify_role_permissions() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:

        async def permission_codes(role_code: str) -> set[str]:
            return set(
                (
                    await session.scalars(
                        select(Permission.code)
                        .join(RolePermission, RolePermission.permission_id == Permission.id)
                        .join(Role, Role.id == RolePermission.role_id)
                        .where(Role.code == role_code)
                    )
                ).all()
            )

        unit_pic = await permission_codes("UNIT_PIC")
        budget_admin = await permission_codes("BUDGET_ADMIN")
        system_admin = await permission_codes("SYSTEM_ADMIN")
        expected = {
            "realizations.view",
            "realizations.create",
            "realizations.update",
            "realizations.post",
        }
        assert expected <= unit_pic
        assert "realizations.view" in budget_admin
        assert "realizations.create" not in budget_admin
        assert "realizations.view" in system_admin
        assert "realizations.post" not in system_admin


async def login_client() -> tuple[AsyncClient, dict[str, str]]:
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
        follow_redirects=True,
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
    )
    assert login.status_code == 200, login.text
    return client, {"X-CSRF-Token": login.json()["csrf_token"]}


async def concurrent_post(realization_id: str) -> int:
    client, headers = await login_client()
    try:
        detail = await client.get(f"/api/v1/realizations/{realization_id}")
        assert detail.status_code == 200, detail.text
        data = detail.json()
        response = await client.post(
            f"/api/v1/realizations/{realization_id}/post",
            headers=headers,
            json={
                "expected_row_version": data["row_version"],
                "expected_status": data["status"],
                "expected_plan_version_id": data["plan_version_id"],
            },
        )
        return response.status_code
    finally:
        await client.aclose()


async def verify() -> None:
    fiscal_year_id = await setup()
    try:
        await verify_role_permissions()
        client, headers = await login_client()
        try:
            context = await client.get(
                "/api/v1/realizations/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert context.status_code == 200, context.text
            context_data = context.json()
            assert context_data["fiscal_year_status"] == "ACTIVE"
            assert len(context_data["plans"]) == 1
            plan_id = context_data["plans"][0]["budget_plan_id"]
            session_factory = get_session_factory()
            async with session_factory() as session:
                fiscal = await session.scalar(
                    select(FiscalYear).where(FiscalYear.id == UUID(fiscal_year_id))
                )
                assert fiscal is not None
                valid_date = fiscal.start_date.isoformat()

            missing_csrf = await client.post(
                "/api/v1/realizations",
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P4A-DOC-001",
                    "description": "Missing CSRF",
                    "amount": "400.00",
                },
            )
            assert missing_csrf.status_code == 403, missing_csrf.text

            created = await client.post(
                "/api/v1/realizations",
                headers=headers,
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P4A-DOC-001",
                    "description": "First realization draft",
                    "vendor_name": "Vendor Verification",
                    "amount": "400.00",
                },
            )
            assert created.status_code == 201, created.text
            created_data = created.json()
            assert created_data["status"] == "DRAFT"
            assert created_data["row_version"] == 1
            realization_id = created_data["id"]
            plan_version_id = created_data["plan_version_id"]

            updated = await client.patch(
                f"/api/v1/realizations/{realization_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                    "realization_date": valid_date,
                    "reference_number": "P4A-DOC-001-R1",
                    "description": "Updated realization draft",
                    "vendor_name": "Vendor Verification",
                    "amount": "450.00",
                },
            )
            assert updated.status_code == 200, updated.text
            assert updated.json()["row_version"] == 2

            stale = await client.patch(
                f"/api/v1/realizations/{realization_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                    "realization_date": valid_date,
                    "reference_number": "P4A-STALE",
                    "description": "Stale",
                    "amount": "100.00",
                },
            )
            assert stale.status_code == 409, stale.text

            posted = await client.post(
                f"/api/v1/realizations/{realization_id}/post",
                headers=headers,
                json={
                    "expected_row_version": 2,
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                },
            )
            assert posted.status_code == 200, posted.text
            posted_data = posted.json()
            assert posted_data["status"] == "POSTED"
            assert Decimal(posted_data["plan_realized_amount"]) == Decimal("450.00")
            assert Decimal(posted_data["plan_remaining_amount"]) == Decimal("550.00")

            immutable = await client.patch(
                f"/api/v1/realizations/{realization_id}",
                headers=headers,
                json={
                    "expected_row_version": posted_data["row_version"],
                    "expected_status": "POSTED",
                    "expected_plan_version_id": plan_version_id,
                    "realization_date": valid_date,
                    "reference_number": "P4A-IMMUTABLE",
                    "description": "Must fail",
                    "amount": "10.00",
                },
            )
            assert immutable.status_code == 409, immutable.text

            draft_ids: list[str] = []
            for index in (2, 3):
                draft = await client.post(
                    "/api/v1/realizations",
                    headers=headers,
                    json={
                        "budget_plan_id": plan_id,
                        "realization_date": valid_date,
                        "reference_number": f"P4A-DOC-00{index}",
                        "description": f"Concurrent draft {index}",
                        "amount": "400.00",
                    },
                )
                assert draft.status_code == 201, draft.text
                draft_ids.append(draft.json()["id"])

        finally:
            await client.aclose()

        results = await asyncio.gather(*(concurrent_post(item_id) for item_id in draft_ids))
        assert sorted(results) == [200, 409], results

        client, _ = await login_client()
        try:
            final_context = await client.get(
                "/api/v1/realizations/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert final_context.status_code == 200, final_context.text
            plan_data = final_context.json()["plans"][0]
            assert Decimal(plan_data["realized_amount"]) == Decimal("850.00")
            assert Decimal(plan_data["remaining_amount"]) == Decimal("150.00")

        finally:
            await client.aclose()

        session_factory = get_session_factory()
        async with session_factory() as session:
            posted_count = await session.scalar(
                select(func.count(Realization.id)).where(
                    Realization.budget_plan_id == UUID(plan_id),
                    Realization.status == "POSTED",
                )
            )
            assert int(posted_count or 0) == 2
            assert (
                await session.scalar(
                    select(AuditLog).where(
                        AuditLog.action == "REALIZATION_POSTED",
                        AuditLog.entity_type == "realization",
                    )
                )
                is not None
            )
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 4A realization core verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
