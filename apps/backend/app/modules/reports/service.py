from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.annual_budgets.models import AnnualBudget
from app.modules.annual_budgets.schemas import AnnualBudgetStatus
from app.modules.auth.repository import get_user_organization
from app.modules.authorization.service import get_permission_scope_assignments
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear
from app.modules.budget_foundation.schemas import FiscalYearStatus
from app.modules.budget_plans.models import BudgetPlan, BudgetPlanItem, BudgetPlanVersion
from app.modules.organizations.models import OrganizationUnit, UserUnitMembership
from app.modules.realizations.models import Realization
from app.modules.reports.schemas import (
    FinancialSummaryResponse,
    ReportCategoryPlanSummary,
    ReportMonthlyRealization,
    ReportUnitOption,
    ReportUnitSummary,
)
from app.modules.unit_allocations.models import UnitAllocation

ZERO = Decimal("0.00")
PERCENT_ZERO = Decimal("0.00")


@dataclass(slots=True)
class _CategoryTotals:
    code: str
    name: str
    committed: Decimal = ZERO
    pipeline: Decimal = ZERO


MONTH_LABELS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
)


def normalize_amount(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def utilization_percent(realized: Decimal, committed: Decimal) -> Decimal:
    if committed <= ZERO:
        return PERCENT_ZERO
    return ((realized / committed) * Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def resolve_requested_scope(
    permitted_unit_ids: set[UUID],
    requested_unit_id: UUID | None,
) -> set[UUID]:
    if requested_unit_id is None:
        return set(permitted_unit_ids)
    if requested_unit_id not in permitted_unit_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unit organisasi berada di luar scope laporan Anda.",
        )
    return {requested_unit_id}


def _descendant_ids(
    *,
    root_id: UUID,
    children_by_parent: dict[UUID | None, set[UUID]],
) -> set[UUID]:
    result: set[UUID] = set()
    pending = [root_id]
    while pending:
        current = pending.pop()
        if current in result:
            continue
        result.add(current)
        pending.extend(children_by_parent.get(current, set()))
    return result


async def _report_scope_unit_ids(
    session: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID,
) -> tuple[set[UUID], bool]:
    assignments = await get_permission_scope_assignments(
        session,
        user_id=user_id,
        permission_code="reports.view",
    )
    if not assignments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki permission untuk melihat laporan.",
        )

    units = (
        await session.scalars(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization_id,
                OrganizationUnit.is_active.is_(True),
            )
        )
    ).all()
    all_ids = {unit.id for unit in units}
    if any(assignment.scope_type == "ALL" for assignment in assignments):
        return all_ids, True

    children_by_parent: dict[UUID | None, set[UUID]] = defaultdict(set)
    for unit in units:
        children_by_parent[unit.parent_id].add(unit.id)

    allowed: set[UUID] = set()
    for assignment in assignments:
        if assignment.scope_type == "OWN_UNIT" and assignment.scope_unit_id is not None:
            if assignment.scope_unit_id in all_ids:
                allowed.add(assignment.scope_unit_id)
        elif (
            assignment.scope_type == "OWN_UNIT_AND_CHILDREN"
            and assignment.scope_unit_id is not None
            and assignment.scope_unit_id in all_ids
        ):
            allowed.update(
                _descendant_ids(
                    root_id=assignment.scope_unit_id,
                    children_by_parent=children_by_parent,
                )
            )
        elif assignment.scope_type == "OWN":
            membership_ids = (
                await session.scalars(
                    select(UserUnitMembership.organization_unit_id).where(
                        UserUnitMembership.user_id == user_id,
                        UserUnitMembership.start_at <= date.today(),
                        or_(
                            UserUnitMembership.end_at.is_(None),
                            UserUnitMembership.end_at >= date.today(),
                        ),
                    )
                )
            ).all()
            allowed.update(unit_id for unit_id in membership_ids if unit_id in all_ids)

    return allowed, False


