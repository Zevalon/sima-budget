import asyncio
from uuid import uuid4

from app.core.database import get_engine
from scripts.verify_phase4a import cleanup, login_client, setup


async def verify() -> None:
    fiscal_year_id = await setup()
    try:
        client, _ = await login_client()
        try:
            summary = await client.get(
                "/api/v1/reports/financial-summary",
                params={"fiscal_year_id": fiscal_year_id},
            )
            assert summary.status_code == 200, summary.text
            data = summary.json()
            unit_id = data["unit_summaries"][0]["organization_unit_id"]

            csv_response = await client.get(
                "/api/v1/reports/financial-summary/export",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "format": "csv",
                    "organization_unit_id": unit_id,
                    "month": 1,
                },
            )
            assert csv_response.status_code == 200, csv_response.text
            assert csv_response.headers["content-type"].startswith("text/csv")
            assert ".csv" in csv_response.headers["content-disposition"]
            assert b"SIMA - Laporan Anggaran" in csv_response.content

            xlsx_response = await client.get(
                "/api/v1/reports/financial-summary/export",
                params={"fiscal_year_id": fiscal_year_id, "format": "xlsx"},
            )
            assert xlsx_response.status_code == 200, xlsx_response.text
            assert xlsx_response.content.startswith(b"PK")
            assert ".xlsx" in xlsx_response.headers["content-disposition"]

            pdf_response = await client.get(
                "/api/v1/reports/financial-summary/export",
                params={"fiscal_year_id": fiscal_year_id, "format": "pdf"},
            )
            assert pdf_response.status_code == 200, pdf_response.text
            assert pdf_response.content.startswith(b"%PDF-1.4")
            assert ".pdf" in pdf_response.headers["content-disposition"]

            forbidden = await client.get(
                "/api/v1/reports/financial-summary/export",
                params={
                    "fiscal_year_id": fiscal_year_id,
                    "format": "csv",
                    "organization_unit_id": str(uuid4()),
                },
            )
            assert forbidden.status_code == 403, forbidden.text
        finally:
            await client.aclose()
    finally:
        await cleanup()
        await get_engine().dispose()

    print("Phase 5C report export verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
