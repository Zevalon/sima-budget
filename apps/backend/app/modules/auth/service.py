from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import (
    derive_csrf_token,
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_password,
)
from app.modules.audit.service import record_audit
from app.modules.auth.models import UserSession
from app.modules.auth.repository import (
    get_active_role_grants,
    get_default_organization,
    get_effective_permission_codes,
    get_session_and_user_by_token_hash,
    get_unit_memberships,
    get_user_by_principal,
    get_user_organization,
)
from app.modules.auth.schemas import (
    CurrentUserResponse,
    LoginResponse,
    RoleGrantResponse,
    UnitMembershipResponse,
)
from app.modules.settings.service import get_application_setting
from app.modules.users.models import User

_dummy_password_hash = hash_password("SIMA-DUMMY-PASSWORD-DO-NOT-USE")


@dataclass(slots=True)
class AuthContext:
    user: User
    user_session: UserSession
    raw_session_token: str


def _authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Username/email atau password tidak valid, atau akun tidak dapat digunakan.",
    )


async def login(
    session: AsyncSession,
    *,
    principal: str,
    password: str,
    settings: Settings,
    ip_address: str | None,
    user_agent: str | None,
) -> tuple[str, LoginResponse]:
    now = datetime.now(UTC)
    normalized = principal.strip().lower()
    user = await get_user_by_principal(session, normalized)

    if user is None:
        verify_password(_dummy_password_hash, password)
        organization = await get_default_organization(session)
        record_audit(
            session,
            organization_id=organization.id,
            action="LOGIN_FAILED",
            entity_type="auth",
            metadata_json={"principal": normalized},
        )
        await session.commit()
        raise _authentication_error()

    organization = await get_user_organization(session, user.id)

    if user.is_locked and user.locked_until is not None and user.locked_until <= now:
        user.is_locked = False
        user.locked_until = None
        user.failed_login_attempts = 0

    credentials_valid = (
        user.is_active and not user.is_locked and verify_password(user.password_hash, password)
    )

    if not credentials_valid:
        if user.is_active and not user.is_locked:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.auth_max_failed_attempts:
                user.is_locked = True
                user.locked_until = now + timedelta(seconds=settings.auth_lock_seconds)

        record_audit(
            session,
            organization_id=organization.id,
            actor_user_id=user.id,
            action="LOGIN_FAILED",
            entity_type="user",
            entity_id=user.id,
        )
        await session.commit()
        raise _authentication_error()

    user.failed_login_attempts = 0
    user.is_locked = False
    user.locked_until = None
    user.last_login_at = now

    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token, settings.session_secret)
    expires_at = now + timedelta(seconds=settings.session_ttl_seconds)

    user_session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked_at=None,
        last_seen_at=now,
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent else None,
        created_at=now,
    )
    session.add(user_session)

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=user.id,
        action="LOGIN_SUCCESS",
        entity_type="user",
        entity_id=user.id,
    )
    await session.commit()

    response = await build_current_user_response(
        session,
        user=user,
        user_session=user_session,
        raw_session_token=raw_token,
        settings=settings,
    )
    return raw_token, LoginResponse(**response.model_dump())


async def authenticate_session(
    session: AsyncSession,
    *,
    raw_session_token: str | None,
    settings: Settings,
) -> AuthContext:
    if not raw_session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session autentikasi tidak tersedia.",
        )

    token_hash = hash_session_token(raw_session_token, settings.session_secret)
    result = await get_session_and_user_by_token_hash(session, token_hash)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session tidak valid atau sudah berakhir.",
        )

    user_session, user = result
    now = datetime.now(UTC)

    if (
        user_session.revoked_at is not None
        or user_session.expires_at <= now
        or not user.is_active
        or user.is_locked
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session tidak valid atau sudah berakhir.",
        )

    return AuthContext(
        user=user,
        user_session=user_session,
        raw_session_token=raw_session_token,
    )


async def build_current_user_response(
    session: AsyncSession,
    *,
    user: User,
    user_session: UserSession,
    raw_session_token: str,
    settings: Settings,
) -> CurrentUserResponse:
    now = datetime.now(UTC)
    organization = await get_user_organization(session, user.id)
    application_setting = await get_application_setting(session)
    role_rows = await get_active_role_grants(session, user.id, now)
    permissions = await get_effective_permission_codes(session, user.id, now)
    memberships = await get_unit_memberships(session, user.id)

    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        organization_id=organization.id,
        organization_name=organization.name,
        application_name=application_setting.application_name,
        application_short_name=application_setting.application_short_name,
        organization_display_name=application_setting.organization_display_name,
        roles=[
            RoleGrantResponse(
                role_code=role.code,
                role_name=role.name,
                scope_type=assignment.scope_type,
                scope_unit_id=assignment.scope_unit_id,
            )
            for role, assignment in role_rows
        ],
        permissions=permissions,
        unit_memberships=[
            UnitMembershipResponse(
                unit_id=unit.id,
                unit_code=unit.code,
                unit_name=unit.name,
                job_title=membership.job_title,
                is_primary=membership.is_primary,
            )
            for membership, unit in memberships
        ],
        session_expires_at=user_session.expires_at,
        csrf_token=derive_csrf_token(raw_session_token, settings.csrf_secret),
    )


async def logout(
    session: AsyncSession,
    *,
    context: AuthContext,
) -> None:
    now = datetime.now(UTC)
    organization = await get_user_organization(session, context.user.id)
    context.user_session.revoked_at = now

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=context.user.id,
        action="LOGOUT",
        entity_type="user",
        entity_id=context.user.id,
    )
    await session.commit()
