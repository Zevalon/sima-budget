from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import get_auth_context
from app.modules.auth.service import AuthContext
from app.modules.authorization.service import has_permission


class RequirePermission:
    def __init__(self, permission_code: str) -> None:
        self.permission_code = permission_code

    async def __call__(
        self,
        context: Annotated[AuthContext, Depends(get_auth_context)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> AuthContext:
        allowed = await has_permission(
            session,
            user_id=context.user.id,
            permission_code=self.permission_code,
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki permission untuk operasi ini.",
            )
        return context
