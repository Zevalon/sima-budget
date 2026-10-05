import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import FiscalYear
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.unit_allocations.service import get_unit_allocation_overview
from app.modules.users.models import User
from scripts.verify_phase4a import UNIT_CODE, cleanup, login_client, setup

OUTSIDER_USERNAME = "phase4d_outsider"
OUTSIDER_PASSWORD = "Phase4D-Outsider!"
OUTSIDER_UNIT_CODE = "P4D-OUT"


async def cleanup_outsider() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == OUTSIDER_USERNAME))
        unit = await session.scalar(
            select(OrganizationUnit).where(OrganizationUnit.code == OUTSIDER_UNIT_CODE)
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
        await session.commit()


async def setup_outsider() -> None:
    await cleanup_outsider()
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        root = await session.scalar(select(OrganizationUnit).where(OrganizationUnit.code == "ROOT"))
        role = (
            await session.scalar(
                select(Role).where(
                    Role.organization_id == organization.id,
                    Role.code == "UNIT_PIC",
                )
            )
            if organization is not None
            else None
        )
        if organization is None or root is None or role is None:
            raise RuntimeError("Bootstrap Phase 4D belum lengkap.")

        user = User(
            username=OUTSIDER_USERNAME,
            email=None,
            full_name="Phase 4D Outside Scope PIC",
            password_hash=hash_password(OUTSIDER_PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        unit = OrganizationUnit(
            organization_id=organization.id,
            unit_type_id=root.unit_type_id,
            parent_id=root.id,
            code=OUTSIDER_UNIT_CODE,
            name="Phase 4D Outside Scope Unit",
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
                job_title="Outside scope verification",
                is_primary=True,
            )
        )
        session.add(
            UserRoleAssignment(
                user_id=user.id,
                role_id=role.id,
                scope_type="OWN_UNIT",
                scope_unit_id=unit.id,
            )
        )
        await session.commit()


async def outsider_client() -> AsyncClient:
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
        follow_redirects=True,
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": OUTSIDER_USERNAME, "password": OUTSIDER_PASSWORD},
    )
    assert login.status_code == 200, login.text
    return client


async def verify() -> None:
    fiscal_year_id = await setup()
    await setup_outsider()
    try:
        client, headers = await login_client()
        try:
            context = await client.get(
                "/api/v1/realizations/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert context.status_code == 200, context.text
            context_data = context.json()
            assert len(context_data["plans"]) == 1
            plan = context_data["plans"][0]
            plan_id = plan["budget_plan_id"]
            plan_version_id = plan["plan_version_id"]

            session_factory = get_session_factory()
            async with session_factory() as session:
                fiscal = await session.get(FiscalYear, UUID(fiscal_year_id))
                assert fiscal is not None
                valid_date = fiscal.start_date.isoformat()

            created = await client.post(
                "/api/v1/realizations",
                headers=headers,
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P4D-WORKFLOW-001",
                    "description": "Phase 4D workflow identity verification",
                    "amount": "300.00",
                },
            )
            assert created.status_code == 201, created.text
            created_data = created.json()
            realization_id = created_data["id"]
            assert created_data["status"] == "DRAFT"

            wrong_status = await client.patch(
                f"/api/v1/realizations/{realization_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "expected_status": "POSTED",
                    "expected_plan_version_id": plan_version_id,
                    "realization_date": valid_date,
                    "reference_number": "P4D-WRONG-STATUS",
                    "description": "Must fail due to stale workflow status",
                    "amount": "250.00",
                },
            )
            assert wrong_status.status_code == 409, wrong_status.text

            wrong_plan_version = await client.patch(
                f"/api/v1/realizations/{realization_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": str(uuid4()),
                    "realization_date": valid_date,
                    "reference_number": "P4D-WRONG-VERSION",
                    "description": "Must fail due to stale plan version identity",
                    "amount": "250.00",
                },
            )
            assert wrong_plan_version.status_code == 409, wrong_plan_version.text

            updated = await client.patch(
                f"/api/v1/realizations/{realization_id}",
                headers=headers,
                json={
                    "expected_row_version": 1,
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                    "realization_date": valid_date,
                    "reference_number": "P4D-WORKFLOW-001-R1",
                    "description": "Phase 4D workflow identity verification updated",
                    "amount": "250.00",
                },
            )
            assert updated.status_code == 200, updated.text
            updated_data = updated.json()
            assert updated_data["row_version"] == 2

            stale_post_identity = await client.post(
                f"/api/v1/realizations/{realization_id}/post",
                headers=headers,
                json={
                    "expected_row_version": 2,
                    "expected_status": "POSTED",
                    "expected_plan_version_id": plan_version_id,
                },
            )
            assert stale_post_identity.status_code == 409, stale_post_identity.text

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

            wrong_reverse_identity = await client.post(
                f"/api/v1/realizations/{realization_id}/reverse",
                headers=headers,
                json={
                    "expected_row_version": posted_data["row_version"],
                    "expected_status": "POSTED",
                    "expected_plan_version_id": str(uuid4()),
                    "reason": "Wrong version identity must fail.",
                },
            )
            assert wrong_reverse_identity.status_code == 409, wrong_reverse_identity.text

            reversed_response = await client.post(
                f"/api/v1/realizations/{realization_id}/reverse",
                headers=headers,
                json={
                    "expected_row_version": posted_data["row_version"],
                    "expected_status": "POSTED",
                    "expected_plan_version_id": plan_version_id,
                    "reason": "Phase 4D reversal verification.",
                },
            )
            assert reversed_response.status_code == 200, reversed_response.text
            reversed_data = reversed_response.json()
            assert reversed_data["status"] == "REVERSED"

            wrong_correction_identity = await client.post(
                f"/api/v1/realizations/{realization_id}/correction",
                headers=headers,
                json={
                    "expected_row_version": reversed_data["row_version"],
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                },
            )
            assert wrong_correction_identity.status_code == 409, wrong_correction_identity.text

            correction = await client.post(
                f"/api/v1/realizations/{realization_id}/correction",
                headers=headers,
                json={
                    "expected_row_version": reversed_data["row_version"],
                    "expected_status": "REVERSED",
                    "expected_plan_version_id": plan_version_id,
                },
            )
            assert correction.status_code == 201, correction.text
            correction_data = correction.json()
            assert correction_data["status"] == "DRAFT"
            assert correction_data["correction_of_id"] == realization_id

            source_after_correction = await client.get(f"/api/v1/realizations/{realization_id}")
            assert source_after_correction.status_code == 200, source_after_correction.text
            source_data = source_after_correction.json()
            assert source_data["correction_id"] == correction_data["id"]
            assert source_data["row_version"] == reversed_data["row_version"] + 1

            stale_duplicate_correction = await client.post(
                f"/api/v1/realizations/{realization_id}/correction",
                headers=headers,
                json={
                    "expected_row_version": reversed_data["row_version"],
                    "expected_status": "REVERSED",
                    "expected_plan_version_id": plan_version_id,
                },
            )
            assert stale_duplicate_correction.status_code == 409, stale_duplicate_correction.text

            corrected = await client.patch(
                f"/api/v1/realizations/{correction_data['id']}",
                headers=headers,
                json={
                    "expected_row_version": correction_data["row_version"],
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                    "realization_date": valid_date,
                    "reference_number": "P4D-CORRECTED-001",
                    "description": "Phase 4D corrected realization",
                    "amount": "200.00",
                },
            )
            assert corrected.status_code == 200, corrected.text
            corrected_data = corrected.json()

            corrected_posted = await client.post(
                f"/api/v1/realizations/{correction_data['id']}/post",
                headers=headers,
                json={
                    "expected_row_version": corrected_data["row_version"],
                    "expected_status": "DRAFT",
                    "expected_plan_version_id": plan_version_id,
                },
            )
            assert corrected_posted.status_code == 200, corrected_posted.text

            final_context = await client.get(
                "/api/v1/realizations/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert final_context.status_code == 200, final_context.text
            final_data = final_context.json()
            assert Decimal(final_data["scope_approved_amount"]) == Decimal("1000.00")
            assert Decimal(final_data["scope_realized_amount"]) == Decimal("200.00")
            assert Decimal(final_data["scope_draft_pipeline_amount"]) == Decimal("0.00")
            assert Decimal(final_data["scope_remaining_amount"]) == Decimal("800.00")
            assert Decimal(final_data["scope_utilization_percent"]) == Decimal("20.00")
        finally:
            await client.aclose()

        session_factory = get_session_factory()
        async with session_factory() as session:
            overview = await get_unit_allocation_overview(
                session,
                fiscal_year_id=UUID(fiscal_year_id),
            )
            allocation = next(
                item for item in overview.allocations if item.organization_unit_code == UNIT_CODE
            )
            assert allocation.amount == Decimal("1000.00")
            assert allocation.committed_amount == Decimal("1000.00")
            assert allocation.realized_amount == Decimal("200.00")
            assert allocation.realization_draft_pipeline_amount == Decimal("0.00")
            assert allocation.remaining_to_realize_amount == Decimal("800.00")
            assert allocation.realized_amount <= allocation.committed_amount <= allocation.amount

        outside = await outsider_client()
        try:
            denied = await outside.get(f"/api/v1/realizations/{correction_data['id']}")
            assert denied.status_code == 403, denied.text
            outside_context = await outside.get(
                "/api/v1/realizations/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert outside_context.status_code == 200, outside_context.text
            outside_data = outside_context.json()
            assert outside_data["plans"] == []
            assert Decimal(outside_data["scope_realized_amount"]) == Decimal("0.00")
        finally:
            await outside.aclose()
    finally:
        await cleanup_outsider()
        await cleanup()
        await get_engine().dispose()

    print("Phase 4D realization hardening verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