async def get_financial_summary(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    user_id: UUID,
    organization_unit_id: UUID | None = None,
) -> FinancialSummaryResponse:
    organization = await get_user_organization(session, user_id)
    fiscal_year = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.id == fiscal_year_id,
            FiscalYear.organization_id == organization.id,
        )
    )
    if fiscal_year is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tahun anggaran tidak ditemukan.",
        )

    permitted_scope_unit_ids, has_all_scope = await _report_scope_unit_ids(
        session,
        user_id=user_id,
        organization_id=organization.id,
    )

    unit_filter_rows = (
        (
            await session.execute(
                select(
                    OrganizationUnit.id,
                    OrganizationUnit.code,
                    OrganizationUnit.name,
                )
                .where(
                    OrganizationUnit.organization_id == organization.id,
                    OrganizationUnit.id.in_(permitted_scope_unit_ids),
                    OrganizationUnit.is_active.is_(True),
                )
                .order_by(OrganizationUnit.name.asc())
            )
        )
        .tuples()
        .all()
        if permitted_scope_unit_ids
        else []
    )
    unit_filter_options = [
        ReportUnitOption(
            organization_unit_id=unit_id,
            organization_unit_code=unit_code,
            organization_unit_name=unit_name,
        )
        for unit_id, unit_code, unit_name in unit_filter_rows
    ]

    scope_unit_ids = resolve_requested_scope(
        permitted_scope_unit_ids,
        organization_unit_id,
    )
    has_all_scope = has_all_scope and organization_unit_id is None

    annual_budget = await session.scalar(
        select(AnnualBudget).where(
            AnnualBudget.organization_id == organization.id,
            AnnualBudget.fiscal_year_id == fiscal_year.id,
        )
    )

    allocation_rows = (
        (
            await session.execute(
                select(
                    UnitAllocation.organization_unit_id,
                    UnitAllocation.amount,
                    OrganizationUnit.code,
                    OrganizationUnit.name,
                )
                .join(
                    OrganizationUnit,
                    OrganizationUnit.id == UnitAllocation.organization_unit_id,
                )
                .where(
                    UnitAllocation.organization_id == organization.id,
                    UnitAllocation.fiscal_year_id == fiscal_year.id,
                    UnitAllocation.organization_unit_id.in_(scope_unit_ids),
                )
                .order_by(OrganizationUnit.name.asc())
            )
        )
        .tuples()
        .all()
        if scope_unit_ids
        else []
    )

    allocated_by_unit: dict[UUID, Decimal] = {
        unit_id: normalize_amount(amount) for unit_id, amount, _, _ in allocation_rows
    }

    committed_by_unit: dict[UUID, Decimal] = defaultdict(lambda: ZERO)
    plan_pipeline_by_unit: dict[UUID, Decimal] = defaultdict(lambda: ZERO)
    approved_plan_count = 0

    plan_rows = (
        (
            await session.execute(
                select(
                    BudgetPlan.organization_unit_id,
                    BudgetPlan.status,
                    BudgetPlanVersion.total_amount,
                )
                .join(
                    BudgetPlanVersion,
                    and_(
                        BudgetPlanVersion.budget_plan_id == BudgetPlan.id,
                        BudgetPlanVersion.version_no == BudgetPlan.current_version_no,
                    ),
                )
                .where(
                    BudgetPlan.organization_id == organization.id,
                    BudgetPlan.fiscal_year_id == fiscal_year.id,
                    BudgetPlan.organization_unit_id.in_(scope_unit_ids),
                )
            )
        )
        .tuples()
        .all()
        if scope_unit_ids
        else []
    )

    for unit_id, plan_status, total_amount in plan_rows:
        total = normalize_amount(total_amount)
        if plan_status == "APPROVED":
            committed_by_unit[unit_id] = normalize_amount(committed_by_unit[unit_id] + total)
            approved_plan_count += 1
        elif plan_status in {"DRAFT", "PENDING_APPROVAL"}:
            plan_pipeline_by_unit[unit_id] = normalize_amount(
                plan_pipeline_by_unit[unit_id] + total
            )

    realized_by_unit: dict[UUID, Decimal] = defaultdict(lambda: ZERO)
    realization_pipeline_by_unit: dict[UUID, Decimal] = defaultdict(lambda: ZERO)
    monthly_amounts: dict[int, Decimal] = defaultdict(lambda: ZERO)
    realization_count = 0

    realization_rows: list[Realization] = []
    if scope_unit_ids:
        realization_rows = list(
            (
                await session.scalars(
                    select(Realization).where(
                        Realization.organization_id == organization.id,
                        Realization.fiscal_year_id == fiscal_year.id,
                        Realization.organization_unit_id.in_(scope_unit_ids),
                    )
                )
            ).all()
        )

    for realization in realization_rows:
        if realization.status == "POSTED":
            amount = normalize_amount(realization.amount)
            realized_by_unit[realization.organization_unit_id] = normalize_amount(
                realized_by_unit[realization.organization_unit_id] + amount
            )
            monthly_amounts[realization.realization_date.month] = normalize_amount(
                monthly_amounts[realization.realization_date.month] + amount
            )
            realization_count += 1
        elif realization.status == "DRAFT":
            amount = normalize_amount(realization.amount)
            realization_pipeline_by_unit[realization.organization_unit_id] = normalize_amount(
                realization_pipeline_by_unit[realization.organization_unit_id] + amount
            )

    unit_summaries: list[ReportUnitSummary] = []
    for unit_id, _, unit_code, unit_name in allocation_rows:
        allocated = allocated_by_unit.get(unit_id, ZERO)
        committed = committed_by_unit.get(unit_id, ZERO)
        plan_pipeline = plan_pipeline_by_unit.get(unit_id, ZERO)
        realized = realized_by_unit.get(unit_id, ZERO)
        realization_pipeline = realization_pipeline_by_unit.get(unit_id, ZERO)
        unit_summaries.append(
            ReportUnitSummary(
                organization_unit_id=unit_id,
                organization_unit_code=unit_code,
                organization_unit_name=unit_name,
                allocated_amount=allocated,
                committed_amount=committed,
                draft_pipeline_amount=plan_pipeline,
                available_amount=normalize_amount(max(allocated - committed, ZERO)),
                realized_amount=realized,
                realization_draft_pipeline_amount=realization_pipeline,
                remaining_to_realize_amount=normalize_amount(max(committed - realized, ZERO)),
                utilization_percent=utilization_percent(realized, committed),
            )
        )

    allocated = normalize_amount(sum(allocated_by_unit.values(), ZERO))
    committed = normalize_amount(sum(committed_by_unit.values(), ZERO))
    draft_pipeline = normalize_amount(sum(plan_pipeline_by_unit.values(), ZERO))
    realized = normalize_amount(sum(realized_by_unit.values(), ZERO))
    realization_pipeline = normalize_amount(sum(realization_pipeline_by_unit.values(), ZERO))
    available = normalize_amount(max(allocated - committed, ZERO))
    remaining_to_realize = normalize_amount(max(committed - realized, ZERO))

    organization_budget_amount = (
        normalize_amount(annual_budget.amount) if annual_budget is not None else None
    )
    scope_budget_amount = organization_budget_amount or ZERO if has_all_scope else allocated
    unallocated = normalize_amount(max(scope_budget_amount - allocated, ZERO))

    category_totals: dict[UUID, _CategoryTotals] = {}
    if scope_unit_ids:
        category_rows = (
            (
                await session.execute(
                    select(
                        BudgetCategory.id,
                        BudgetCategory.code,
                        BudgetCategory.name,
                        BudgetPlan.status,
                        BudgetPlanItem.amount,
                    )
                    .join(
                        BudgetPlanItem,
                        BudgetPlanItem.budget_category_id == BudgetCategory.id,
                    )
                    .join(
                        BudgetPlanVersion,
                        BudgetPlanVersion.id == BudgetPlanItem.plan_version_id,
                    )
                    .join(
                        BudgetPlan,
                        and_(
                            BudgetPlan.id == BudgetPlanVersion.budget_plan_id,
                            BudgetPlan.current_version_no == BudgetPlanVersion.version_no,
                        ),
                    )
                    .where(
                        BudgetCategory.organization_id == organization.id,
                        BudgetPlan.fiscal_year_id == fiscal_year.id,
                        BudgetPlan.organization_unit_id.in_(scope_unit_ids),
                        BudgetPlan.status.in_(("APPROVED", "DRAFT", "PENDING_APPROVAL")),
                    )
                )
            )
            .tuples()
            .all()
        )
        for category_id, code, name, plan_status, item_amount in category_rows:
            current = category_totals.setdefault(
                category_id,
                _CategoryTotals(code=code, name=name),
            )
            amount = normalize_amount(item_amount)
            if plan_status == "APPROVED":
                current.committed = normalize_amount(current.committed + amount)
            else:
                current.pipeline = normalize_amount(current.pipeline + amount)

    category_summaries = [
        ReportCategoryPlanSummary(
            budget_category_id=category_id,
            budget_category_code=values.code,
            budget_category_name=values.name,
            committed_amount=values.committed,
            draft_pipeline_amount=values.pipeline,
        )
        for category_id, values in sorted(
            category_totals.items(),
            key=lambda item: item[1].name,
        )
    ]

    monthly = [
        ReportMonthlyRealization(
            month=month,
            month_label=MONTH_LABELS[month - 1],
            realized_amount=normalize_amount(monthly_amounts.get(month, ZERO)),
        )
        for month in range(1, 13)
    ]

    return FinancialSummaryResponse(
        fiscal_year_id=fiscal_year.id,
        fiscal_year_code=fiscal_year.code,
        fiscal_year_status=FiscalYearStatus(fiscal_year.status),
        organization_unit_filter_id=organization_unit_id,
        annual_budget_id=annual_budget.id if annual_budget is not None else None,
        annual_budget_status=(
            AnnualBudgetStatus(annual_budget.status) if annual_budget is not None else None
        ),
        organization_annual_budget_amount=organization_budget_amount,
        scope_budget_amount=scope_budget_amount,
        allocated_amount=allocated,
        unallocated_amount=unallocated,
        committed_amount=committed,
        draft_pipeline_amount=draft_pipeline,
        available_amount=available,
        realized_amount=realized,
        realization_draft_pipeline_amount=realization_pipeline,
        remaining_to_realize_amount=remaining_to_realize,
        utilization_percent=utilization_percent(realized, committed),
        allocation_count=len(allocation_rows),
        approved_plan_count=approved_plan_count,
        realization_count=realization_count,
        unit_filter_options=unit_filter_options,
        unit_summaries=unit_summaries,
        monthly_realization=monthly,
        category_plan_summaries=category_summaries,
    )
