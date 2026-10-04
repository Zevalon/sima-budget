import asyncio
from decimal import Decimal
from uuid import UUID

from app.core.database import get_engine, get_session_factory
from app.modules.budget_foundation.models import FiscalYear
from app.modules.unit_allocations.service import get_unit_allocation_overview
from scripts.verify_phase4a import (
    UNIT_CODE,
    cleanup,
    concurrent_post,
    login_client,
    setup,
)


async def verify() -> None:
    fiscal_year_id = await setup()
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
            plan_id = context_data["plans"][0]["budget_plan_id"]

            session_factory = get_session_factory()
            async with session_factory() as session:
                fiscal_year = await session.get(FiscalYear, UUID(fiscal_year_id))
                assert fiscal_year is not None
                valid_date = fiscal_year.start_date.isoformat()
            first = await client.post(
                "/api/v1/realizations",
                headers=headers,
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P4C-CONCURRENT-001",
                    "description": "Concurrent posting candidate A",
                    "amount": "600.00",
                },
            )
            second = await client.post(
                "/api/v1/realizations",
                headers=headers,
                json={
                    "budget_plan_id": plan_id,
                    "realization_date": valid_date,
                    "reference_number": "P4C-CONCURRENT-002",
                    "description": "Concurrent posting candidate B",
                    "amount": "600.00",
                },
            )
            assert first.status_code == 201, first.text
            assert second.status_code == 201, second.text

            statuses = await asyncio.gather(
                concurrent_post(first.json()["id"]),
                concurrent_post(second.json()["id"]),
            )
            assert sorted(statuses) == [200, 409], statuses

            refreshed = await client.get(
                "/api/v1/realizations/context",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert refreshed.status_code == 200, refreshed.text
            data = refreshed.json()
            assert Decimal(data["scope_approved_amount"]) == Decimal("1000.00")
            assert Decimal(data["scope_realized_amount"]) == Decimal("600.00")
            assert Decimal(data["scope_draft_pipeline_amount"]) == Decimal("600.00")
            assert Decimal(data["scope_remaining_amount"]) == Decimal("400.00")
            assert Decimal(data["scope_utilization_percent"]) == Decimal("60.00")
            plan = data["plans"][0]
            assert Decimal(plan["utilization_percent"]) == Decimal("60.00")
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
            assert allocation.realized_amount == Decimal("600.00")
            assert allocation.realization_draft_pipeline_amount == Decimal("600.00")
            assert allocation.remaining_to_realize_amount == Decimal("400.00")
            assert allocation.realized_amount <= allocation.committed_amount <= allocation.amount
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 4C realization aggregates and monitoring verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
