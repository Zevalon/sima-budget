from app.modules.reports.exporters import _pdf_lines, build_csv_export, csv_safe_text
from tests.unit.test_phase5c_report_exports import _summary


def test_csv_safe_text_blocks_spreadsheet_formula_prefixes() -> None:
    assert csv_safe_text("=1+1") == "'=1+1"
    assert csv_safe_text(" +SUM(A1:A2)") == "' +SUM(A1:A2)"
    assert csv_safe_text("@cmd") == "'@cmd"
    assert csv_safe_text("Normal Unit") == "Normal Unit"


def test_csv_export_includes_active_filter_metadata() -> None:
    summary = _summary()
    unit_id = summary.unit_filter_options[0].organization_unit_id
    category_id = summary.category_plan_summaries[0].budget_category_id
    filtered = summary.model_copy(update={"organization_unit_filter_id": unit_id})

    exported = build_csv_export(filtered, month=1, category_id=category_id)
    text = exported.content.decode("utf-8-sig")

    assert "Filter Unit" in text
    assert "IT - UPT Teknologi Informasi" in text
    assert "Filter Bulan,Jan" in text
    assert "CLOUD - Cloud & Infrastruktur" in text


def test_pdf_lines_wrap_without_silent_truncation() -> None:
    summary = _summary()
    long_name = "Unit " + ("Pelayanan Akademik dan Teknologi " * 5)
    unit = summary.unit_summaries[0].model_copy(update={"organization_unit_name": long_name})
    hardened = summary.model_copy(update={"unit_summaries": [unit]})

    lines = _pdf_lines(hardened, month=None, category_id=None)

    assert all(len(line) <= 90 for line in lines)
    assert any("Pelayanan Akademik" in line for line in lines)
    assert any("Teknologi" in line for line in lines)
