import asyncio
from datetime import date
from decimal import Decimal
from uuid import UUID

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.annual_budgets.models import AnnualBudget
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.budget_plans.models import BudgetPlan, BudgetPlanApproval
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

PIC_USERNAME = "phase3c_pic"
APPROVER_USERNAME = "phase3c_approver"
BUDGET_ADMIN_USERNAME = "phase3c_budget_admin"
PASSWORD = "Phase3C-Verification!"
FISCAL_CODE = "P3C-2194"
UNIT_CODE = "P3C-UNIT"
CATEGORY_CODE = "P3C-CAT"
UOM_CODE = "P3C-UOM"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        users = (
            await session.scalars(
                select(User).where(
                    User.username.in_([PIC_USERNAME, APPROVER_USERNAME, BUDGET_ADMIN_USERNAME])
                )
            )
        ).all()
        fiscal_year = await session.scalar(select(FiscalYear).where(FiscalYear.code == FISCAL_CODE))
        unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == UNIT_CODE)
        )
        category = await session.scalar(
            select(BudgetCategory).where(BudgetCategory.code == CATEGORY_CODE)
        )
        uom = await session.scalar(select(UnitOfMeasure).where(UnitOfMeasure.code == UOM_CODE))

        if fiscal_year is not None:
            plans = (
                await session.scalars(
                    select(BudgetPlan).where(BudgetPlan.fiscal_year_id == fiscal_year.id)
                )
            ).all()
            plan_ids = [item.id for item in plans]
            if plan_ids:
                await session.execute(delete(AuditLog).where(AuditLog.entity_id.in_(plan_ids)))
                await session.execute(
                    delete(BudgetPlanApproval).where(
                        BudgetPlanApproval.budget_plan_id.in_(plan_ids)
                    )
                )
                await session.execute(delete(BudgetPlan).where(BudgetPlan.id.in_(plan_ids)))
            await session.execute(
                delete(UnitAllocation).where(UnitAllocation.fiscal_year_id == fiscal_year.id)
            )
            budget = await session.scalar(
                select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fiscal_year.id)
            )
            if budget is not None:
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
            await session.delete(user)

        if unit is not None:
            await session.delete(unit)
        if category is not None:
            await session.delete(category)
        if uom is not None:
            await session.delete(uom)
        if fiscal_year is not None:
            await session.delete(fiscal_year)
        await session.commit()


