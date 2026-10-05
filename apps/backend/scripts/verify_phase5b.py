import asyncio
from uuid import uuid4

from app.core.database import get_engine
from scripts.verify_phase4a import cleanup, login_client, setup


async def verify() -> None:
    fiscal_year_id = await setup()
    try:
        client, _ = await login_client()
        try:
            unfiltered = await client.get(
                "/api/v1/reports/financial-summary",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert unfiltered.status_code == 200, unfiltered.text
            data = unfiltered.json()
            assert data["organization_unit_filter_id"] is None
            assert len(data["unit_filter_options"]) >= 1
            assert len(data["unit_summaries"]) == 1

            unit_id = data["unit_summaries"][0]["organization_unit_id"]
            filtered = await client.get(
                "/api/v1/reports/financial-summary",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "organization_unit_id": unit_id,
                },
            )
            assert filtered.status_code == 200, filtered.text
            filtered_data = filtered.json()
            assert filtered_data["organization_unit_filter_id"] == unit_id
            assert len(filtered_data["unit_filter_options"]) >= 1
            assert len(filtered_data["unit_summaries"]) == 1
            assert filtered_data["unit_summaries"][0]["organization_unit_id"] == unit_id

            forbidden = await client.get(
                "/api/v1/reports/financial-summary",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "organization_unit_id": str(uuid4()),
                },
            )
            assert forbidden.status_code == 403, forbidden.text
        finally:
            await client.aclose()
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 5B report filter verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
