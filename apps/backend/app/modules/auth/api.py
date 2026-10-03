from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.core.config import Settings, get_settings
from app.modules.auth.dependencies import get_auth_context, require_csrf
from app.modules.auth.schemas import CurrentUserResponse, LoginRequest, LoginResponse
from app.modules.auth.service import (
    AuthContext,
    build_current_user_response,
    login,
    logout,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login_endpoint(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponse:
    raw_token, result = await login(
        session,
        principal=payload.username,
        password=payload.password,
        settings=settings,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        path="/",
    )
    return result


@router.get("/me", response_model=CurrentUserResponse)
async def current_user_endpoint(
    context: Annotated[AuthContext, Depends(get_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CurrentUserResponse:
    return await build_current_user_response(
        session,
        user=context.user,
        user_session=context.user_session,
        raw_session_token=context.raw_session_token,
        settings=settings,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_endpoint(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    context: Annotated[AuthContext, Depends(require_csrf)],
) -> None:
    await logout(session, context=context)
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
    )