async def setup() -> tuple[str, str, str, str]:
    await cleanup()
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        root = await session.scalar(select(OrganizationUnit).where(OrganizationUnit.code == "ROOT"))
        if organization is None or root is None:
            raise RuntimeError("Bootstrap organisasi Phase 3C belum lengkap.")

        roles = {
            code: await session.scalar(
                select(Role).where(Role.organization_id == organization.id, Role.code == code)
            )
            for code in ("UNIT_PIC", "UNIT_APPROVER", "BUDGET_ADMIN")
        }
        if any(role is None for role in roles.values()):
            raise RuntimeError("Role Phase 3C belum lengkap.")

        pic = User(
            username=PIC_USERNAME,
            full_name="Phase 3C PIC",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        approver = User(
            username=APPROVER_USERNAME,
            full_name="Phase 3C Approver",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        budget_admin = User(
            username=BUDGET_ADMIN_USERNAME,
            full_name="Phase 3C Budget Admin",
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
            name="Phase 3C Verification Unit",
            can_receive_budget=True,
            can_create_budget_plan=True,
            is_active=True,
        )
        category = BudgetCategory(
            organization_id=organization.id,
            code=CATEGORY_CODE,
            name="Phase 3C Category",
            is_active=True,
        )
        uom = UnitOfMeasure(
            organization_id=organization.id,
            code=UOM_CODE,
            name="Phase 3C Unit",
            is_active=True,
        )
        fiscal_year = FiscalYear(
            organization_id=organization.id,
            code=FISCAL_CODE,
            year=2194,
            start_date=date(2194, 1, 1),
            end_date=date(2194, 12, 31),
            status="PLANNING",
        )
        session.add_all([pic, approver, budget_admin, unit, category, uom, fiscal_year])
        await session.flush()

        session.add_all(
            [
                UserUnitMembership(
                    user_id=pic.id,
                    organization_unit_id=unit.id,
                    job_title="Verification PIC",
                    is_primary=True,
                ),
                UserUnitMembership(
                    user_id=approver.id,
                    organization_unit_id=unit.id,
                    job_title="Verification Approver",
                    is_primary=True,
                ),
                UserRoleAssignment(
                    user_id=pic.id,
                    role_id=roles["UNIT_PIC"].id,
                    scope_type="OWN_UNIT",
                    scope_unit_id=unit.id,
                ),
                UserRoleAssignment(
                    user_id=approver.id,
                    role_id=roles["UNIT_APPROVER"].id,
                    scope_type="OWN_UNIT",
                    scope_unit_id=unit.id,
                ),
                UserRoleAssignment(
                    user_id=budget_admin.id,
                    role_id=roles["BUDGET_ADMIN"].id,
                    scope_type="ALL",
                    scope_unit_id=None,
                ),
            ]
        )

        budget = AnnualBudget(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            amount=Decimal("1000.00"),
            notes="Phase 3C verification budget",
            status="APPROVED",
            version=1,
        )
        session.add(budget)
        await session.flush()
        allocation = UnitAllocation(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            annual_budget_id=budget.id,
            organization_unit_id=unit.id,
            amount=Decimal("1000.00"),
            notes="Phase 3C allocation",
            version=1,
        )
        session.add(allocation)
        await session.commit()
        return str(fiscal_year.id), str(allocation.id), str(category.id), str(uom.id)


async def login(client: AsyncClient, username: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"X-CSRF-Token": response.json()["csrf_token"]}


async def create_submitted_plan(
    client: AsyncClient,
    *,
    headers: dict[str, str],
    allocation_id: str,
    category_id: str,
    uom_id: str,
    title: str,
) -> tuple[str, int]:
    created = await client.post(
        "/api/v1/budget-plans",
        headers=headers,
        json={
            "unit_allocation_id": allocation_id,
            "title": title,
            "items": [
                {
                    "budget_category_id": category_id,
                    "unit_of_measure_id": uom_id,
                    "description": title,
                    "quantity": "1",
                    "unit_price": "600.00",
                }
            ],
        },
    )
    assert created.status_code == 201, created.text
    created_data = created.json()
    plan_id = created_data["id"]
    submitted = await client.post(
        f"/api/v1/budget-plans/{plan_id}/submit",
        headers=headers,
        json={"expected_row_version": created_data["row_version"]},
    )
    assert submitted.status_code == 200, submitted.text
    submitted_data = submitted.json()
    return plan_id, int(submitted_data["row_version"])


async def verify() -> None:
    fiscal_year_id, allocation_id, category_id, uom_id = await setup()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as pic_client:
            pic_headers = await login(pic_client, PIC_USERNAME)
            first_plan_id, first_row_version = await create_submitted_plan(
                pic_client,
                headers=pic_headers,
                allocation_id=allocation_id,
                category_id=category_id,
                uom_id=uom_id,
                title="Concurrent plan A",
            )
            second_plan_id, second_row_version = await create_submitted_plan(
                pic_client,
                headers=pic_headers,
                allocation_id=allocation_id,
                category_id=category_id,
                uom_id=uom_id,
                title="Concurrent plan B",
            )

        async with (
            AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://localhost",
                follow_redirects=True,
            ) as approver_a,
            AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://localhost",
                follow_redirects=True,
            ) as approver_b,
        ):
            headers_a = await login(approver_a, APPROVER_USERNAME)
            headers_b = await login(approver_b, APPROVER_USERNAME)
            first_result, second_result = await asyncio.gather(
                approver_a.post(
                    f"/api/v1/budget-plans/{first_plan_id}/approve",
                    headers=headers_a,
                    json={
                        "expected_row_version": first_row_version,
                        "expected_submission_no": 1,
                        "expected_version_no": 1,
                        "decision_note": "Concurrent approval A",
                    },
                ),
                approver_b.post(
                    f"/api/v1/budget-plans/{second_plan_id}/approve",
                    headers=headers_b,
                    json={
                        "expected_row_version": second_row_version,
                        "expected_submission_no": 1,
                        "expected_version_no": 1,
                        "decision_note": "Concurrent approval B",
                    },
                ),
            )
            assert sorted([first_result.status_code, second_result.status_code]) == [200, 409]

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://localhost",
            follow_redirects=True,
        ) as admin_client:
            admin_headers = await login(admin_client, BUDGET_ADMIN_USERNAME)
            overview = await admin_client.get(
                "/api/v1/unit-allocations/overview",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert overview.status_code == 200, overview.text
            overview_data = overview.json()
            assert Decimal(overview_data["committed_amount"]) == Decimal("600.00")
            assert Decimal(overview_data["draft_pipeline_amount"]) == Decimal("600.00")
            assert Decimal(overview_data["available_amount"]) == Decimal("400.00")
            allocation_data = overview_data["allocations"][0]
            assert Decimal(allocation_data["committed_amount"]) == Decimal("600.00")
            assert Decimal(allocation_data["available_amount"]) == Decimal("400.00")

            too_low = await admin_client.patch(
                f"/api/v1/unit-allocations/{allocation_id}",
                headers=admin_headers,
                json={"expected_version": 1, "amount": "500.00"},
            )
            assert too_low.status_code == 409, too_low.text

            reduced = await admin_client.patch(
                f"/api/v1/unit-allocations/{allocation_id}",
                headers=admin_headers,
                json={"expected_version": 1, "amount": "800.00"},
            )
            assert reduced.status_code == 200, reduced.text
            assert Decimal(reduced.json()["committed_amount"]) == Decimal("600.00")
            assert Decimal(reduced.json()["available_amount"]) == Decimal("200.00")

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://localhost",
            follow_redirects=True,
        ) as pic_client:
            await login(pic_client, PIC_USERNAME)
            context = await pic_client.get(
                "/api/v1/budget-plans/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert context.status_code == 200, context.text
            option = context.json()["allocations"][0]
            assert Decimal(option["committed_amount"]) == Decimal("600.00")
            assert Decimal(option["draft_pipeline_amount"]) == Decimal("600.00")
            assert Decimal(option["available_amount"]) == Decimal("200.00")

        session_factory = get_session_factory()
        async with session_factory() as session:
            plans = (
                await session.scalars(
                    select(BudgetPlan).where(
                        BudgetPlan.fiscal_year_id == UUID(fiscal_year_id),
                    )
                )
            ).all()
            assert sum(1 for plan in plans if plan.status == "APPROVED") == 1
            assert sum(1 for plan in plans if plan.status == "PENDING_APPROVAL") == 1
            approved_plan = next(plan for plan in plans if plan.status == "APPROVED")
            audit = await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "BUDGET_PLAN_APPROVED",
                    AuditLog.entity_id == approved_plan.id,
                )
            )
            assert audit is not None
            assert audit.after_data["committed_after"] == "600.00"
            assert audit.after_data["available_after"] == "400.00"
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 3C commitment and available-budget verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
