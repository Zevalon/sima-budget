import asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.core.database import get_engine, get_session_factory
from app.core.security import hash_password
from app.main import app
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.organizations.models import Organization, OrganizationUnit, UserUnitMembership
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.users.models import User

USERNAME = "phase2a_budget_admin"
PASSWORD = "Phase2A-Verification!"
FISCAL_CODES = ("P2A-2198", "P2A-2199")
CATEGORY_CODE = "P2A-CAT"
UOM_CODE = "P2A-UOM"


async def cleanup() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await session.scalar(select(User).where(User.username == USERNAME))
        fiscal_years = (
            await session.scalars(select(FiscalYear).where(FiscalYear.code.in_(FISCAL_CODES)))
        ).all()
        category = await session.scalar(
            select(BudgetCategory).where(BudgetCategory.code == CATEGORY_CODE)
        )
        uom = await session.scalar(select(UnitOfMeasure).where(UnitOfMeasure.code == UOM_CODE))

        entity_ids = [item.id for item in fiscal_years]
        if category is not None:
            entity_ids.append(category.id)
        if uom is not None:
            entity_ids.append(uom.id)

        if user is not None:
            await session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user.id))
            await session.execute(delete(UserSession).where(UserSession.user_id == user.id))
            await session.execute(
                delete(UserRoleAssignment).where(UserRoleAssignment.user_id == user.id)
            )
            await session.execute(
                delete(UserUnitMembership).where(UserUnitMembership.user_id == user.id)
            )

        if entity_ids:
            await session.execute(delete(AuditLog).where(AuditLog.entity_id.in_(entity_ids)))

        if fiscal_years:
            await session.execute(delete(FiscalYear).where(FiscalYear.id.in_(entity_ids)))
        if category is not None:
            await session.delete(category)
        if uom is not None:
            await session.delete(uom)
        if user is not None:
            await session.delete(user)

        await session.commit()


