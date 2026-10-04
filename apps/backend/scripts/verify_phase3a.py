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
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.budget_plans.models import BudgetPlan, BudgetPlanItem, BudgetPlanVersion
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

USERNAME = "phase3a_unit_pic"
PASSWORD = "Phase3A-Verification!"
FISCAL_CODE = "P3A-2194"
UNIT_CODES = ("P3A-UNIT-A", "P3A-UNIT-B")
CATEGORY_CODE = "P3A-CAT"
UOM_CODE = "P3A-UOM"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        fiscal_year = await session.scalar(select(FiscalYear).where(FiscalYear.code == FISCAL_CODE))
        units = (
            await session.scalars(
                select(OrganizationUnit).where(OrganizationUnit.code.in_(UNIT_CODES))
            )
        ).all()
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
                await session.execute(delete(BudgetPlan).where(BudgetPlan.id.in_(plan_ids)))
            allocations = (
                await session.scalars(
                    select(UnitAllocation).where(UnitAllocation.fiscal_year_id == fiscal_year.id)
                )
            ).all()
            allocation_ids = [item.id for item in allocations]
            if allocation_ids:
                await session.execute(
                    delete(UnitAllocation).where(UnitAllocation.id.in_(allocation_ids))
                )
            budget = await session.scalar(
                select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fiscal_year.id)
            )
            if budget is not None:
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
            await session.delete(user)

        for unit in units:
            await session.delete(unit)
        if category is not None:
            await session.delete(category)
        if uom is not None:
            await session.delete(uom)
        if fiscal_year is not None:
            await session.delete(fiscal_year)
        await session.commit()


