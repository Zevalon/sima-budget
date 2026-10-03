from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


def record_audit(
    session: AsyncSession,
    *,
    organization_id: UUID,
    action: str,
    entity_type: str,
    actor_user_id: UUID | None = None,
    entity_id: UUID | None = None,
    before_data: dict[str, Any] | None = None,
    after_data: dict[str, Any] | None = None,
    metadata_json: dict[str, Any] | None = None,
) -> AuditLog:
    event = AuditLog(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_data=before_data,
        after_data=after_data,
        metadata_json=metadata_json,
    )
    session.add(event)
    return event
