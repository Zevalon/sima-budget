from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.reports.exporters import build_report_export
from app.modules.reports.schemas import FinancialSummaryResponse
from app.modules.reports.service import get_financial_summary

router = APIRouter(tags=["reports"])

_REPORT_HEADERS = {
    "Cache-Control": "private, no-store",
    "Pragma": "no-cache",
    "X-Content-Type-Options": "nosniff",
}


def _apply_report_headers(response: Response) -> None:
    for name, value in _REPORT_HEADERS.items():
        response.headers[name] = value


def _validate_export_category(
    summary: FinancialSummaryResponse,
    category_id: UUID | None,
) -> None:
    if category_id is None:
        return
    if any(
        item.budget_category_id == category_id
        for item in summary.category_plan_summaries
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Kategori anggaran tidak tersedia dalam scope laporan saat ini.",
    )


@router.get("/reports/financial-summary", response_model=FinancialSummaryResponse)
async def financial_summary_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("reports.view"))],
    response: Response,
    fiscal_year_id: Annotated[UUID, Query()],
    organization_unit_id: Annotated[UUID | None, Query()] = None,
) -> FinancialSummaryResponse:
    _apply_report_headers(response)
    return await get_financial_summary(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
        organization_unit_id=organization_unit_id,
    )


@router.get("/reports/financial-summary/export")
async def financial_summary_export_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("reports.view"))],
    fiscal_year_id: Annotated[UUID, Query()],
    format: Annotated[Literal["csv", "xlsx", "pdf"], Query()] = "csv",
    organization_unit_id: Annotated[UUID | None, Query()] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
    budget_category_id: Annotated[UUID | None, Query()] = None,
) -> Response:
    summary = await get_financial_summary(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
        organization_unit_id=organization_unit_id,
    )
    _validate_export_category(summary, budget_category_id)
    exported = build_report_export(
        summary,
        export_format=format,
        month=month,
        category_id=budget_category_id,
    )
    return Response(
        content=exported.content,
        media_type=exported.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{exported.filename}"',
            **_REPORT_HEADERS,
        },
    )
