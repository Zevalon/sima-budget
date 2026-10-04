import asyncio
from decimal import Decimal

from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.database import get_engine, get_session_factory
from app.core.security import verify_password
from app.modules.annual_budgets.models import AnnualBudget, AnnualBudgetApproval
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.budget_plans.models import (
    BudgetPlan,
    BudgetPlanApproval,
    BudgetPlanItem,
    BudgetPlanVersion,
)
from app.modules.organizations.bootstrap_data import DEFAULT_UNIT_TYPES
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    OrganizationUnitType,
    UserUnitMembership,
)
from app.modules.realizations.models import Realization
from app.modules.roles.bootstrap_data import ALL_BOOTSTRAP_PERMISSIONS, DEFAULT_ROLE_TEMPLATES
from app.modules.roles.models import Permission, Role, UserRoleAssignment
from app.modules.settings.models import ApplicationSetting
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User
from scripts.seed_dev import CATEGORY_SPECS, SEED_PROFILE, UNIT_SPECS, UOM_SPECS, USER_SPECS


async def verify() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        assert organization is not None

        setting = await session.scalar(
            select(ApplicationSetting).where(ApplicationSetting.organization_id == organization.id)
        )
        assert setting is not None
        assert setting.application_short_name == "SIMA DEV"
        assert setting.allow_self_approval is False

        unit_count = await session.scalar(
            select(func.count(OrganizationUnit.id)).where(
                OrganizationUnit.organization_id == organization.id
            )
        )
        unit_type_count = await session.scalar(
            select(func.count(OrganizationUnitType.id)).where(
                OrganizationUnitType.organization_id == organization.id
            )
        )
        assert int(unit_count or 0) >= 1 + len(UNIT_SPECS)
        assert int(unit_type_count or 0) >= len(DEFAULT_UNIT_TYPES)

        users = (
            await session.scalars(
                select(User).where(User.username.in_([item[0] for item in USER_SPECS]))
            )
        ).all()
        assert len(users) == len(USER_SPECS)
        users_by_username = {user.username: user for user in users}
        password = get_settings().dev_seed_password
        for username in ("sysadmin", "budgetadmin", "management"):
            assert verify_password(users_by_username[username].password_hash, password)

        membership_count = await session.scalar(
            select(func.count(UserUnitMembership.id)).where(
                UserUnitMembership.user_id.in_([user.id for user in users])
            )
        )
        assignment_count = await session.scalar(
            select(func.count(UserRoleAssignment.id)).where(
                UserRoleAssignment.user_id.in_([user.id for user in users])
            )
        )
        assert int(membership_count or 0) == len(USER_SPECS)
        assert int(assignment_count or 0) == len(USER_SPECS)

        role_count = await session.scalar(
            select(func.count(Role.id)).where(Role.organization_id == organization.id)
        )
        permission_count = await session.scalar(select(func.count(Permission.id)))
        assert int(role_count or 0) >= len(DEFAULT_ROLE_TEMPLATES)
        assert int(permission_count or 0) >= len(ALL_BOOTSTRAP_PERMISSIONS)

        active_count = await session.scalar(
            select(func.count(FiscalYear.id)).where(
                FiscalYear.organization_id == organization.id,
                FiscalYear.status == "ACTIVE",
            )
        )
        planning_count = await session.scalar(
            select(func.count(FiscalYear.id)).where(
                FiscalYear.organization_id == organization.id,
                FiscalYear.status == "PLANNING",
            )
        )
        assert int(active_count or 0) == 1
        assert int(planning_count or 0) == 1

        category_count = await session.scalar(
            select(func.count(BudgetCategory.id)).where(
                BudgetCategory.organization_id == organization.id
            )
        )
        uom_count = await session.scalar(
            select(func.count(UnitOfMeasure.id)).where(
                UnitOfMeasure.organization_id == organization.id
            )
        )
        assert int(category_count or 0) >= len(CATEGORY_SPECS)
        assert int(uom_count or 0) >= len(UOM_SPECS)

        fy2026 = await session.scalar(
            select(FiscalYear).where(
                FiscalYear.organization_id == organization.id,
                FiscalYear.code == "FY2026",
            )
        )
        assert fy2026 is not None
        budget2026 = await session.scalar(
            select(AnnualBudget).where(AnnualBudget.fiscal_year_id == fy2026.id)
        )
        assert budget2026 is not None
        assert budget2026.status == "APPROVED"
        assert budget2026.amount == Decimal("600000000000.00")

        allocated = await session.scalar(
            select(func.sum(UnitAllocation.amount)).where(
                UnitAllocation.annual_budget_id == budget2026.id
            )
        )
        assert allocated == Decimal("300000000000.00")
        assert budget2026.amount - allocated == Decimal("300000000000.00")

        approval_count = await session.scalar(
            select(func.count(AnnualBudgetApproval.id)).where(
                AnnualBudgetApproval.annual_budget_id == budget2026.id
            )
        )
        assert int(approval_count or 0) == 1

        eligible_unallocated = await session.scalar(
            select(func.count(OrganizationUnit.id)).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.is_active.is_(True),
                OrganizationUnit.can_receive_budget.is_(True),
                ~OrganizationUnit.id.in_(
                    select(UnitAllocation.organization_unit_id).where(
                        UnitAllocation.annual_budget_id == budget2026.id
                    )
                ),
            )
        )
        assert int(eligible_unallocated or 0) >= 1

        seeded_plans = (
            await session.scalars(
                select(BudgetPlan).where(
                    BudgetPlan.organization_id == organization.id,
                    BudgetPlan.plan_number.in_(
                        [
                            "DEV-FY2026-IT-001",
                            "DEV-FY2026-IT-APPROVED-001",
                            "DEV-FY2026-FTI-001",
                        ]
                    ),
                )
            )
        ).all()
        assert len(seeded_plans) == 3
        statuses = {plan.plan_number: plan.status for plan in seeded_plans}
        assert statuses["DEV-FY2026-IT-001"] == "PENDING_APPROVAL"
        assert statuses["DEV-FY2026-IT-APPROVED-001"] == "APPROVED"
        assert statuses["DEV-FY2026-FTI-001"] == "REJECTED"
        for plan in seeded_plans:
            version = await session.scalar(
                select(BudgetPlanVersion).where(
                    BudgetPlanVersion.budget_plan_id == plan.id,
                    BudgetPlanVersion.version_no == 1,
                )
            )
            assert version is not None
            item_count = await session.scalar(
                select(func.count(BudgetPlanItem.id)).where(
                    BudgetPlanItem.plan_version_id == version.id
                )
            )
            assert int(item_count or 0) == 2
            assert version.total_amount > Decimal("0.00")
            approval = await session.scalar(
                select(BudgetPlanApproval).where(
                    BudgetPlanApproval.budget_plan_id == plan.id,
                    BudgetPlanApproval.submission_no == 1,
                )
            )
            assert approval is not None
            assert approval.plan_version_id == version.id
            if plan.plan_number == "DEV-FY2026-IT-001":
                assert approval.status == "PENDING"
                assert approval.decided_by is None
            elif plan.plan_number == "DEV-FY2026-IT-APPROVED-001":
                assert approval.status == "APPROVED"
                assert approval.decided_by is not None
                assert plan.approved_by is not None
                assert plan.approved_at is not None
            else:
                assert approval.status == "REJECTED"
                assert approval.decided_by is not None
                assert plan.rejection_reason is not None

        it_allocation = await session.scalar(
            select(UnitAllocation)
            .join(OrganizationUnit, OrganizationUnit.id == UnitAllocation.organization_unit_id)
            .where(
                UnitAllocation.fiscal_year_id == fy2026.id,
                OrganizationUnit.code == "IT",
            )
        )
        approved_it_plan = next(
            plan for plan in seeded_plans if plan.plan_number == "DEV-FY2026-IT-APPROVED-001"
        )
        approved_it_version = await session.scalar(
            select(BudgetPlanVersion).where(
                BudgetPlanVersion.budget_plan_id == approved_it_plan.id,
                BudgetPlanVersion.version_no == approved_it_plan.current_version_no,
            )
        )
        assert it_allocation is not None
        assert approved_it_version is not None
        assert approved_it_version.total_amount == Decimal("30000000000.00")
        assert it_allocation.amount - approved_it_version.total_amount == Decimal("90000000000.00")

        fy2025 = await session.scalar(
            select(FiscalYear).where(
                FiscalYear.organization_id == organization.id,
                FiscalYear.code == "FY2025",
            )
        )
        assert fy2025 is not None
        realization_plan = await session.scalar(
            select(BudgetPlan).where(
                BudgetPlan.organization_id == organization.id,
                BudgetPlan.plan_number == "DEV-FY2025-IT-REALIZATION-001",
            )
        )
        assert realization_plan is not None
        assert realization_plan.status == "APPROVED"
        realization_rows = (
            await session.scalars(
                select(Realization).where(Realization.budget_plan_id == realization_plan.id)
            )
        ).all()
        assert len(realization_rows) == 2
        realized_amount = sum(
            (item.amount for item in realization_rows if item.status == "POSTED"),
            Decimal("0.00"),
        )
        draft_realization = sum(
            (item.amount for item in realization_rows if item.status == "DRAFT"),
            Decimal("0.00"),
        )
        assert realized_amount == Decimal("5000000000.00")
        assert draft_realization == Decimal("2000000000.00")

        revoked_seed_session = await session.scalar(
            select(UserSession).where(UserSession.user_id == users_by_username["viewer"].id)
        )
        assert revoked_seed_session is not None
        assert revoked_seed_session.revoked_at is not None

        seed_audit = await session.scalar(
            select(AuditLog).where(
                AuditLog.action == "DEV_SEED_APPLIED",
                AuditLog.metadata_json.contains({"seed_profile": SEED_PROFILE}),
            )
        )
        assert seed_audit is not None

    await get_engine().dispose()
    print(
        "Development seed verification: OK "
        f"(users={len(USER_SPECS)}, roles={len(DEFAULT_ROLE_TEMPLATES)}, "
        f"permissions={len(ALL_BOOTSTRAP_PERMISSIONS)}, units={1 + len(UNIT_SPECS)})"
    )


if __name__ == "__main__":
    asyncio.run(verify())
