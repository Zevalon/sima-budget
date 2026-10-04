from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.budget_plans.schemas import (
    BudgetPlanApprovalResponse,
    BudgetPlanApproveRequest,
    BudgetPlanContextResponse,
    BudgetPlanCreateRequest,
    BudgetPlanPendingApprovalResponse,
    BudgetPlanRejectRequest,
    BudgetPlanResponse,
    BudgetPlanRevisionRequest,
    BudgetPlanUpdateRequest,
)
from app.modules.budget_plans.service import (
    approve_budget_plan,
    create_budget_plan,
    get_budget_plan,
    get_budget_plan_context,
    list_budget_plan_approvals,
    list_budget_plans,
    list_pending_budget_plan_approvals,
    reject_budget_plan,
    revise_budget_plan,
    submit_budget_plan,
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


@router.get(
    "/budget-plan-approvals/pending",
    response_model=list[BudgetPlanPendingApprovalResponse],
)
async def pending_budget_plan_approvals_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("budget_plans.approve"))],
    fiscal_year_id: Annotated[UUID | None, Query()] = None,
) -> list[BudgetPlanPendingApprovalResponse]:
    return await list_pending_budget_plan_approvals(
        session,
        user_id=context.user.id,
        fiscal_year_id=fiscal_year_id,
    )


@router.get("/budget-plans/{plan_id}", response_model=BudgetPlanResponse)
async def get_budget_plan_endpoint(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("budget_plans.view"))],
) -> BudgetPlanResponse:
    return await get_budget_plan(session, plan_id=plan_id, user_id=context.user.id)


@router.get(
    "/budget-plans/{plan_id}/approvals",
    response_model=list[BudgetPlanApprovalResponse],
)
async def budget_plan_approvals_endpoint(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("budget_plans.view"))],
) -> list[BudgetPlanApprovalResponse]:
    return await list_budget_plan_approvals(
        session,
        plan_id=plan_id,
        user_id=context.user.id,
    )


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


@router.post("/budget-plans/{plan_id}/submit", response_model=BudgetPlanResponse)
async def submit_budget_plan_endpoint(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_plans.submit"))],
) -> BudgetPlanResponse:
    return await submit_budget_plan(session, plan_id=plan_id, actor_user_id=context.user.id)


@router.post("/budget-plans/{plan_id}/approve", response_model=BudgetPlanResponse)
async def approve_budget_plan_endpoint(
    plan_id: UUID,
    payload: BudgetPlanApproveRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_plans.approve"))],
) -> BudgetPlanResponse:
    return await approve_budget_plan(
        session,
        plan_id=plan_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/budget-plans/{plan_id}/reject", response_model=BudgetPlanResponse)
async def reject_budget_plan_endpoint(
    plan_id: UUID,
    payload: BudgetPlanRejectRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_plans.approve"))],
) -> BudgetPlanResponse:
    return await reject_budget_plan(
        session,
        plan_id=plan_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/budget-plans/{plan_id}/revise", response_model=BudgetPlanResponse)
async def revise_budget_plan_endpoint(
    plan_id: UUID,
    payload: BudgetPlanRevisionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_plans.revise"))],
) -> BudgetPlanResponse:
    return await revise_budget_plan(
        session,
        plan_id=plan_id,
        payload=payload,
        actor_user_id=context.user.id,
    )
