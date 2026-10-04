from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.budget_plans.schemas import (
    BudgetPlanContextResponse,
    BudgetPlanCreateRequest,
    BudgetPlanResponse,
    BudgetPlanUpdateRequest,
)
from app.modules.budget_plans.service import (
    create_budget_plan,
    get_budget_plan,
    get_budget_plan_context,
    list_budget_plans,
    update_budget_plan,
)

router = APIRouter(tags=["budget-plans"])


@router.get("/budget-plans/context", response_model=BudgetPlanContextResponse)
async def budget_plan_context_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("budget_plans.view"))],
    fiscal_year_id: Annotated[UUID, Query()],
) -> BudgetPlanContextResponse:
    return await get_budget_plan_context(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
    )


@router.get("/budget-plans", response_model=list[BudgetPlanResponse])
async def list_budget_plans_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("budget_plans.view"))],
    fiscal_year_id: Annotated[UUID, Query()],
) -> list[BudgetPlanResponse]:
    return await list_budget_plans(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
    )


@router.get("/budget-plans/{plan_id}", response_model=BudgetPlanResponse)
async def get_budget_plan_endpoint(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("budget_plans.view"))],
) -> BudgetPlanResponse:
    return await get_budget_plan(session, plan_id=plan_id, user_id=context.user.id)


@router.post(
    "/budget-plans",
    response_model=BudgetPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget_plan_endpoint(
    payload: BudgetPlanCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_plans.create"))],
) -> BudgetPlanResponse:
    return await create_budget_plan(session, payload=payload, actor_user_id=context.user.id)


@router.patch("/budget-plans/{plan_id}", response_model=BudgetPlanResponse)
async def update_budget_plan_endpoint(
    plan_id: UUID,
    payload: BudgetPlanUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_plans.update"))],
) -> BudgetPlanResponse:
    return await update_budget_plan(
        session,
        plan_id=plan_id,
        payload=payload,
        actor_user_id=context.user.id,
    )
