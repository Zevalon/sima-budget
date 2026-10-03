from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.core.config import Settings, get_settings
from app.core.security import csrf_token_matches
from app.modules.auth.service import AuthContext, authenticate_session


async def get_auth_context(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthContext:
    return await authenticate_session(
        session,
        raw_session_token=request.cookies.get(settings.session_cookie_name),
        settings=settings,
    )


async def require_csrf(
    context: Annotated[AuthContext, Depends(get_auth_context)],
    settings: Annotated[Settings, Depends(get_settings)],
    csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> AuthContext:
    if csrf_token is None or not csrf_token_matches(
        context.raw_session_token,
        csrf_token,
        settings.csrf_secret,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token tidak valid.",
        )
    return context
