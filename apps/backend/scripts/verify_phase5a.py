import asyncio
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select

from app.core.database import get_engine, get_session_factory
from app.modules.budget_foundation.models import FiscalYear
from app.modules.roles.models import Permission, Role, RolePermission
from scripts.verify_phase4a import cleanup, login_client, setup


async def verify_role_permissions() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        for role_code in (
            "SYSTEM_ADMIN",
            "BUDGET_ADMIN",
            "UNIT_PIC",
            "UNIT_APPROVER",
            "MANAGEMENT_APPROVER",
            "AUDITOR",
            "VIEWER",
        ):
            permission = await session.scalar(
                select(Permission.code)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .join(Role, Role.id == RolePermission.role_id)
                .where(Role.code == role_code, Permission.code == "reports.view")
            )
            assert permission == "reports.view", role_code


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
            plan_id = context.json()["plans"][0]["budget_plan_id"]

            session_factory = get_session_factory()
            async with session_factory() as session:
                fiscal_year = await session.get(FiscalYear, UUID(fiscal_year_id))
                assert fiscal_year is not None
                valid_date = fiscal_year.start_date.isoformat()

            posted = await client.post(
                "/api/v1/realizations",
                headers=headers,
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P5A-POSTED-001",
                    "description": "Phase 5A posted realization",
                    "amount": "400.00",
                },
            )
            assert posted.status_code == 201, posted.text
            posted_data = posted.json()
            posted_result = await client.post(
                f"/api/v1/realizations/{posted_data['id']}/post",
                headers=headers,
                json={
                    "expected_row_version": posted_data["row_version"],
                    "expected_status": posted_data["status"],
                    "expected_plan_version_id": posted_data["plan_version_id"],
                },
            )
            assert posted_result.status_code == 200, posted_result.text

            draft = await client.post(
                "/api/v1/realizations",
                headers=headers,
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P5A-DRAFT-001",
                    "description": "Phase 5A draft realization",
                    "amount": "100.00",
                },
            )
            assert draft.status_code == 201, draft.text

            report = await client.get(
                "/api/v1/reports/financial-summary",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert report.status_code == 200, report.text
            data = report.json()

            assert data["fiscal_year_id"] == fiscal_year_id
            assert Decimal(data["scope_budget_amount"]) == Decimal("1000.00")
            assert Decimal(data["allocated_amount"]) == Decimal("1000.00")
            assert Decimal(data["committed_amount"]) == Decimal("1000.00")
            assert Decimal(data["available_amount"]) == Decimal("0.00")
            assert Decimal(data["realized_amount"]) == Decimal("400.00")
            assert Decimal(data["realization_draft_pipeline_amount"]) == Decimal("100.00")
            assert Decimal(data["remaining_to_realize_amount"]) == Decimal("600.00")
            assert Decimal(data["utilization_percent"]) == Decimal("40.00")
            assert data["allocation_count"] == 1
            assert data["approved_plan_count"] == 1
            assert data["realization_count"] == 1
            assert len(data["unit_summaries"]) == 1
            assert data["unit_summaries"][0]["organization_unit_code"] == "P4A-UNIT"
            assert Decimal(data["unit_summaries"][0]["realized_amount"]) == Decimal("400.00")
            assert len(data["monthly_realization"]) == 12
            month = int(valid_date[5:7])
            monthly = next(item for item in data["monthly_realization"] if item["month"] == month)
            assert Decimal(monthly["realized_amount"]) == Decimal("400.00")
        finally:
            await client.aclose()
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 5A reporting foundation verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
