import argparse
import asyncio
import getpass
import os

from sqlalchemy import select

from app.core.database import get_session_factory
from app.core.security import hash_password
from app.modules.audit.service import record_audit
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.users.models import User


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or repair the first SIMA administrator.")
    parser.add_argument("--username")
    parser.add_argument("--full-name")
    parser.add_argument("--email")
    parser.add_argument(
        "--reset-password",
        action="store_true",
        help="Allow resetting password when the username already exists.",
    )
    return parser.parse_args()


def read_value(current: str | None, prompt: str) -> str:
    if current:
        return current.strip()
    return input(prompt).strip()


def read_password() -> str:
    env_password = os.getenv("SIMA_BOOTSTRAP_ADMIN_PASSWORD")
    if env_password:
        password = env_password
    else:
        password = getpass.getpass("Password (minimal 12 karakter): ")
        confirmation = getpass.getpass("Ulangi password: ")
        if password != confirmation:
            raise SystemExit("Password confirmation does not match.")

    if len(password) < 12:
        raise SystemExit("Password minimal 12 karakter.")
    return password


async def bootstrap_admin(args: argparse.Namespace) -> None:
    username = read_value(args.username, "Username admin: ").lower()
    full_name = read_value(args.full_name, "Nama lengkap: ")
    email_input = args.email if args.email is not None else input("Email (boleh kosong): ")
    email = email_input.strip().lower() or None
    password = read_password()

    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        root_unit = (
            await session.scalar(
                select(OrganizationUnit).where(
                    OrganizationUnit.organization_id == organization.id,
                    OrganizationUnit.code == "ROOT",
                )
            )
            if organization
            else None
        )
        system_admin = (
            await session.scalar(
                select(Role).where(
                    Role.organization_id == organization.id,
                    Role.code == "SYSTEM_ADMIN",
                )
            )
            if organization
            else None
        )

        if organization is None or root_unit is None or system_admin is None:
            raise SystemExit(
                "Foundation data belum tersedia. Jalankan "
                "'make foundation-bootstrap' terlebih dahulu."
            )

        user = await session.scalar(select(User).where(User.username == username))
        if user is not None and not args.reset_password:
            raise SystemExit(
                "Username sudah ada. Gunakan --reset-password hanya jika memang ingin "
                "mengatur ulang password akun tersebut."
            )

        created = user is None
        if user is None:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                password_hash=hash_password(password),
                is_active=True,
                is_locked=False,
                failed_login_attempts=0,
            )
            session.add(user)
            await session.flush()
        else:
            user.full_name = full_name
            user.email = email
            user.password_hash = hash_password(password)
            user.is_active = True
            user.is_locked = False
            user.failed_login_attempts = 0
            user.locked_until = None

        membership = await session.scalar(
            select(UserUnitMembership).where(
                UserUnitMembership.user_id == user.id,
                UserUnitMembership.organization_unit_id == root_unit.id,
            )
        )
        if membership is None:
            session.add(
                UserUnitMembership(
                    user_id=user.id,
                    organization_unit_id=root_unit.id,
                    job_title="System Administrator",
                    is_primary=True,
                )
            )

        assignment = await session.scalar(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == user.id,
                UserRoleAssignment.role_id == system_admin.id,
                UserRoleAssignment.scope_type == "ALL",
            )
        )
        if assignment is None:
            session.add(
                UserRoleAssignment(
                    user_id=user.id,
                    role_id=system_admin.id,
                    scope_type="ALL",
                    scope_unit_id=None,
                )
            )

        record_audit(
            session,
            organization_id=organization.id,
            actor_user_id=user.id,
            action="ADMIN_BOOTSTRAP_CREATED" if created else "ADMIN_BOOTSTRAP_UPDATED",
            entity_type="user",
            entity_id=user.id,
        )
        await session.commit()

        action = "dibuat" if created else "diperbarui"
        print(f"System Administrator '{username}' berhasil {action}.")


async def main() -> None:
    await bootstrap_admin(parse_args())


if __name__ == "__main__":
    asyncio.run(main())
