import asyncio

from sqlalchemy import inspect, select

from app.core.database import get_engine, get_session_factory
from app.modules.organizations.models import Organization, OrganizationUnit, OrganizationUnitType
from app.modules.roles.models import Permission, Role
from app.modules.settings.models import ApplicationSetting

EXPECTED_TABLES = {
    "organizations",
    "application_settings",
    "organization_unit_types",
    "organization_units",
    "users",
    "user_unit_memberships",
    "roles",
    "permissions",
    "role_permissions",
    "user_role_assignments",
    "user_sessions",
    "audit_logs",
}


async def get_table_names() -> set[str]:
    async with get_engine().connect() as connection:
        names = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )
    return set(names)


async def main() -> None:
    tables = await get_table_names()
    missing = EXPECTED_TABLES - tables
    if missing:
        raise SystemExit(f"Missing foundation tables: {sorted(missing)}")

    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            raise SystemExit("Default organization was not bootstrapped.")

        settings = await session.scalar(
            select(ApplicationSetting).where(ApplicationSetting.organization_id == organization.id)
        )
        if settings is None:
            raise SystemExit("Application settings were not bootstrapped.")

        unit_type_count = len(
            (
                await session.scalars(
                    select(OrganizationUnitType).where(
                        OrganizationUnitType.organization_id == organization.id
                    )
                )
            ).all()
        )
        root_unit = await session.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.code == "ROOT",
            )
        )
        role_count = len(
            (
                await session.scalars(select(Role).where(Role.organization_id == organization.id))
            ).all()
        )
        permission_count = len((await session.scalars(select(Permission))).all())

        if unit_type_count < 8:
            raise SystemExit(f"Expected at least 8 unit types, found {unit_type_count}.")
        if root_unit is None:
            raise SystemExit("Root organization unit was not bootstrapped.")
        if role_count < 7:
            raise SystemExit(f"Expected at least 7 default roles, found {role_count}.")
        if permission_count < 17:
            raise SystemExit(
                f"Expected at least 17 foundation permissions, found {permission_count}."
            )

        print(
            "Foundation verification: OK "
            f"(tables={len(EXPECTED_TABLES)}, unit_types={unit_type_count}, "
            f"roles={role_count}, permissions={permission_count})"
        )


if __name__ == "__main__":
    asyncio.run(main())
