from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.unit_allocations.schemas import (
    UnitAllocationCreateRequest,
    UnitAllocationOverviewResponse,
    UnitAllocationResponse,
    UnitAllocationUpdateRequest,
)
from app.modules.unit_allocations.service import (
    create_unit_allocation,
    get_unit_allocation_overview,
    update_unit_allocation,
)

router = APIRouter(tags=["unit-allocations"])


@router.get("/unit-allocations/overview", response_model=UnitAllocationOverviewResponse)
async def unit_allocation_overview_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("unit_allocations.view", require_all_scope=True)),
    ],
    fiscal_year_id: Annotated[UUID, Query()],
) -> UnitAllocationOverviewResponse:
    return await get_unit_allocation_overview(session, fiscal_year_id=fiscal_year_id)


@router.post(
    "/unit-allocations",
    response_model=UnitAllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_unit_allocation_endpoint(
    payload: UnitAllocationCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("unit_allocations.create", require_all_scope=True)),
    ],
) -> UnitAllocationResponse:
    return await create_unit_allocation(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.patch("/unit-allocations/{allocation_id}", response_model=UnitAllocationResponse)
async def update_unit_allocation_endpoint(
    allocation_id: UUID,
    payload: UnitAllocationUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("unit_allocations.update", require_all_scope=True)),
    ],
) -> UnitAllocationResponse:
    return await update_unit_allocation(
        session,
        allocation_id=allocation_id,
        payload=payload,
        actor_user_id=context.user.id,
    )
