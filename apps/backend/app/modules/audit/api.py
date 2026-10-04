from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.audit.repository import list_audit_logs
from app.modules.audit.schemas import AuditLogPage
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditLogPage)
async def audit_logs_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("audit.view"))],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    action: str | None = None,
    entity_type: str | None = None,
) -> AuditLogPage:
    return await list_audit_logs(
        session,
        limit=limit,
        offset=offset,
        action=action,
        entity_type=entity_type,
    )
