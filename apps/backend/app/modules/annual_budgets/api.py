from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.annual_budgets.schemas import (
    AnnualBudgetApprovalResponse,
    AnnualBudgetCreateRequest,
    AnnualBudgetResponse,
    AnnualBudgetUpdateRequest,
)
from app.modules.annual_budgets.service import (
    create_annual_budget,
    get_annual_budget,
    list_annual_budget_approvals,
    list_annual_budgets,
    submit_annual_budget,
    update_annual_budget,
)
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission

router = APIRouter(tags=["annual-budgets"])


@router.get("/annual-budgets", response_model=list[AnnualBudgetResponse])
async def annual_budgets_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("annual_budgets.view"))],
    fiscal_year_id: Annotated[UUID | None, Query()] = None,
) -> list[AnnualBudgetResponse]:
    return await list_annual_budgets(session, fiscal_year_id=fiscal_year_id)


@router.get("/annual-budgets/{annual_budget_id}", response_model=AnnualBudgetResponse)
async def annual_budget_detail_endpoint(
    annual_budget_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("annual_budgets.view"))],
) -> AnnualBudgetResponse:
    return await get_annual_budget(session, annual_budget_id=annual_budget_id)


@router.post(
    "/annual-budgets",
    response_model=AnnualBudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_annual_budget_endpoint(
    payload: AnnualBudgetCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("annual_budgets.create", require_all_scope=True)),
    ],
) -> AnnualBudgetResponse:
    return await create_annual_budget(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.patch("/annual-budgets/{annual_budget_id}", response_model=AnnualBudgetResponse)
async def update_annual_budget_endpoint(
    annual_budget_id: UUID,
    payload: AnnualBudgetUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("annual_budgets.update", require_all_scope=True)),
    ],
) -> AnnualBudgetResponse:
    return await update_annual_budget(
        session,
        annual_budget_id=annual_budget_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/annual-budgets/{annual_budget_id}/submit", response_model=AnnualBudgetResponse)
async def submit_annual_budget_endpoint(
    annual_budget_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("annual_budgets.submit", require_all_scope=True)),
    ],
) -> AnnualBudgetResponse:
    return await submit_annual_budget(
        session,
        annual_budget_id=annual_budget_id,
        actor_user_id=context.user.id,
    )


@router.get(
    "/annual-budgets/{annual_budget_id}/approvals",
    response_model=list[AnnualBudgetApprovalResponse],
)
async def annual_budget_approvals_endpoint(
    annual_budget_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("annual_budgets.view"))],
) -> list[AnnualBudgetApprovalResponse]:
    return await list_annual_budget_approvals(session, annual_budget_id=annual_budget_id)
