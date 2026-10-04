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

PIC_USERNAME = "phase3d_pic"
APPROVER_USERNAME = "phase3d_approver"
PASSWORD = "Phase3D-Verification!"
FISCAL_CODE = "P3D-2195"
UNIT_CODE = "P3D-UNIT"
CATEGORY_CODE = "P3D-CAT"
UOM_CODE = "P3D-UOM"


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
        if organization is None or root is None:
            raise RuntimeError("Bootstrap organisasi Phase 3D belum lengkap.")

        pic_role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "UNIT_PIC",
            )
        )
        approver_role = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "UNIT_APPROVER",
            )
        )
        if pic_role is None or approver_role is None:
            raise RuntimeError("Role Phase 3D belum lengkap.")

        pic = User(
            username=PIC_USERNAME,
            full_name="Phase 3D PIC",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        approver = User(
            username=APPROVER_USERNAME,
            full_name="Phase 3D Approver",
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
            name="Phase 3D Verification Unit",
            can_receive_budget=True,
            can_create_budget_plan=True,
            is_active=True,
        )
        category = BudgetCategory(
            organization_id=organization.id,
            code=CATEGORY_CODE,
            name="Phase 3D Category",
            is_active=True,
        )
        uom = UnitOfMeasure(
            organization_id=organization.id,
            code=UOM_CODE,
            name="Phase 3D Unit",
            is_active=True,
        )
        fiscal_year = FiscalYear(
            organization_id=organization.id,
            code=FISCAL_CODE,
            year=2195,
            start_date=date(2195, 1, 1),
            end_date=date(2195, 12, 31),
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
            notes="Phase 3D verification budget",
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
            notes="Phase 3D allocation",
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


def item_payload(
    category_id: str,
    uom_id: str,
    *,
    quantity: str,
    unit_price: str,
) -> dict[str, str]:
    return {
        "budget_category_id": category_id,
        "unit_of_measure_id": uom_id,
        "description": "Phase 3D guarded item",
        "quantity": quantity,
        "unit_price": unit_price,
    }


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
            created = await pic_client.post(
                "/api/v1/budget-plans",
                headers=pic_headers,
                json={
                    "unit_allocation_id": allocation_id,
                    "title": "Phase 3D Guarded Plan",
                    "description": "Workflow identity and stale-action verification",
                    "items": [
                        item_payload(
                            category_id,
                            uom_id,
                            quantity="2",
                            unit_price="500.00",
                        )
                    ],
                },
            )
            assert created.status_code == 201, created.text
            created_data = created.json()
            plan_id = created_data["id"]
            assert created_data["row_version"] == 1

            updated = await pic_client.patch(
                f"/api/v1/budget-plans/{plan_id}",
                headers=pic_headers,
                json={
                    "expected_row_version": created_data["row_version"],
                    "title": "Phase 3D Updated Plan",
                    "description": "Updated before submission",
                    "items": [
                        item_payload(
                            category_id,
                            uom_id,
                            quantity="2",
                            unit_price="500.00",
                        )
                    ],
                },
            )
            assert updated.status_code == 200, updated.text
            updated_data = updated.json()
            assert updated_data["row_version"] == 2

            stale_submit = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/submit",
                headers=pic_headers,
                json={"expected_row_version": 1},
            )
            assert stale_submit.status_code == 409, stale_submit.text

            submitted = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/submit",
                headers=pic_headers,
                json={"expected_row_version": updated_data["row_version"]},
            )
            assert submitted.status_code == 200, submitted.text
            submitted_data = submitted.json()
            assert submitted_data["status"] == "PENDING_APPROVAL"
            assert submitted_data["row_version"] == 3

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as approver_client:
            approver_headers = await login(approver_client, APPROVER_USERNAME)
            pending = await approver_client.get(
                "/api/v1/budget-plan-approvals/pending",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert pending.status_code == 200, pending.text
            first_item = pending.json()[0]
            first_approval = first_item["approval"]
            assert first_approval["submission_no"] == 1
            assert first_approval["version_no"] == 1

            rejected = await approver_client.post(
                f"/api/v1/budget-plans/{plan_id}/reject",
                headers=approver_headers,
                json={
                    "expected_row_version": first_item["budget_plan"]["row_version"],
                    "expected_submission_no": first_approval["submission_no"],
                    "expected_version_no": first_approval["version_no"],
                    "reason": "Revisi diperlukan untuk stale-decision test",
                },
            )
            assert rejected.status_code == 200, rejected.text
            rejected_data = rejected.json()
            assert rejected_data["status"] == "REJECTED"

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as pic_client:
            pic_headers = await login(pic_client, PIC_USERNAME)
            revised = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/revise",
                headers=pic_headers,
                json={
                    "expected_row_version": rejected_data["row_version"],
                    "title": "Phase 3D Revised Plan",
                    "description": "Second reviewed version",
                    "items": [
                        item_payload(
                            category_id,
                            uom_id,
                            quantity="3",
                            unit_price="400.00",
                        )
                    ],
                },
            )
            assert revised.status_code == 200, revised.text
            revised_data = revised.json()
            assert revised_data["current_version_no"] == 2
            assert revised_data["row_version"] == 5

            resubmitted = await pic_client.post(
                f"/api/v1/budget-plans/{plan_id}/submit",
                headers=pic_headers,
                json={"expected_row_version": revised_data["row_version"]},
            )
            assert resubmitted.status_code == 200, resubmitted.text
            resubmitted_data = resubmitted.json()
            assert resubmitted_data["row_version"] == 6

            context = await pic_client.get(
                "/api/v1/budget-plans/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert context.status_code == 200, context.text
            context_data = context.json()
            assert Decimal(context_data["scope_allocation_amount"]) == Decimal("5000.00")
            assert Decimal(context_data["scope_committed_amount"]) == Decimal("0.00")
            assert Decimal(context_data["scope_draft_pipeline_amount"]) == Decimal("1200.00")
            assert Decimal(context_data["scope_available_amount"]) == Decimal("5000.00")

        async with AsyncClient(
            transport=transport,
            base_url="http://localhost",
            follow_redirects=True,
        ) as approver_client:
            approver_headers = await login(approver_client, APPROVER_USERNAME)

            stale_approve = await approver_client.post(
                f"/api/v1/budget-plans/{plan_id}/approve",
                headers=approver_headers,
                json={
                    "expected_row_version": first_item["budget_plan"]["row_version"],
                    "expected_submission_no": first_approval["submission_no"],
                    "expected_version_no": first_approval["version_no"],
                    "decision_note": "Stale browser tab must not approve a newer submission",
                },
            )
            assert stale_approve.status_code == 409, stale_approve.text

            pending = await approver_client.get(
                "/api/v1/budget-plan-approvals/pending",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert pending.status_code == 200, pending.text
            assert len(pending.json()) == 1
            fresh_item = pending.json()[0]
            fresh_approval = fresh_item["approval"]
            assert fresh_approval["submission_no"] == 2
            assert fresh_approval["version_no"] == 2

            approved = await approver_client.post(
                f"/api/v1/budget-plans/{plan_id}/approve",
                headers=approver_headers,
                json={
                    "expected_row_version": fresh_item["budget_plan"]["row_version"],
                    "expected_submission_no": fresh_approval["submission_no"],
                    "expected_version_no": fresh_approval["version_no"],
                    "decision_note": "Reviewed exact resubmitted version",
                },
            )
            assert approved.status_code == 200, approved.text
            approved_data = approved.json()
            assert approved_data["status"] == "APPROVED"
            assert Decimal(approved_data["allocation_committed_amount"]) == Decimal("1200.00")
            assert Decimal(approved_data["allocation_available_amount"]) == Decimal("3800.00")

            approvals = await approver_client.get(f"/api/v1/budget-plans/{plan_id}/approvals")
            assert approvals.status_code == 200, approvals.text
            history = approvals.json()
            assert len(history) == 2
            assert {item["submission_no"] for item in history} == {1, 2}
            assert {item["version_no"] for item in history} == {1, 2}

        session_factory = get_session_factory()
        async with session_factory() as session:
            audit = await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "BUDGET_PLAN_APPROVED",
                    AuditLog.entity_id == UUID(plan_id),
                )
            )
            assert audit is not None
            assert audit.after_data["submission_no"] == 2
            assert audit.after_data["version_no"] == 2
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 3D budget plan hardening verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
