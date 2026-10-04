from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.modules.audit.models import AuditLog
from app.modules.audit.schemas import AuditLogItem, AuditLogPage
from app.modules.users.models import User


async def list_audit_logs(
    session: AsyncSession,
    *,
    limit: int,
    offset: int,
    action: str | None,
    entity_type: str | None,
) -> AuditLogPage:
    filters: list[ColumnElement[bool]] = []

    if action:
        filters.append(AuditLog.action.ilike(f"%{action.strip()}%"))
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type.strip())

    total = await session.scalar(select(func.count(AuditLog.id)).where(*filters))
    rows = (
        await session.execute(
            select(AuditLog, User)
            .outerjoin(User, User.id == AuditLog.actor_user_id)
            .where(*filters)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()

    return AuditLogPage(
        items=[
            AuditLogItem(
                id=event.id,
                actor_user_id=event.actor_user_id,
                actor_username=user.username if user else None,
                actor_full_name=user.full_name if user else None,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                before_data=event.before_data,
                after_data=event.after_data,
                metadata=event.metadata_json,
                created_at=event.created_at,
            )
            for event, user in rows
        ],
        total=total or 0,
        limit=limit,
        offset=offset,
    )
