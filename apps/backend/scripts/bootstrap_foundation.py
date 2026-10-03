import asyncio

from sqlalchemy import select

from app.core.database import get_session_factory
from app.modules.organizations.bootstrap_data import DEFAULT_UNIT_TYPES
from app.modules.organizations.models import Organization, OrganizationUnit, OrganizationUnitType
from app.modules.roles.bootstrap_data import DEFAULT_ROLE_TEMPLATES, FOUNDATION_PERMISSIONS
from app.modules.roles.models import Permission, Role, RolePermission
from app.modules.settings.models import ApplicationSetting


async def ensure_organization() -> Organization:
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            organization = Organization(
                code="DEFAULT",
                name="Universitas / Organisasi",
                legal_name=None,
                is_active=True,
            )
            session.add(organization)
            await session.flush()

        settings = await session.scalar(
            select(ApplicationSetting).where(ApplicationSetting.organization_id == organization.id)
        )
        if settings is None:
            session.add(
                ApplicationSetting(
                    organization_id=organization.id,
                    application_name="SIMA",
                    application_short_name="SIMA",
                    organization_display_name=organization.name,
                    currency_code="IDR",
                    timezone="Asia/Jakarta",
                    date_format="DD/MM/YYYY",
                )
            )

        unit_types_by_code: dict[str, OrganizationUnitType] = {}
        for code, name, sort_order in DEFAULT_UNIT_TYPES:
            unit_type = await session.scalar(
                select(OrganizationUnitType).where(
                    OrganizationUnitType.organization_id == organization.id,
                    OrganizationUnitType.code == code,
                )
            )
            if unit_type is None:
                unit_type = OrganizationUnitType(
                    organization_id=organization.id,
                    code=code,
                    name=name,
                    sort_order=sort_order,
                    is_active=True,
                )
                session.add(unit_type)
                await session.flush()
            unit_types_by_code[code] = unit_type

        root_unit = await session.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.code == "ROOT",
            )
        )
        if root_unit is None:
            session.add(
                OrganizationUnit(
                    organization_id=organization.id,
                    unit_type_id=unit_types_by_code["UNIVERSITY"].id,
                    parent_id=None,
                    code="ROOT",
                    name=organization.name,
                    can_receive_budget=False,
                    can_create_budget_plan=False,
                    is_active=True,
                )
            )

        permissions_by_code: dict[str, Permission] = {}
        for code, name, module in FOUNDATION_PERMISSIONS:
            permission = await session.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, name=name, module=module)
                session.add(permission)
                await session.flush()
            permissions_by_code[code] = permission

        for code, name, description, permission_codes in DEFAULT_ROLE_TEMPLATES:
            role = await session.scalar(
                select(Role).where(
                    Role.organization_id == organization.id,
                    Role.code == code,
                )
            )
            if role is None:
                role = Role(
                    organization_id=organization.id,
                    code=code,
                    name=name,
                    description=description,
                    is_system_role=True,
                    is_active=True,
                )
                session.add(role)
                await session.flush()

            existing_permission_ids = set(
                (
                    await session.scalars(
                        select(RolePermission.permission_id).where(
                            RolePermission.role_id == role.id
                        )
                    )
                ).all()
            )
            for permission_code in permission_codes:
                permission = permissions_by_code[permission_code]
                if permission.id not in existing_permission_ids:
                    session.add(
                        RolePermission(
                            role_id=role.id,
                            permission_id=permission.id,
                        )
                    )

        await session.commit()
        return organization


async def main() -> None:
    organization = await ensure_organization()
    print(f"Foundation bootstrap complete for organization: {organization.code}")


if __name__ == "__main__":
    asyncio.run(main())
