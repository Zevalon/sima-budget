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
from app.modules.budget_plans.models import BudgetPlan, BudgetPlanApproval, BudgetPlanVersion
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

PIC_USERNAME = "phase3b_pic"
APPROVER_USERNAME = "phase3b_approver"
PASSWORD = "Phase3B-Verification!"
FISCAL_CODE = "P3B-2193"
UNIT_CODE = "P3B-UNIT"
CATEGORY_CODE = "P3B-CAT"
UOM_CODE = "P3B-UOM"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        users = (
            await session.scalars(
                select(User).where(User.username.in_([PIC_USERNAME, APPROVER_USERNAME]))
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
        pic_role = (
            await session.scalar(
                select(Role).where(
                    Role.organization_id == organization.id,
                    Role.code == "UNIT_PIC",
                )
            )
            if organization is not None
            else None
        )
        approver_role = (
            await session.scalar(
                select(Role).where(
                    Role.organization_id == organization.id,
                    Role.code == "UNIT_APPROVER",
                )
            )
            if organization is not None
            else None
        )
        if organization is None or root is None or pic_role is None or approver_role is None:
            raise RuntimeError("Bootstrap Phase 3B belum lengkap.")

        pic = User(
            username=PIC_USERNAME,
            email=None,
            full_name="Phase 3B PIC",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        approver = User(
            username=APPROVER_USERNAME,
            email=None,
            full_name="Phase 3B Approver",
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
            name="Phase 3B Verification Unit",
            can_receive_budget=True,
            can_create_budget_plan=True,
            is_active=True,
        )
        category = BudgetCategory(
            organization_id=organization.id,
            code=CATEGORY_CODE,
            name="Phase 3B Category",
            description="Verification category",
            is_active=True,
        )
        uom = UnitOfMeasure(
            organization_id=organization.id,
            code=UOM_CODE,
            name="Phase 3B Unit",
            is_active=True,
        )
        fiscal_year = FiscalYear(
            organization_id=organization.id,
            code=FISCAL_CODE,
            year=2193,
            start_date=date(2193, 1, 1),
            end_date=date(2193, 12, 31),
            status="PLANNING",
        )
        session.add_all([pic, approver, unit, category, uom, fiscal_year])
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
                    role_id=pic_role.id,
                    scope_type="OWN_UNIT",
                    scope_unit_id=unit.id,
                ),
                UserRoleAssignment(
                    user_id=approver.id,
                    role_id=approver_role.id,
                    scope_type="OWN_UNIT",
                    scope_unit_id=unit.id,
                ),
            ]
        )

        budget = AnnualBudget(
            organization_id=organization.id,
            fiscal_year_id=fiscal_year.id,
            amount=Decimal("5000.00"),
            notes="Phase 3B verification budget",
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
            amount=Decimal("5000.00"),
            notes="Phase 3B allocation",
            version=1,
        )
        session.add(allocation)
        await session.commit()
        return str(fiscal_year.id), str(allocation.id), str(category.id), str(uom.id)


async def permission_codes(role_code: str) -> set[str]:
    session_factory = get_session_factory()
    async with session_factory() as session:
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


async def grant_pic_approver_role() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        pic = await session.scalar(select(User).where(User.username == PIC_USERNAME))
        unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == UNIT_CODE)
        )
        role = await session.scalar(select(Role).where(Role.code == "UNIT_APPROVER"))
        if pic is None or unit is None or role is None:
            raise RuntimeError("Data self-approval verification tidak ditemukan.")
        existing = await session.scalar(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == pic.id,
                UserRoleAssignment.role_id == role.id,
            )
        )
        if existing is None:
            session.add(
                UserRoleAssignment(
                    user_id=pic.id,
                    role_id=role.id,
                    scope_type="OWN_UNIT",
                    scope_unit_id=unit.id,
                )
            )
            await session.commit()


