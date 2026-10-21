import asyncio
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select

from app.core.database import get_engine, get_session_factory
from app.modules.organizations.models import OrganizationUnit
from scripts.verify_phase4a import UNIT_CODE, cleanup, login_client, setup


async def verify() -> None:
    fiscal_year_id = await setup()
    try:
        client, _ = await login_client()
        try:
            baseline = await client.get(
                "/api/v1/reports/financial-summary",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert baseline.status_code == 200, baseline.text
            assert baseline.headers["cache-control"] == "private, no-store"
            assert baseline.headers["x-content-type-options"] == "nosniff"

            baseline_data = baseline.json()
            assert len(baseline_data["unit_summaries"]) == 1
            unit_id = baseline_data["unit_summaries"][0]["organization_unit_id"]
            allocated = Decimal(baseline_data["allocated_amount"])
            committed = Decimal(baseline_data["committed_amount"])
            available = Decimal(baseline_data["available_amount"])
            realized = Decimal(baseline_data["realized_amount"])
            remaining = Decimal(baseline_data["remaining_to_realize_amount"])
            assert available == allocated - committed
            assert remaining == committed - realized

            session_factory = get_session_factory()
            async with session_factory() as session:
                unit = await session.scalar(
                    select(OrganizationUnit).where(
                        OrganizationUnit.id == UUID(unit_id),
                        OrganizationUnit.code == UNIT_CODE,
                    )
                )
                assert unit is not None
                unit.is_active = False
                await session.commit()

            historical = await client.get(
                "/api/v1/reports/financial-summary",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert historical.status_code == 200, historical.text
            historical_data = historical.json()
            assert len(historical_data["unit_summaries"]) == 1
            assert historical_data["unit_summaries"][0]["organization_unit_id"] == unit_id
            assert any(
                item["organization_unit_id"] == unit_id
                for item in historical_data["unit_filter_options"]
            )
            assert Decimal(historical_data["allocated_amount"]) == allocated
            assert Decimal(historical_data["committed_amount"]) == committed

            filtered = await client.get(
                "/api/v1/reports/financial-summary",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "organization_unit_id": unit_id,
                },
            )
            assert filtered.status_code == 200, filtered.text
            assert filtered.json()["organization_unit_filter_id"] == unit_id

            exported = await client.get(
                "/api/v1/reports/financial-summary/export",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "format": "csv",
                    "organization_unit_id": unit_id,
                    "month": 1,
                },
            )
            assert exported.status_code == 200, exported.text
            assert exported.headers["cache-control"] == "private, no-store"
            assert exported.headers["pragma"] == "no-cache"
            assert exported.headers["x-content-type-options"] == "nosniff"
            assert b"Filter Unit" in exported.content
            assert b"Filter Bulan" in exported.content

            invalid_category = await client.get(
                "/api/v1/reports/financial-summary/export",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "format": "csv",
                    "budget_category_id": str(uuid4()),
                },
            )
            assert invalid_category.status_code == 404, invalid_category.text
        finally:
            await client.aclose()
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 5D reporting hardening verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
