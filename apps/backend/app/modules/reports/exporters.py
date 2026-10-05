from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from html import escape
from typing import Literal
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

from app.modules.reports.schemas import (
    FinancialSummaryResponse,
    ReportCategoryPlanSummary,
    ReportMonthlyRealization,
)

ExportFormat = Literal["csv", "xlsx", "pdf"]


@dataclass(frozen=True, slots=True)
class ReportExport:
    content: bytes
    media_type: str
    filename: str


def _currency_text(value: Decimal) -> str:
    fixed = value.quantize(Decimal("0.01"))
    whole, fraction = f"{fixed:.2f}".split(".")
    grouped = f"{int(whole):,}".replace(",", ".")
    return f"Rp {grouped},{fraction}"


def _safe_filename_part(value: str) -> str:
    cleaned = re_sub_filename(value)
    return cleaned or "report"


def re_sub_filename(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return cleaned.strip("-")


def _filtered_months(
    summary: FinancialSummaryResponse,
    month: int | None,
) -> list[ReportMonthlyRealization]:
    if month is None:
        return summary.monthly_realization
    return [item for item in summary.monthly_realization if item.month == month]


def _filtered_categories(
    summary: FinancialSummaryResponse,
    category_id: UUID | None,
) -> list[ReportCategoryPlanSummary]:
    if category_id is None:
        return summary.category_plan_summaries
    return [
        item for item in summary.category_plan_summaries if item.budget_category_id == category_id
    ]


def build_csv_export(
    summary: FinancialSummaryResponse,
    *,
    month: int | None = None,
    category_id: UUID | None = None,
) -> ReportExport:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(["SIMA - Laporan Anggaran"])
    writer.writerow(["Tahun Anggaran", summary.fiscal_year_code])
    writer.writerow(["Status Tahun", summary.fiscal_year_status.value])
    writer.writerow([])
    writer.writerow(["Ringkasan", "Nilai"])
    writer.writerow(["Pagu Scope", f"{summary.scope_budget_amount:.2f}"])
    writer.writerow(["Allocated", f"{summary.allocated_amount:.2f}"])
    writer.writerow(["Committed", f"{summary.committed_amount:.2f}"])
    writer.writerow(["Realized", f"{summary.realized_amount:.2f}"])
    writer.writerow(["Available", f"{summary.available_amount:.2f}"])
    writer.writerow(["Sisa Direalisasi", f"{summary.remaining_to_realize_amount:.2f}"])
    writer.writerow(["Draft Plan Pipeline", f"{summary.draft_pipeline_amount:.2f}"])
    writer.writerow(
        [
            "Draft Realization Pipeline",
            f"{summary.realization_draft_pipeline_amount:.2f}",
        ]
    )
    writer.writerow(["Utilization (%)", f"{summary.utilization_percent:.2f}"])

    writer.writerow([])
    writer.writerow(
        [
            "Unit Code",
            "Unit Name",
            "Allocated",
            "Committed",
            "Plan Pipeline",
            "Realized",
            "Realization Pipeline",
            "Available",
            "Remaining To Realize",
            "Utilization (%)",
        ]
    )
    for unit_item in summary.unit_summaries:
        writer.writerow(
            [
                unit_item.organization_unit_code,
                unit_item.organization_unit_name,
                f"{unit_item.allocated_amount:.2f}",
                f"{unit_item.committed_amount:.2f}",
                f"{unit_item.draft_pipeline_amount:.2f}",
                f"{unit_item.realized_amount:.2f}",
                f"{unit_item.realization_draft_pipeline_amount:.2f}",
                f"{unit_item.available_amount:.2f}",
                f"{unit_item.remaining_to_realize_amount:.2f}",
                f"{unit_item.utilization_percent:.2f}",
            ]
        )

    writer.writerow([])
    writer.writerow(["Month", "Realized"])
    for month_item in _filtered_months(summary, month):
        writer.writerow([month_item.month_label, f"{month_item.realized_amount:.2f}"])

    writer.writerow([])
    writer.writerow(["Category Code", "Category Name", "Committed", "Draft Plan Pipeline"])
    for category_item in _filtered_categories(summary, category_id):
        writer.writerow(
            [
                category_item.budget_category_code,
                category_item.budget_category_name,
                f"{category_item.committed_amount:.2f}",
                f"{category_item.draft_pipeline_amount:.2f}",
            ]
        )

    filename = f"sima-financial-summary-{_safe_filename_part(summary.fiscal_year_code)}.csv"
    return ReportExport(
        content=("\ufeff" + buffer.getvalue()).encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        filename=filename,
    )


def _excel_column_name(index: int) -> str:
    result = ""
    current = index
    while current:
        current, remainder = divmod(current - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _worksheet_xml(rows: list[list[object]], *, currency_columns: set[int] | None = None) -> str:
    currency_columns = currency_columns or set()
    output: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        cells: list[str] = []
        for col_index, value in enumerate(row, start=1):
            reference = f"{_excel_column_name(col_index)}{row_index}"
            if isinstance(value, Decimal):
                style = ' s="2"' if col_index in currency_columns else ' s="1"'
                cells.append(f'<c r="{reference}"{style}><v>{value}</v></c>')
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                cells.append(f'<c r="{reference}" s="1"><v>{value}</v></c>')
            else:
                text = escape("" if value is None else str(value))
                style = ' s="3"' if row_index == 1 else ""
                cells.append(f'<c r="{reference}" t="inlineStr"{style}><is><t>{text}</t></is></c>')
        output.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        "<sheetData>" + "".join(output) + "</sheetData></worksheet>"
    )


def build_xlsx_export(
    summary: FinancialSummaryResponse,
    *,
    month: int | None = None,
    category_id: UUID | None = None,
) -> ReportExport:
    summary_rows: list[list[object]] = [
        ["Metric", "Value"],
        ["Fiscal Year", summary.fiscal_year_code],
        ["Fiscal Year Status", summary.fiscal_year_status.value],
        ["Scope Budget", summary.scope_budget_amount],
        ["Allocated", summary.allocated_amount],
        ["Committed", summary.committed_amount],
        ["Realized", summary.realized_amount],
        ["Available", summary.available_amount],
        ["Remaining To Realize", summary.remaining_to_realize_amount],
        ["Draft Plan Pipeline", summary.draft_pipeline_amount],
        ["Draft Realization Pipeline", summary.realization_draft_pipeline_amount],
        ["Utilization (%)", summary.utilization_percent],
    ]
    unit_rows: list[list[object]] = [
        [
            "Unit Code",
            "Unit Name",
            "Allocated",
            "Committed",
            "Plan Pipeline",
            "Realized",
            "Realization Pipeline",
            "Available",
            "Remaining To Realize",
            "Utilization (%)",
        ]
    ]
    for item in summary.unit_summaries:
        unit_rows.append(
            [
                item.organization_unit_code,
                item.organization_unit_name,
                item.allocated_amount,
                item.committed_amount,
                item.draft_pipeline_amount,
                item.realized_amount,
                item.realization_draft_pipeline_amount,
                item.available_amount,
                item.remaining_to_realize_amount,
                item.utilization_percent,
            ]
        )

    monthly_rows: list[list[object]] = [["Month", "Realized"]]
    monthly_rows.extend(
        [item.month_label, item.realized_amount] for item in _filtered_months(summary, month)
    )

    category_rows: list[list[object]] = [
        [
            "Category Code",
            "Category Name",
            "Committed",
            "Draft Plan Pipeline",
        ]
    ]
    category_rows.extend(
        [
            item.budget_category_code,
            item.budget_category_name,
            item.committed_amount,
            item.draft_pipeline_amount,
        ]
        for item in _filtered_categories(summary, category_id)
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>"
        '<sheet name="Ringkasan" sheetId="1" r:id="rId1"/>'
        '<sheet name="Unit" sheetId="2" r:id="rId2"/>'
        '<sheet name="Bulanan" sheetId="3" r:id="rId3"/>'
        '<sheet name="Kategori" sheetId="4" r:id="rId4"/>'
        "</sheets></workbook>"
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>'
        '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet4.xml"/>'
        '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.'
        'relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet4.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        "</Types>"
    )
    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;Rp&quot; #,##0.00"/></numFmts>'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
        "</cellStyleXfs>"
        '<cellXfs count="4">'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
        '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0"/>'
        "</cellXfs>"
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        "</styleSheet>"
    )

    output = io.BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/styles.xml", styles_xml)
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            _worksheet_xml(summary_rows, currency_columns={2}),
        )
        archive.writestr(
            "xl/worksheets/sheet2.xml",
            _worksheet_xml(unit_rows, currency_columns={3, 4, 5, 6, 7, 8, 9}),
        )
        archive.writestr(
            "xl/worksheets/sheet3.xml",
            _worksheet_xml(monthly_rows, currency_columns={2}),
        )
        archive.writestr(
            "xl/worksheets/sheet4.xml",
            _worksheet_xml(category_rows, currency_columns={3, 4}),
        )

    filename = f"sima-financial-summary-{_safe_filename_part(summary.fiscal_year_code)}.xlsx"
    return ReportExport(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _pdf_lines(
    summary: FinancialSummaryResponse,
    *,
    month: int | None,
    category_id: UUID | None,
) -> list[str]:
    scope_label = "Pagu Unit" if summary.organization_unit_filter_id is not None else "Pagu Scope"
    lines = [
        "SIMA - Laporan Anggaran",
        f"Tahun Anggaran: {summary.fiscal_year_code}",
        f"Status Tahun: {summary.fiscal_year_status.value}",
        "",
        "RINGKASAN",
        f"{scope_label}: {_currency_text(summary.scope_budget_amount)}",
        f"Allocated: {_currency_text(summary.allocated_amount)}",
        f"Committed: {_currency_text(summary.committed_amount)}",
        f"Realized: {_currency_text(summary.realized_amount)}",
        f"Available: {_currency_text(summary.available_amount)}",
        f"Sisa Direalisasi: {_currency_text(summary.remaining_to_realize_amount)}",
        f"Draft Plan Pipeline: {_currency_text(summary.draft_pipeline_amount)}",
        (
            "Draft Realization Pipeline: "
            f"{_currency_text(summary.realization_draft_pipeline_amount)}"
        ),
        f"Utilization: {summary.utilization_percent:.2f}%",
        "",
        "UNIT",
    ]
    for unit_item in summary.unit_summaries:
        lines.extend(
            [
                f"{unit_item.organization_unit_code} - {unit_item.organization_unit_name}",
                (
                    f"  Allocated: {_currency_text(unit_item.allocated_amount)} | "
                    f"Committed: {_currency_text(unit_item.committed_amount)}"
                ),
                (
                    f"  Realized: {_currency_text(unit_item.realized_amount)} | "
                    f"Available: {_currency_text(unit_item.available_amount)}"
                ),
            ]
        )

    lines.extend(["", "REALISASI BULANAN", "Month | Realized"])
    for month_item in _filtered_months(summary, month):
        lines.append(f"{month_item.month_label} | {_currency_text(month_item.realized_amount)}")

    lines.extend(["", "KATEGORI"])
    for category_item in _filtered_categories(summary, category_id):
        lines.extend(
            [
                (f"{category_item.budget_category_code} - {category_item.budget_category_name}"),
                (
                    f"  Committed: {_currency_text(category_item.committed_amount)} | "
                    "Draft Pipeline: "
                    f"{_currency_text(category_item.draft_pipeline_amount)}"
                ),
            ]
        )
    lines.extend(
        [
            "",
            "Catatan: Realized per kategori tidak ditampilkan karena realisasi saat ini",
            "dicatat pada level Budget Plan, bukan pada item/kategori.",
        ]
    )
    return [line[:90] for line in lines]


def _build_simple_pdf(lines: Iterable[str]) -> bytes:
    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if len(current) >= 48:
            pages.append(current)
            current = []
    if current or not pages:
        pages.append(current)

    objects: list[bytes] = []
    page_object_ids: list[int] = []
    font_object_id = 3
    next_object_id = 4
    page_pairs: list[tuple[int, int, list[str]]] = []
    for page_lines in pages:
        page_id = next_object_id
        content_id = next_object_id + 1
        next_object_id += 2
        page_object_ids.append(page_id)
        page_pairs.append((page_id, content_id, page_lines))

    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for page_id, content_id, page_lines in page_pairs:
        page_object = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_object_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode()
        while len(objects) < page_id - 1:
            objects.append(b"<<>>")
        objects.append(page_object)

        commands = ["BT", "/F1 9 Tf", "40 800 Td", "12 TL"]
        for index, line in enumerate(page_lines):
            if index:
                commands.append("T*")
            commands.append(f"({_pdf_escape(line)}) Tj")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        content_object = (
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
        while len(objects) < content_id - 1:
            objects.append(b"<<>>")
        objects.append(content_object)

    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id, payload in enumerate(objects, start=1):
        offsets.append(pdf.tell())
        pdf.write(f"{object_id} 0 obj\n".encode())
        pdf.write(payload)
        pdf.write(b"\nendobj\n")

    xref_offset = pdf.tell()
    pdf.write(f"xref\n0 {len(objects) + 1}\n".encode())
    pdf.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode())
    pdf.write(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return pdf.getvalue()


def build_pdf_export(
    summary: FinancialSummaryResponse,
    *,
    month: int | None = None,
    category_id: UUID | None = None,
) -> ReportExport:
    filename = f"sima-financial-summary-{_safe_filename_part(summary.fiscal_year_code)}.pdf"
    return ReportExport(
        content=_build_simple_pdf(_pdf_lines(summary, month=month, category_id=category_id)),
        media_type="application/pdf",
        filename=filename,
    )


def build_report_export(
    summary: FinancialSummaryResponse,
    *,
    export_format: ExportFormat,
    month: int | None = None,
    category_id: UUID | None = None,
) -> ReportExport:
    if export_format == "csv":
        return build_csv_export(summary, month=month, category_id=category_id)
    if export_format == "xlsx":
        return build_xlsx_export(summary, month=month, category_id=category_id)
    return build_pdf_export(summary, month=month, category_id=category_id)
