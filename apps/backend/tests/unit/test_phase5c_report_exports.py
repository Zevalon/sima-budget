import io
from decimal import Decimal
from uuid import uuid4
from zipfile import ZipFile

from app.modules.annual_budgets.schemas import AnnualBudgetStatus
from app.modules.budget_foundation.schemas import FiscalYearStatus
from app.modules.reports.exporters import build_csv_export, build_pdf_export, build_xlsx_export
from app.modules.reports.schemas import (
    FinancialSummaryResponse,
    ReportCategoryPlanSummary,
    ReportMonthlyRealization,
    ReportUnitOption,
    ReportUnitSummary,
)


def _summary() -> FinancialSummaryResponse:
    unit_id = uuid4()
    category_id = uuid4()
    return FinancialSummaryResponse(
        fiscal_year_id=uuid4(),
        fiscal_year_code="FY2025",
        fiscal_year_status=FiscalYearStatus.ACTIVE,
        organization_unit_filter_id=None,
        annual_budget_id=uuid4(),
        annual_budget_status=AnnualBudgetStatus.APPROVED,
        organization_annual_budget_amount=Decimal("500000000000.00"),
        scope_budget_amount=Decimal("500000000000.00"),
        allocated_amount=Decimal("120000000000.00"),
        unallocated_amount=Decimal("380000000000.00"),
        committed_amount=Decimal("30000000000.00"),
        draft_pipeline_amount=Decimal("5000000000.00"),
        available_amount=Decimal("90000000000.00"),
        realized_amount=Decimal("12000000000.00"),
        realization_draft_pipeline_amount=Decimal("1000000000.00"),
        remaining_to_realize_amount=Decimal("18000000000.00"),
        utilization_percent=Decimal("40.00"),
        allocation_count=1,
        approved_plan_count=1,
        realization_count=1,
        unit_filter_options=[
            ReportUnitOption(
                organization_unit_id=unit_id,
                organization_unit_code="IT",
                organization_unit_name="UPT Teknologi Informasi",
            )
        ],
        unit_summaries=[
            ReportUnitSummary(
                organization_unit_id=unit_id,
                organization_unit_code="IT",
                organization_unit_name="UPT Teknologi Informasi",
                allocated_amount=Decimal("120000000000.00"),
                committed_amount=Decimal("30000000000.00"),
                draft_pipeline_amount=Decimal("5000000000.00"),
                available_amount=Decimal("90000000000.00"),
                realized_amount=Decimal("12000000000.00"),
                realization_draft_pipeline_amount=Decimal("1000000000.00"),
                remaining_to_realize_amount=Decimal("18000000000.00"),
                utilization_percent=Decimal("40.00"),
            )
        ],
        monthly_realization=[
            ReportMonthlyRealization(
                month=1,
                month_label="Jan",
                realized_amount=Decimal("12000000000.00"),
            ),
            ReportMonthlyRealization(month=2, month_label="Feb", realized_amount=Decimal("0.00")),
        ],
        category_plan_summaries=[
            ReportCategoryPlanSummary(
                budget_category_id=category_id,
                budget_category_code="CLOUD",
                budget_category_name="Cloud & Infrastruktur",
                committed_amount=Decimal("20000000000.00"),
                draft_pipeline_amount=Decimal("3000000000.00"),
            )
        ],
    )


def test_csv_export_contains_canonical_sections() -> None:
    exported = build_csv_export(_summary(), month=1)
    text = exported.content.decode("utf-8-sig")
    assert exported.filename.endswith(".csv")
    assert "Pagu Scope" in text
    assert "UPT Teknologi Informasi" in text
    assert "Jan" in text
    assert "Feb" not in text


def test_xlsx_export_is_valid_ooxml_package() -> None:
    exported = build_xlsx_export(_summary())
    assert exported.content.startswith(b"PK")
    with ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
        assert "xl/workbook.xml" in names
        assert "xl/worksheets/sheet4.xml" in names
        assert b"Kategori" in archive.read("xl/workbook.xml")


def test_pdf_export_has_pdf_signature_and_report_text() -> None:
    exported = build_pdf_export(_summary())
    assert exported.content.startswith(b"%PDF-1.4")
    assert b"SIMA - Laporan Anggaran" in exported.content
    assert exported.content.endswith(b"%%EOF\n")