async def verify() -> None:
    fiscal_year_id, allocation_id, category_id, uom_id = await setup()
    try:
        pic_permissions = await permission_codes("UNIT_PIC")
        approver_permissions = await permission_codes("UNIT_APPROVER")
        assert {"budget_plans.submit", "budget_plans.revise"} <= pic_permissions
        assert "budget_plans.approve" not in pic_permissions
        assert "budget_plans.approve" in approver_permissions
        assert "budget_plans.submit" not in approver_permissions

        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as pic_client:
            login = await pic_client.post(
                "/api/v1/auth/login",
                json={"username": PIC_USERNAME, "password": PASSWORD},
            )
            assert login.status_code == 200, login.text
            pic_headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            created = await pic_client.post(
                "/api/v1/budget-plans",
                headers=pic_headers,
                json={
                    "unit_allocation_id": allocation_id,
                    "title": "Phase 3B Plan",
                    "description": "Submission and approval verification",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Verification item",
                            "quantity": "2",
                            "unit_price": "500.00",
                        }
                    ],
                },
            )
            assert created.status_code == 201, created.text
            created_data = created.json()
            plan_id = created_data["id"]

            submitted = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/submit",
                headers=pic_headers,
                json={"expected_row_version": created_data["row_version"]},
            )
            assert submitted.status_code == 200, submitted.text
            submitted_data = submitted.json()
            assert submitted_data["status"] == "PENDING_APPROVAL"
            assert submitted_data["submitted_by"] is not None

            await grant_pic_approver_role()
            self_approve = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/approve",
                headers=pic_headers,
                json={
                    "expected_row_version": submitted_data["row_version"],
                    "expected_submission_no": 1,
                    "expected_version_no": 1,
                    "decision_note": "Should be blocked",
                },
            )
            assert self_approve.status_code == 409, self_approve.text

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as approver_client:
            login = await approver_client.post(
                "/api/v1/auth/login",
                json={"username": APPROVER_USERNAME, "password": PASSWORD},
            )
            assert login.status_code == 200, login.text
            approver_headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            pending = await approver_client.get(
                "/api/v1/budget-plan-approvals/pending",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert pending.status_code == 200, pending.text
            assert len(pending.json()) == 1
            pending_item = pending.json()[0]
            assert pending_item["budget_plan"]["id"] == plan_id
            assert pending_item["approval"]["version_no"] == 1

            no_csrf = await approver_client.post(
                f"/api/v1/budget-plans/{plan_id}/reject",
                json={
                    "expected_row_version": pending_item["budget_plan"]["row_version"],
                    "expected_submission_no": pending_item["approval"]["submission_no"],
                    "expected_version_no": pending_item["approval"]["version_no"],
                    "reason": "Needs revision",
                },
            )
            assert no_csrf.status_code == 403, no_csrf.text

            rejected = await approver_client.post(
                f"/api/v1/budget-plans/{plan_id}/reject",
                headers=approver_headers,
                json={
                    "expected_row_version": pending_item["budget_plan"]["row_version"],
                    "expected_submission_no": pending_item["approval"]["submission_no"],
                    "expected_version_no": pending_item["approval"]["version_no"],
                    "reason": "Perbaiki rincian item",
                },
            )
            assert rejected.status_code == 200, rejected.text
            rejected_data = rejected.json()
            assert rejected_data["status"] == "REJECTED"
            assert rejected_data["rejection_reason"] == "Perbaiki rincian item"

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as pic_client:
            login = await pic_client.post(
                "/api/v1/auth/login",
                json={"username": PIC_USERNAME, "password": PASSWORD},
            )
            assert login.status_code == 200, login.text
            pic_headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            revised = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/revise",
                headers=pic_headers,
                json={
                    "expected_row_version": rejected_data["row_version"],
                    "title": "Phase 3B Revised Plan",
                    "description": "Revision 2",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Revised item",
                            "quantity": "3",
                            "unit_price": "400.00",
                        }
                    ],
                },
            )
            assert revised.status_code == 200, revised.text
            revised_data = revised.json()
            assert revised_data["status"] == "DRAFT"
            assert revised_data["current_version_no"] == 2
            assert Decimal(revised_data["total_amount"]) == Decimal("1200.00")
            assert revised_data["rejection_reason"] is None

            resubmitted = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/submit",
                headers=pic_headers,
                json={"expected_row_version": revised_data["row_version"]},
            )
            assert resubmitted.status_code == 200, resubmitted.text
            resubmitted_data = resubmitted.json()
            assert resubmitted_data["status"] == "PENDING_APPROVAL"

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as approver_client:
            login = await approver_client.post(
                "/api/v1/auth/login",
                json={"username": APPROVER_USERNAME, "password": PASSWORD},
            )
            assert login.status_code == 200, login.text
            approver_headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            approved = await approver_client.post(
                f"/api/v1/budget-plans/{plan_id}/approve",
                headers=approver_headers,
                json={
                    "expected_row_version": resubmitted_data["row_version"],
                    "expected_submission_no": 2,
                    "expected_version_no": 2,
                    "decision_note": "Rencana unit disetujui",
                },
            )
            assert approved.status_code == 200, approved.text
            approved_data = approved.json()
            assert approved_data["status"] == "APPROVED"
            assert approved_data["approved_by"] is not None

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as pic_client:
            login = await pic_client.post(
                "/api/v1/auth/login",
                json={"username": PIC_USERNAME, "password": PASSWORD},
            )
            assert login.status_code == 200, login.text
            pic_headers = {"X-CSRF-Token": login.json()["csrf_token"]}

            locked = await pic_client.patch(
                f"/api/v1/budget-plans/{plan_id}",
                headers=pic_headers,
                json={
                    "expected_row_version": approved_data["row_version"],
                    "title": "Should stay locked",
                    "items": [
                        {
                            "budget_category_id": category_id,
                            "unit_of_measure_id": uom_id,
                            "description": "Locked item",
                            "quantity": "1",
                            "unit_price": "100.00",
                        }
                    ],
                },
            )
            assert locked.status_code == 409, locked.text

            history = await pic_client.get(f"/api/v1/budget-plans/{plan_id}/approvals")
            assert history.status_code == 200, history.text
            history_data = history.json()
            assert len(history_data) == 2
            assert history_data[0]["submission_no"] == 2
            assert history_data[0]["version_no"] == 2
            assert history_data[0]["status"] == "APPROVED"
            assert history_data[1]["submission_no"] == 1
            assert history_data[1]["version_no"] == 1
            assert history_data[1]["status"] == "REJECTED"

        session_factory = get_session_factory()
        async with session_factory() as session:
            plan = await session.scalar(select(BudgetPlan).where(BudgetPlan.id == plan_id))
            assert plan is not None
            versions = (
                await session.scalars(
                    select(BudgetPlanVersion)
                    .where(BudgetPlanVersion.budget_plan_id == plan.id)
                    .order_by(BudgetPlanVersion.version_no.asc())
                )
            ).all()
            assert [item.version_no for item in versions] == [1, 2]
            assert (
                await session.scalar(
                    select(AuditLog).where(
                        AuditLog.action == "BUDGET_PLAN_APPROVED",
                        AuditLog.entity_id == plan.id,
                    )
                )
                is not None
            )
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 3B budget plan submission and approval verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
