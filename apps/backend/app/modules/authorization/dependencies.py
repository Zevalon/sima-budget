from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import get_auth_context
from app.modules.auth.service import AuthContext
from app.modules.authorization.service import get_permission_scope_assignments


class RequirePermission:
    def __init__(self, permission_code: str, *, require_all_scope: bool = False) -> None:
        self.permission_code = permission_code
        self.require_all_scope = require_all_scope

    async def __call__(
        self,
        context: Annotated[AuthContext, Depends(get_auth_context)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> AuthContext:
        assignments = await get_permission_scope_assignments(
            session,
            user_id=context.user.id,
            permission_code=self.permission_code,
        )

        allowed = bool(assignments)
        if self.require_all_scope:
            allowed = any(assignment.scope_type == "ALL" for assignment in assignments)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki permission untuk operasi ini.",
            )
        return context