async def create_budget_admin() -> None:
    await cleanup()
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            raise RuntimeError("Default organization belum tersedia.")

        root_unit = await session.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.code == "ROOT",
            )
        )
        budget_admin = await session.scalar(
            select(Role).where(
                Role.organization_id == organization.id,
                Role.code == "BUDGET_ADMIN",
            )
        )
        if root_unit is None or budget_admin is None:
            raise RuntimeError("Phase 2A foundation bootstrap belum tersedia.")

        user = User(
            username=USERNAME,
            email=None,
            full_name="Phase 2A Budget Admin",
            password_hash=hash_password(PASSWORD),
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        session.add(user)
        await session.flush()
        session.add(
            UserUnitMembership(
                user_id=user.id,
                organization_unit_id=root_unit.id,
                job_title="Verification",
                is_primary=True,
            )
        )
        session.add(
            UserRoleAssignment(
                user_id=user.id,
                role_id=budget_admin.id,
                scope_type="ALL",
                scope_unit_id=None,
            )
        )
        await session.commit()


async def verify() -> None:
    await create_budget_admin()
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://localhost",
        follow_redirects=True,
    ) as client:
        login = await client.post(
            "/api/v1/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
        )
        assert login.status_code == 200, login.text
        login_data = login.json()
        csrf = login_data["csrf_token"]
        permissions = set(login_data["permissions"])
        required_permissions = {
            "fiscal_years.view",
            "fiscal_years.create",
            "fiscal_years.update",
            "fiscal_years.transition",
            "fiscal_years.reopen",
            "budget_categories.view",
            "budget_categories.manage",
            "units_of_measure.view",
            "units_of_measure.manage",
        }
        assert required_permissions <= permissions
        headers = {"X-CSRF-Token": csrf}

        no_csrf = await client.post(
            "/api/v1/fiscal-years",
            json={
                "code": FISCAL_CODES[0],
                "year": 2198,
                "start_date": "2198-01-01",
                "end_date": "2198-12-31",
            },
        )
        assert no_csrf.status_code == 403, no_csrf.text

        fy1 = await client.post(
            "/api/v1/fiscal-years",
            headers=headers,
            json={
                "code": FISCAL_CODES[0],
                "year": 2198,
                "start_date": "2198-01-01",
                "end_date": "2198-12-31",
            },
        )
        assert fy1.status_code == 201, fy1.text
        fy1_id = fy1.json()["id"]
        assert fy1.json()["status"] == "DRAFT"

        updated = await client.patch(
            f"/api/v1/fiscal-years/{fy1_id}",
            headers=headers,
            json={"code": "p2a-2198"},
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["code"] == FISCAL_CODES[0]

        planning1 = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/transition",
            headers=headers,
            json={"target_status": "PLANNING"},
        )
        assert planning1.status_code == 200, planning1.text
        active1 = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/transition",
            headers=headers,
            json={"target_status": "ACTIVE"},
        )
        assert active1.status_code == 200, active1.text

        fy2 = await client.post(
            "/api/v1/fiscal-years",
            headers=headers,
            json={
                "code": FISCAL_CODES[1],
                "year": 2199,
                "start_date": "2199-01-01",
                "end_date": "2199-12-31",
            },
        )
        assert fy2.status_code == 201, fy2.text
        fy2_id = fy2.json()["id"]
        planning2 = await client.post(
            f"/api/v1/fiscal-years/{fy2_id}/transition",
            headers=headers,
            json={"target_status": "PLANNING"},
        )
        assert planning2.status_code == 200, planning2.text

        second_active = await client.post(
            f"/api/v1/fiscal-years/{fy2_id}/transition",
            headers=headers,
            json={"target_status": "ACTIVE"},
        )
        assert second_active.status_code == 409, second_active.text

        close1 = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/transition",
            headers=headers,
            json={"target_status": "CLOSED", "reason": "Verification close"},
        )
        assert close1.status_code == 200, close1.text

        activate2 = await client.post(
            f"/api/v1/fiscal-years/{fy2_id}/transition",
            headers=headers,
            json={"target_status": "ACTIVE"},
        )
        assert activate2.status_code == 200, activate2.text

        reopen_conflict = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/reopen",
            headers=headers,
            json={"reason": "Verification reopen while another year is active"},
        )
        assert reopen_conflict.status_code == 409, reopen_conflict.text

        close2 = await client.post(
            f"/api/v1/fiscal-years/{fy2_id}/transition",
            headers=headers,
            json={"target_status": "CLOSED"},
        )
        assert close2.status_code == 200, close2.text

        reopened = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/reopen",
            headers=headers,
            json={"reason": "Verification controlled reopen"},
        )
        assert reopened.status_code == 200, reopened.text
        assert reopened.json()["status"] == "ACTIVE"
        assert reopened.json()["reopen_reason"] == "Verification controlled reopen"

        close_again = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/transition",
            headers=headers,
            json={"target_status": "CLOSED"},
        )
        assert close_again.status_code == 200, close_again.text
        archive1 = await client.post(
            f"/api/v1/fiscal-years/{fy1_id}/transition",
            headers=headers,
            json={"target_status": "ARCHIVED"},
        )
        assert archive1.status_code == 200, archive1.text
        archive2 = await client.post(
            f"/api/v1/fiscal-years/{fy2_id}/transition",
            headers=headers,
            json={"target_status": "ARCHIVED"},
        )
        assert archive2.status_code == 200, archive2.text

        category = await client.post(
            "/api/v1/master-data/budget-categories",
            headers=headers,
            json={
                "code": CATEGORY_CODE,
                "name": "Phase 2A Verification Category",
                "description": "Temporary verification data",
            },
        )
        assert category.status_code == 201, category.text
        category_id = category.json()["id"]
        duplicate_category = await client.post(
            "/api/v1/master-data/budget-categories",
            headers=headers,
            json={"code": CATEGORY_CODE, "name": "Duplicate"},
        )
        assert duplicate_category.status_code == 409, duplicate_category.text
        updated_category = await client.patch(
            f"/api/v1/master-data/budget-categories/{category_id}",
            headers=headers,
            json={"name": "Phase 2A Category Updated"},
        )
        assert updated_category.status_code == 200, updated_category.text
        deactivate_category = await client.post(
            f"/api/v1/master-data/budget-categories/{category_id}/deactivate",
            headers=headers,
        )
        assert deactivate_category.status_code == 204, deactivate_category.text

        uom = await client.post(
            "/api/v1/master-data/units-of-measure",
            headers=headers,
            json={"code": UOM_CODE, "name": "Unit Verification"},
        )
        assert uom.status_code == 201, uom.text
        uom_id = uom.json()["id"]
        updated_uom = await client.patch(
            f"/api/v1/master-data/units-of-measure/{uom_id}",
            headers=headers,
            json={"name": "Unit Verification Updated"},
        )
        assert updated_uom.status_code == 200, updated_uom.text
        deactivate_uom = await client.post(
            f"/api/v1/master-data/units-of-measure/{uom_id}/deactivate",
            headers=headers,
        )
        assert deactivate_uom.status_code == 204, deactivate_uom.text

        audit_api = await client.get(
            "/api/v1/audit",
            params={"action": "FISCAL_YEAR_REOPENED"},
        )
        assert audit_api.status_code == 403, audit_api.text

    session_factory = get_session_factory()
    async with session_factory() as session:
        audit_event = await session.scalar(
            select(AuditLog).where(
                AuditLog.action == "FISCAL_YEAR_REOPENED",
                AuditLog.entity_id == fy1_id,
            )
        )
        assert audit_event is not None
        assert audit_event.actor_user_id is not None

    await cleanup()
    await get_engine().dispose()
    print("Phase 2A budget foundation verification: OK")


if __name__ == "__main__":
    asyncio.run(verify())
