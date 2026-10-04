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
from app.modules.settings.models import ApplicationSetting
from app.modules.users.models import User

BUDGET_USERNAME = "phase2b2_budget_admin"
APPROVER_USERNAME = "phase2b2_management_approver"
PASSWORD = "Phase2B2-Verification!"
FISCAL_CODE = "P2B2-2196"


async def cleanup(*, restore_self_approval: bool | None = None) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        users = (
            await session.scalars(
                select(User).where(User.username.in_([BUDGET_USERNAME, APPROVER_USERNAME]))
            )
        ).all()
        fiscal_year = await session.scalar(select(FiscalYear).where(FiscalYear.code == FISCAL_CODE))
        budget = None
        if fiscal_year is not None:
            budget = await session.scalar(
                select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fiscal_year.id)
            )

        entity_ids = []
        if budget is not None:
            entity_ids.append(budget.id)
            await session.execute(
                delete(AnnualBudgetApproval).where(
                    AnnualBudgetApproval.annual_budget_id == budget.id
                )
            )
            await session.delete(budget)
        if fiscal_year is not None:
            entity_ids.append(fiscal_year.id)

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

        if fiscal_year is not None:
            await session.delete(fiscal_year)
        for user in users:
            await session.delete(user)

        if restore_self_approval is not None:
            setting = await session.scalar(select(ApplicationSetting))
            if setting is not None:
                setting.allow_self_approval = restore_self_approval

        await session.commit()


async def setup() -> bool:
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
        setting = await session.scalar(
            select(ApplicationSetting).where(ApplicationSetting.organization_id == organization.id)
        )
        if root_unit is None or budget_role is None or approver_role is None or setting is None:
            raise RuntimeError("Bootstrap Phase 2B2 belum lengkap.")

        original_self_approval = setting.allow_self_approval
        setting.allow_self_approval = False

        budget_user = User(
            username=BUDGET_USERNAME,
            email=None,
            full_name="Phase 2B2 Budget Admin",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        approver_user = User(
            username=APPROVER_USERNAME,
            email=None,
            full_name="Phase 2B2 Management Approver",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        session.add_all([budget_user, approver_user])
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
                    user_id=budget_user.id,
                    role_id=approver_role.id,
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
        return original_self_approval


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
        assert "annual_budgets.approve" not in system_admin
        assert "annual_budgets.approve" not in budget_admin
        assert "annual_budgets.approve" in management_approver
        assert "annual_budgets.create" not in management_approver


async def login(client: AsyncClient, username: str) -> dict:
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()


async def verify() -> None:
    original_self_approval = await setup()
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
            ) as approver_client,
        ):
            budget_login = await login(budget_client, BUDGET_USERNAME)
            budget_permissions = set(budget_login["permissions"])
            assert "annual_budgets.approve" in budget_permissions
            budget_headers = {"X-CSRF-Token": budget_login["csrf_token"]}

            fiscal_year = await budget_client.post(
                "/api/v1/fiscal-years",
                headers=budget_headers,
                json={
                    "code": FISCAL_CODE,
                    "year": 2196,
                    "start_date": "2196-01-01",
                    "end_date": "2196-12-31",
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

            created = await budget_client.post(
                "/api/v1/annual-budgets",
                headers=budget_headers,
                json={
                    "fiscal_year_id": fiscal_year_id,
                    "amount": "600000000000.00",
                    "notes": "Phase 2B2 verification",
                },
            )
            assert created.status_code == 201, created.text
            budget_id = created.json()["id"]

            submitted = await budget_client.post(
                f"/api/v1/annual-budgets/{budget_id}/submit",
                headers=budget_headers,
            )
            assert submitted.status_code == 200, submitted.text

            self_approve = await budget_client.post(
                f"/api/v1/annual-budgets/{budget_id}/approve",
                headers=budget_headers,
                json={"decision_note": "Should be rejected by self-approval guard"},
            )
            assert self_approve.status_code == 409, self_approve.text

            approver_login = await login(approver_client, APPROVER_USERNAME)
            approver_permissions = set(approver_login["permissions"])
            assert "annual_budgets.approve" in approver_permissions
            assert "annual_budgets.create" not in approver_permissions
            approver_headers = {"X-CSRF-Token": approver_login["csrf_token"]}

            pending = await approver_client.get("/api/v1/annual-budget-approvals/pending")
            assert pending.status_code == 200, pending.text
            assert any(item["id"] == budget_id for item in pending.json())

            reject_no_csrf = await approver_client.post(
                f"/api/v1/annual-budgets/{budget_id}/reject",
                json={"reason": "Butuh revisi"},
            )
            assert reject_no_csrf.status_code == 403, reject_no_csrf.text

            rejected = await approver_client.post(
                f"/api/v1/annual-budgets/{budget_id}/reject",
                headers=approver_headers,
                json={"reason": "Butuh revisi rincian pagu"},
            )
            assert rejected.status_code == 200, rejected.text
            assert rejected.json()["status"] == "REJECTED"
            assert rejected.json()["rejection_reason"] == "Butuh revisi rincian pagu"

            revised = await budget_client.patch(
                f"/api/v1/annual-budgets/{budget_id}",
                headers=budget_headers,
                json={
                    "amount": "610000000000.25",
                    "notes": "Revised after rejection",
                },
            )
            assert revised.status_code == 200, revised.text
            assert revised.json()["status"] == "DRAFT"
            assert revised.json()["version"] == 2
            assert Decimal(revised.json()["amount"]) == Decimal("610000000000.25")

            resubmitted = await budget_client.post(
                f"/api/v1/annual-budgets/{budget_id}/submit",
                headers=budget_headers,
            )
            assert resubmitted.status_code == 200, resubmitted.text
            assert resubmitted.json()["status"] == "PENDING_APPROVAL"

            approved = await approver_client.post(
                f"/api/v1/annual-budgets/{budget_id}/approve",
                headers=approver_headers,
                json={"decision_note": "Pagu organisasi disetujui"},
            )
            assert approved.status_code == 200, approved.text
            assert approved.json()["status"] == "APPROVED"
            assert approved.json()["approved_by"] is not None

            locked = await budget_client.patch(
                f"/api/v1/annual-budgets/{budget_id}",
                headers=budget_headers,
                json={"amount": "620000000000.00"},
            )
            assert locked.status_code == 409, locked.text

            approvals = await budget_client.get(f"/api/v1/annual-budgets/{budget_id}/approvals")
            assert approvals.status_code == 200, approvals.text
            rows = approvals.json()
            assert len(rows) == 2
            assert rows[0]["submission_no"] == 2
            assert rows[0]["status"] == "APPROVED"
            assert rows[1]["submission_no"] == 1
            assert rows[1]["status"] == "REJECTED"

        session_factory = get_session_factory()
        async with session_factory() as session:
            approved_audit = await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "ANNUAL_BUDGET_APPROVED",
                    AuditLog.entity_id == budget_id,
                )
            )
            rejected_audit = await session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "ANNUAL_BUDGET_REJECTED",
                    AuditLog.entity_id == budget_id,
                )
            )
            assert approved_audit is not None
            assert rejected_audit is not None
    finally:
        await cleanup(restore_self_approval=original_self_approval)
        await get_engine().dispose()

    print("Phase 2B2 annual budget approval verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