async def setup() -> tuple[str, str, str, str, str]:
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
            raise RuntimeError("Bootstrap Phase 3A belum lengkap.")

        user = User(
            username=USERNAME,
            email=None,
            full_name="Phase 3A Unit PIC",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        units = [
            OrganizationUnit(
                organization_id=organization.id,
                unit_type_id=root.unit_type_id,
                parent_id=root.id,
                code=code,
                name=f"Phase 3A Verification Unit {index}",
                can_receive_budget=True,
                can_create_budget_plan=True,
                is_active=True,
            )
            for index, code in enumerate(UNIT_CODES, start=1)
        ]
        category = BudgetCategory(
            organization_id=organization.id,
            code=CATEGORY_CODE,
            name="Phase 3A Category",
            description="Verification category",
            is_active=True,
        )
        uom = UnitOfMeasure(
            organization_id=organization.id,
            code=UOM_CODE,
            name="Phase 3A Unit",
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
        session.add_all([user, *units, category, uom, fiscal_year])
        await session.flush()

        session.add(
            UserUnitMembership(
                user_id=user.id,
                organization_unit_id=units[0].id,
                job_title="Verification PIC",
                is_primary=True,
            )
        )
        session.add(
            UserRoleAssignment(
                user_id=user.id,
                role_id=unit_pic_role.id,
                scope_type="OWN_UNIT",
                scope_unit_id=units[0].id,
            )
        )
        budget = AnnualBudget(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            amount=Decimal("2000.00"),
            notes="Phase 3A verification budget",
            status="APPROVED",
            version=1,
        )
        session.add(budget)
        await session.flush()
        allocation_a = UnitAllocation(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            annual_budget_id=budget.id,
            organization_unit_id=units[0].id,
            amount=Decimal("1000.00"),
            notes="Scoped allocation A",
            version=1,
        )
        allocation_b = UnitAllocation(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            annual_budget_id=budget.id,
            organization_unit_id=units[1].id,
            amount=Decimal("1000.00"),
            notes="Out-of-scope allocation B",
            version=1,
        )
        session.add_all([allocation_a, allocation_b])
        await session.commit()
        return (
            str(fiscal_year.id),
            str(allocation_a.id),
            str(allocation_b.id),
            str(category.id),
            str(uom.id),
        )


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
        assert {"budget_plans.view", "budget_plans.create", "budget_plans.update"} <= unit_pic
        assert "budget_plans.view" in budget_admin
        assert "budget_plans.create" not in budget_admin
        assert "budget_plans.view" in system_admin
        assert "budget_plans.update" not in system_admin


async def verify() -> None:
    fiscal_year_id, allocation_a, allocation_b, category_id, uom_id = await setup()
    try:
        await verify_role_permissions()
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

            context = await client.get(
                "/api/v1/budget-plans/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert context.status_code == 200, context.text
            context_data = context.json()
            assert len(context_data["allocations"]) == 1
            assert context_data["allocations"][0]["unit_allocation_id"] == allocation_a

            out_of_scope = await client.post(
                "/api/v1/budget-plans",
                headers=headers,
                json={
                    "unit_allocation_id": allocation_b,
                    "title": "Out of scope",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Unauthorized item",
                            "quantity": "1",
                            "unit_price": "100.00",
                        }
                    ],
                },
            )
            assert out_of_scope.status_code == 403, out_of_scope.text

            created = await client.post(
                "/api/v1/budget-plans",
                headers=headers,
                json={
                    "unit_allocation_id": allocation_a,
                    "title": "Phase 3A Verification Plan",
                    "description": "Versioned draft items",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Item A",
                            "quantity": "2",
                            "unit_price": "200.00",
                        },
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Item B",
                            "quantity": "1",
                            "unit_price": "200.00",
                        },
                    ],
                },
            )
            assert created.status_code == 201, created.text
            created_data = created.json()
            assert Decimal(created_data["total_amount"]) == Decimal("600.00")
            assert created_data["current_version_no"] == 1
            assert created_data["row_version"] == 1
            assert len(created_data["items"]) == 2
            plan_id = created_data["id"]

            over_allocation = await client.patch(
                f"/api/v1/budget-plans/{plan_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "title": "Too large",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Too large item",
                            "quantity": "2",
                            "unit_price": "600.00",
                        }
                    ],
                },
            )
            assert over_allocation.status_code == 409, over_allocation.text

            updated = await client.patch(
                f"/api/v1/budget-plans/{plan_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "title": "Phase 3A Updated Plan",
                    "description": "Updated safely",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Updated item",
                            "quantity": "7",
                            "unit_price": "100.00",
                        }
                    ],
                },
            )
            assert updated.status_code == 200, updated.text
            assert Decimal(updated.json()["total_amount"]) == Decimal("700.00")
            assert updated.json()["row_version"] == 2
            assert updated.json()["current_version_no"] == 1

            stale = await client.patch(
                f"/api/v1/budget-plans/{plan_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "title": "Stale update",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Stale item",
                            "quantity": "1",
                            "unit_price": "10.00",
                        }
                    ],
                },
            )
            assert stale.status_code == 409, stale.text

            listed = await client.get(
                "/api/v1/budget-plans",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert listed.status_code == 200, listed.text
            assert len(listed.json()) == 1

        session_factory = get_session_factory()
        async with session_factory() as session:
            plan = await session.scalar(select(BudgetPlan).where(BudgetPlan.id == plan_id))
            assert plan is not None
            version = await session.scalar(
                select(BudgetPlanVersion).where(
                    BudgetPlanVersion.budget_plan_id == plan.id,
                    BudgetPlanVersion.version_no == 1,
                )
            )
            assert version is not None
            assert version.total_amount == Decimal("700.00")
            items = (
                await session.scalars(
                    select(BudgetPlanItem).where(BudgetPlanItem.plan_version_id == version.id)
                )
            ).all()
            assert len(items) == 1
            assert items[0].amount == Decimal("700.00")
            assert (
                await session.scalar(
                    select(AuditLog).where(
                        AuditLog.action == "BUDGET_PLAN_UPDATED",
                        AuditLog.entity_id == plan.id,
                    )
                )
                is not None
            )
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 3A budget plan core verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
