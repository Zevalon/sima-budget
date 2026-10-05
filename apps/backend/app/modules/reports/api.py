from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.reports.schemas import FinancialSummaryResponse
from app.modules.reports.service import get_financial_summary

router = APIRouter(tags=["reports"])


@router.get("/reports/financial-summary", response_model=FinancialSummaryResponse)
async def financial_summary_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("reports.view"))],
    fiscal_year_id: Annotated[UUID, Query()],
    organization_unit_id: Annotated[UUID | None, Query()] = None,
) -> FinancialSummaryResponse:
    return await get_financial_summary(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
        organization_unit_id=organization_unit_id,
    )
