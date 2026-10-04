from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import record_audit
from app.modules.organizations.models import Organization
from app.modules.settings.models import ApplicationSetting
from app.modules.settings.schemas import (
    ApplicationSettingResponse,
    ApplicationSettingUpdateRequest,
)


async def get_default_organization(session: AsyncSession) -> Organization:
    organization = await session.scalar(select(Organization).where(Organization.code == "DEFAULT"))
    if organization is None:
        raise RuntimeError("Default organization belum tersedia.")
    return organization


async def get_application_setting(session: AsyncSession) -> ApplicationSetting:
    organization = await get_default_organization(session)
    setting = await session.scalar(
        select(ApplicationSetting).where(ApplicationSetting.organization_id == organization.id)
    )
    if setting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengaturan aplikasi belum tersedia.",
        )
    return setting


def to_response(setting: ApplicationSetting) -> ApplicationSettingResponse:
    return ApplicationSettingResponse(
        application_name=setting.application_name,
        application_short_name=setting.application_short_name,
        organization_display_name=setting.organization_display_name,
        primary_color=setting.primary_color,
        secondary_color=setting.secondary_color,
        currency_code=setting.currency_code,
        timezone=setting.timezone,
        date_format=setting.date_format,
        allow_annual_budget_revision=setting.allow_annual_budget_revision,
        allow_budget_transfer=setting.allow_budget_transfer,
        allow_self_approval=setting.allow_self_approval,
    )


async def update_application_setting(
    session: AsyncSession,
    *,
    payload: ApplicationSettingUpdateRequest,
    actor_user_id: UUID,
) -> ApplicationSettingResponse:
    organization = await get_default_organization(session)
    setting = await get_application_setting(session)

    before = to_response(setting).model_dump()
    updates: dict[str, Any] = payload.model_dump(exclude_unset=True)

    for field_name, value in updates.items():
        if field_name in {"currency_code"} and isinstance(value, str):
            value = value.upper()
        if isinstance(value, str):
            value = value.strip()
        setattr(setting, field_name, value)

    after = to_response(setting).model_dump()

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="APPLICATION_SETTINGS_UPDATED",
        entity_type="application_setting",
        entity_id=setting.id,
        before_data=before,
        after_data=after,
    )
    await session.commit()
    return to_response(setting)
