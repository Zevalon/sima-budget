from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.budget_foundation.schemas import (
    BudgetCategoryCreateRequest,
    BudgetCategoryResponse,
    BudgetCategoryUpdateRequest,
    FiscalYearCreateRequest,
    FiscalYearReopenRequest,
    FiscalYearResponse,
    FiscalYearTransitionRequest,
    FiscalYearUpdateRequest,
    UnitOfMeasureCreateRequest,
    UnitOfMeasureResponse,
    UnitOfMeasureUpdateRequest,
)
from app.modules.budget_foundation.service import (
    create_budget_category,
    create_fiscal_year,
    create_unit_of_measure,
    deactivate_budget_category,
    deactivate_unit_of_measure,
    list_budget_categories,
    list_fiscal_years,
    list_units_of_measure,
    reopen_fiscal_year,
    transition_fiscal_year,
    update_budget_category,
    update_fiscal_year,
    update_unit_of_measure,
)

router = APIRouter(tags=["budget-foundation"])


@router.get("/fiscal-years", response_model=list[FiscalYearResponse])
async def fiscal_years_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("fiscal_years.view"))],
) -> list[FiscalYearResponse]:
    return await list_fiscal_years(session)


@router.post(
    "/fiscal-years",
    response_model=FiscalYearResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_fiscal_year_endpoint(
    payload: FiscalYearCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("fiscal_years.create", require_all_scope=True)),
    ],
) -> FiscalYearResponse:
    return await create_fiscal_year(session, payload=payload, actor_user_id=context.user.id)


@router.patch("/fiscal-years/{fiscal_year_id}", response_model=FiscalYearResponse)
async def update_fiscal_year_endpoint(
    fiscal_year_id: UUID,
    payload: FiscalYearUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("fiscal_years.update", require_all_scope=True)),
    ],
) -> FiscalYearResponse:
    return await update_fiscal_year(
        session,
        fiscal_year_id=fiscal_year_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post(
    "/fiscal-years/{fiscal_year_id}/transition",
    response_model=FiscalYearResponse,
)
async def transition_fiscal_year_endpoint(
    fiscal_year_id: UUID,
    payload: FiscalYearTransitionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("fiscal_years.transition", require_all_scope=True)),
    ],
) -> FiscalYearResponse:
    return await transition_fiscal_year(
        session,
        fiscal_year_id=fiscal_year_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post(
    "/fiscal-years/{fiscal_year_id}/reopen",
    response_model=FiscalYearResponse,
)
async def reopen_fiscal_year_endpoint(
    fiscal_year_id: UUID,
    payload: FiscalYearReopenRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("fiscal_years.reopen", require_all_scope=True)),
    ],
) -> FiscalYearResponse:
    return await reopen_fiscal_year(
        session,
        fiscal_year_id=fiscal_year_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.get("/master-data/budget-categories", response_model=list[BudgetCategoryResponse])
async def budget_categories_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("budget_categories.view"))],
) -> list[BudgetCategoryResponse]:
    return await list_budget_categories(session)


@router.post(
    "/master-data/budget-categories",
    response_model=BudgetCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget_category_endpoint(
    payload: BudgetCategoryCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("budget_categories.manage", require_all_scope=True)),
    ],
) -> BudgetCategoryResponse:
    return await create_budget_category(session, payload=payload, actor_user_id=context.user.id)


@router.patch(
    "/master-data/budget-categories/{category_id}",
    response_model=BudgetCategoryResponse,
)
async def update_budget_category_endpoint(
    category_id: UUID,
    payload: BudgetCategoryUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("budget_categories.manage", require_all_scope=True)),
    ],
) -> BudgetCategoryResponse:
    return await update_budget_category(
        session,
        category_id=category_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post(
    "/master-data/budget-categories/{category_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_budget_category_endpoint(
    category_id: UUID,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("budget_categories.manage", require_all_scope=True)),
    ],
) -> None:
    await deactivate_budget_category(
        session, category_id=category_id, actor_user_id=context.user.id
    )
    response.status_code = status.HTTP_204_NO_CONTENT


@router.get("/master-data/units-of-measure", response_model=list[UnitOfMeasureResponse])
async def units_of_measure_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("units_of_measure.view"))],
) -> list[UnitOfMeasureResponse]:
    return await list_units_of_measure(session)


@router.post(
    "/master-data/units-of-measure",
    response_model=UnitOfMeasureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_unit_of_measure_endpoint(
    payload: UnitOfMeasureCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("units_of_measure.manage", require_all_scope=True)),
    ],
) -> UnitOfMeasureResponse:
    return await create_unit_of_measure(session, payload=payload, actor_user_id=context.user.id)


@router.patch(
    "/master-data/units-of-measure/{unit_id}",
    response_model=UnitOfMeasureResponse,
)
async def update_unit_of_measure_endpoint(
    unit_id: UUID,
    payload: UnitOfMeasureUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("units_of_measure.manage", require_all_scope=True)),
    ],
) -> UnitOfMeasureResponse:
    return await update_unit_of_measure(
        session, unit_id=unit_id, payload=payload, actor_user_id=context.user.id
    )


@router.post(
    "/master-data/units-of-measure/{unit_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_unit_of_measure_endpoint(
    unit_id: UUID,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("units_of_measure.manage", require_all_scope=True)),
    ],
) -> None:
    await deactivate_unit_of_measure(session, unit_id=unit_id, actor_user_id=context.user.id)
    response.status_code = status.HTTP_204_NO_CONTENT
