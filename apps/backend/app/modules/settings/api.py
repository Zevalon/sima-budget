from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.modules.auth.dependencies import require_csrf
from app.modules.auth.service import AuthContext
from app.modules.authorization.dependencies import RequirePermission
from app.modules.settings.schemas import (
    ApplicationSettingResponse,
    ApplicationSettingUpdateRequest,
)
from app.modules.settings.service import (
    get_application_setting,
    to_response,
    update_application_setting,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=ApplicationSettingResponse)
async def settings_endpoint(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[AuthContext, Depends(RequirePermission("settings.view"))],
) -> ApplicationSettingResponse:
    setting = await get_application_setting(session)
    return to_response(setting)


@router.patch("", response_model=ApplicationSettingResponse)
async def update_settings_endpoint(
    payload: ApplicationSettingUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    context: Annotated[AuthContext, Depends(require_csrf)],
    _: Annotated[
        AuthContext,
        Depends(RequirePermission("settings.update", require_all_scope=True)),
    ],
) -> ApplicationSettingResponse:
    return await update_application_setting(
        session,
        payload=payload,
        actor_user_id=context.user.id,
    )
