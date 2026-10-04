from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.realizations.schemas import (
    RealizationContextResponse,
    RealizationCorrectionRequest,
    RealizationCreateRequest,
    RealizationPostRequest,
    RealizationResponse,
    RealizationStatusActionRequest,
    RealizationUpdateRequest,
)
from app.modules.realizations.service import (
    cancel_realization,
    create_correction_draft,
    create_realization,
    get_realization,
    get_realization_context,
    list_realizations,
    post_realization,
    reverse_realization,
    update_realization,
)

router = APIRouter(tags=["realizations"])


@router.get("/realizations/context", response_model=RealizationContextResponse)
async def realization_context_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("realizations.view"))],
    fiscal_year_id: Annotated[UUID, Query()],
) -> RealizationContextResponse:
    return await get_realization_context(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
    )


@router.get("/realizations", response_model=list[RealizationResponse])
async def realizations_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("realizations.view"))],
    fiscal_year_id: Annotated[UUID, Query()],
) -> list[RealizationResponse]:
    return await list_realizations(
        session,
        fiscal_year_id=fiscal_year_id,
        user_id=context.user.id,
    )


@router.get("/realizations/{realization_id}", response_model=RealizationResponse)
async def realization_detail_endpoint(
    realization_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(RequirePermission("realizations.view"))],
) -> RealizationResponse:
    return await get_realization(
        session,
        realization_id=realization_id,
        user_id=context.user.id,
    )


@router.post(
    "/realizations",
    response_model=RealizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_realization_endpoint(
    payload: RealizationCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("realizations.create"))],
) -> RealizationResponse:
    return await create_realization(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.patch("/realizations/{realization_id}", response_model=RealizationResponse)
async def update_realization_endpoint(
    realization_id: UUID,
    payload: RealizationUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("realizations.update"))],
) -> RealizationResponse:
    return await update_realization(
        session,
        realization_id=realization_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/realizations/{realization_id}/post", response_model=RealizationResponse)
async def post_realization_endpoint(
    realization_id: UUID,
    payload: RealizationPostRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("realizations.post"))],
) -> RealizationResponse:
    return await post_realization(
        session,
        realization_id=realization_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/realizations/{realization_id}/cancel", response_model=RealizationResponse)
async def cancel_realization_endpoint(
    realization_id: UUID,
    payload: RealizationStatusActionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("realizations.cancel"))],
) -> RealizationResponse:
    return await cancel_realization(
        session,
        realization_id=realization_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post("/realizations/{realization_id}/reverse", response_model=RealizationResponse)
async def reverse_realization_endpoint(
    realization_id: UUID,
    payload: RealizationStatusActionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("realizations.reverse"))],
) -> RealizationResponse:
    return await reverse_realization(
        session,
        realization_id=realization_id,
        payload=payload,
        actor_user_id=context.user.id,
    )


@router.post(
    "/realizations/{realization_id}/correction",
    response_model=RealizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_correction_draft_endpoint(
    realization_id: UUID,
    payload: RealizationCorrectionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[AuthContext, Depends(RequirePermission("realizations.create"))],
) -> RealizationResponse:
    return await create_correction_draft(
        session,
        realization_id=realization_id,
        payload=payload,
        actor_user_id=context.user.id,
    )
