from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import record_audit
from app.modules.auth.repository import get_default_organization
from app.modules.authorization.service import can_access_unit, get_permission_scope_assignments
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.budget_foundation.schemas import FiscalYearStatus
from app.modules.budget_plans.models import (
    BudgetPlan,
    BudgetPlanApproval,
    BudgetPlanItem,
    BudgetPlanVersion,
)
from app.modules.budget_plans.schemas import (
    BudgetPlanAllocationOption,
    BudgetPlanApprovalResponse,
    BudgetPlanApprovalStatus,
    BudgetPlanApproveRequest,
    BudgetPlanContextResponse,
    BudgetPlanCreateRequest,
    BudgetPlanItemRequest,
    BudgetPlanItemResponse,
    BudgetPlanLookupOption,
    BudgetPlanPendingApprovalResponse,
    BudgetPlanRejectRequest,
    BudgetPlanResponse,
    BudgetPlanRevisionRequest,
    BudgetPlanStatus,
    BudgetPlanSubmitRequest,
    BudgetPlanUpdateRequest,
)
from app.modules.organizations.models import OrganizationUnit
from app.modules.settings.service import get_application_setting
from app.modules.unit_allocations.models import UnitAllocation

MONEY_QUANTUM = Decimal("0.01")


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def normalize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def item_amount(item: BudgetPlanItemRequest) -> Decimal:
    return normalize_money(item.quantity * item.unit_price)


async def _allocation_plan_total(
    session: AsyncSession,
    *,
    allocation_id: UUID,
    statuses: tuple[str, ...],
) -> Decimal:
    value = await session.scalar(
        select(func.sum(BudgetPlanVersion.total_amount))
        .join(
            BudgetPlan,
            and_(
                BudgetPlan.id == BudgetPlanVersion.budget_plan_id,
                BudgetPlan.current_version_no == BudgetPlanVersion.version_no,
            ),
        )
        .where(
            BudgetPlan.unit_allocation_id == allocation_id,
            BudgetPlan.status.in_(statuses),
        )
    )
    return normalize_money(value if value is not None else Decimal("0.00"))


async def _allocation_financials(
    session: AsyncSession,
    *,
    allocation: UnitAllocation,
) -> tuple[Decimal, Decimal, Decimal]:
    committed = await _allocation_plan_total(
        session,
        allocation_id=allocation.id,
        statuses=(BudgetPlanStatus.APPROVED.value,),
    )
    pipeline = await _allocation_plan_total(
        session,
        allocation_id=allocation.id,
        statuses=(BudgetPlanStatus.DRAFT.value, BudgetPlanStatus.PENDING_APPROVAL.value),
    )
    available = normalize_money(max(allocation.amount - committed, Decimal("0.00")))
    return committed, pipeline, available


async def _fiscal_year(
    session: AsyncSession, organization_id: UUID, fiscal_year_id: UUID
) -> FiscalYear:
    item = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.id == fiscal_year_id,
            FiscalYear.organization_id == organization_id,
        )
    )
    if item is None:
        raise not_found("Tahun anggaran tidak ditemukan.")
    return item


async def _allocation_with_unit(
    session: AsyncSession,
    *,
    organization_id: UUID,
    allocation_id: UUID,
    lock: bool = False,
) -> tuple[UnitAllocation, OrganizationUnit]:
    statement = (
        select(UnitAllocation, OrganizationUnit)
        .join(OrganizationUnit, OrganizationUnit.id == UnitAllocation.organization_unit_id)
        .where(
            UnitAllocation.id == allocation_id,
            UnitAllocation.organization_id == organization_id,
        )
    )
    if lock:
        statement = statement.with_for_update(of=UnitAllocation)
    row = (await session.execute(statement)).first()
    if row is None:
        raise not_found("Alokasi unit tidak ditemukan.")
    allocation, unit = row
    return allocation, unit


async def _assert_unit_permission(
    session: AsyncSession,
    *,
    user_id: UUID,
    permission_code: str,
    unit_id: UUID,
) -> None:
    if not await can_access_unit(
        session,
        user_id=user_id,
        permission_code=permission_code,
        unit_id=unit_id,
    ):
        raise forbidden("Anda tidak memiliki scope untuk unit organisasi ini.")


async def _can_read_plan(
    session: AsyncSession,
    *,
    user_id: UUID,
    plan: BudgetPlan,
) -> bool:
    if await can_access_unit(
        session,
        user_id=user_id,
        permission_code="budget_plans.view",
        unit_id=plan.organization_unit_id,
    ):
        return True
    assignments = await get_permission_scope_assignments(
        session,
        user_id=user_id,
        permission_code="budget_plans.view",
    )
    return any(item.scope_type == "OWN" for item in assignments) and plan.created_by == user_id


async def _validated_lookup_maps(
    session: AsyncSession,
    *,
    organization_id: UUID,
    items: list[BudgetPlanItemRequest],
) -> tuple[dict[UUID, BudgetCategory], dict[UUID, UnitOfMeasure]]:
    category_ids = {item.budget_category_id for item in items}
    uom_ids = {item.unit_of_measure_id for item in items}

    categories = {
        item.id: item
        for item in (
            await session.scalars(
                select(BudgetCategory).where(
                    BudgetCategory.organization_id == organization_id,
                    BudgetCategory.id.in_(category_ids),
                    BudgetCategory.is_active.is_(True),
                )
            )
        ).all()
    }
    uoms = {
        item.id: item
        for item in (
            await session.scalars(
                select(UnitOfMeasure).where(
                    UnitOfMeasure.organization_id == organization_id,
                    UnitOfMeasure.id.in_(uom_ids),
                    UnitOfMeasure.is_active.is_(True),
                )
            )
        ).all()
    }

    if len(categories) != len(category_ids):
        raise conflict("Terdapat kategori anggaran yang tidak aktif atau tidak valid.")
    if len(uoms) != len(uom_ids):
        raise conflict("Terdapat satuan yang tidak aktif atau tidak valid.")
    return categories, uoms


async def _response(session: AsyncSession, plan: BudgetPlan) -> BudgetPlanResponse:
    fiscal_year = await session.scalar(
        select(FiscalYear).where(FiscalYear.id == plan.fiscal_year_id)
    )
    allocation, unit = await _allocation_with_unit(
        session,
        organization_id=plan.organization_id,
        allocation_id=plan.unit_allocation_id,
    )
    version = await session.scalar(
        select(BudgetPlanVersion).where(
            BudgetPlanVersion.budget_plan_id == plan.id,
            BudgetPlanVersion.version_no == plan.current_version_no,
        )
    )
    if fiscal_year is None or version is None:
        raise RuntimeError("Data rencana anggaran tidak konsisten.")

    rows = (
        await session.execute(
            select(BudgetPlanItem, BudgetCategory, UnitOfMeasure)
            .join(BudgetCategory, BudgetCategory.id == BudgetPlanItem.budget_category_id)
            .join(UnitOfMeasure, UnitOfMeasure.id == BudgetPlanItem.unit_of_measure_id)
            .where(BudgetPlanItem.plan_version_id == version.id)
            .order_by(BudgetPlanItem.line_no.asc())
        )
    ).all()
    committed, pipeline, available = await _allocation_financials(
        session,
        allocation=allocation,
    )

    return BudgetPlanResponse(
        id=plan.id,
        fiscal_year_id=plan.fiscal_year_id,
        fiscal_year_code=fiscal_year.code,
        unit_allocation_id=plan.unit_allocation_id,
        organization_unit_id=plan.organization_unit_id,
        organization_unit_code=unit.code,
        organization_unit_name=unit.name,
        allocation_amount=allocation.amount,
        allocation_committed_amount=committed,
        allocation_draft_pipeline_amount=pipeline,
        allocation_available_amount=available,
        plan_number=plan.plan_number,
        status=BudgetPlanStatus(plan.status),
        current_version_no=plan.current_version_no,
        row_version=plan.row_version,
        title=version.title,
        description=version.description,
        total_amount=version.total_amount,
        items=[
            BudgetPlanItemResponse(
                id=item.id,
                line_no=item.line_no,
                budget_category_id=category.id,
                budget_category_code=category.code,
                budget_category_name=category.name,
                unit_of_measure_id=uom.id,
                unit_of_measure_code=uom.code,
                unit_of_measure_name=uom.name,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
                notes=item.notes,
            )
            for item, category, uom in rows
        ],
        created_by=plan.created_by,
        submitted_by=plan.submitted_by,
        submitted_at=plan.submitted_at,
        approved_by=plan.approved_by,
        approved_at=plan.approved_at,
        rejection_reason=plan.rejection_reason,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


async def get_budget_plan_context(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    user_id: UUID,
) -> BudgetPlanContextResponse:
    organization = await get_default_organization(session)
    fiscal_year = await _fiscal_year(session, organization.id, fiscal_year_id)

    rows = (
        await session.execute(
            select(UnitAllocation, OrganizationUnit)
            .join(OrganizationUnit, OrganizationUnit.id == UnitAllocation.organization_unit_id)
            .where(
                UnitAllocation.organization_id == organization.id,
                UnitAllocation.fiscal_year_id == fiscal_year.id,
                OrganizationUnit.is_active.is_(True),
                OrganizationUnit.can_create_budget_plan.is_(True),
            )
            .order_by(OrganizationUnit.name.asc())
        )
    ).all()
    allocations: list[BudgetPlanAllocationOption] = []
    for allocation, unit in rows:
        if await can_access_unit(
            session,
            user_id=user_id,
            permission_code="budget_plans.view",
            unit_id=unit.id,
        ):
            committed, pipeline, available = await _allocation_financials(
                session,
                allocation=allocation,
            )
            allocations.append(
                BudgetPlanAllocationOption(
                    unit_allocation_id=allocation.id,
                    organization_unit_id=unit.id,
                    organization_unit_code=unit.code,
                    organization_unit_name=unit.name,
                    allocation_amount=allocation.amount,
                    committed_amount=committed,
                    draft_pipeline_amount=pipeline,
                    available_amount=available,
                )
            )

    categories = (
        await session.scalars(
            select(BudgetCategory)
            .where(
                BudgetCategory.organization_id == organization.id,
                BudgetCategory.is_active.is_(True),
            )
            .order_by(BudgetCategory.code.asc())
        )
    ).all()
    uoms = (
        await session.scalars(
            select(UnitOfMeasure)
            .where(
                UnitOfMeasure.organization_id == organization.id,
                UnitOfMeasure.is_active.is_(True),
            )
            .order_by(UnitOfMeasure.code.asc())
        )
    ).all()
    scope_allocation = normalize_money(
        sum((item.allocation_amount for item in allocations), Decimal("0.00"))
    )
    scope_committed = normalize_money(
        sum((item.committed_amount for item in allocations), Decimal("0.00"))
    )
    scope_pipeline = normalize_money(
        sum((item.draft_pipeline_amount for item in allocations), Decimal("0.00"))
    )
    scope_available = normalize_money(
        sum((item.available_amount for item in allocations), Decimal("0.00"))
    )
    return BudgetPlanContextResponse(
        fiscal_year_id=fiscal_year.id,
        fiscal_year_code=fiscal_year.code,
        fiscal_year_status=FiscalYearStatus(fiscal_year.status),
        scope_allocation_amount=scope_allocation,
        scope_committed_amount=scope_committed,
        scope_draft_pipeline_amount=scope_pipeline,
        scope_available_amount=scope_available,
        allocations=allocations,
        budget_categories=[
            BudgetPlanLookupOption(id=x.id, code=x.code, name=x.name) for x in categories
        ],
        units_of_measure=[BudgetPlanLookupOption(id=x.id, code=x.code, name=x.name) for x in uoms],
    )


async def list_budget_plans(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    user_id: UUID,
) -> list[BudgetPlanResponse]:
    organization = await get_default_organization(session)
    await _fiscal_year(session, organization.id, fiscal_year_id)
    plans = (
        await session.scalars(
            select(BudgetPlan)
            .where(
                BudgetPlan.organization_id == organization.id,
                BudgetPlan.fiscal_year_id == fiscal_year_id,
            )
            .order_by(BudgetPlan.created_at.desc())
        )
    ).all()
    visible = [plan for plan in plans if await _can_read_plan(session, user_id=user_id, plan=plan)]
    return [await _response(session, plan) for plan in visible]


async def get_budget_plan(
    session: AsyncSession,
    *,
    plan_id: UUID,
    user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    plan = await session.scalar(
        select(BudgetPlan).where(
            BudgetPlan.id == plan_id,
            BudgetPlan.organization_id == organization.id,
        )
    )
    if plan is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    if not await _can_read_plan(session, user_id=user_id, plan=plan):
        raise forbidden("Anda tidak memiliki scope untuk rencana anggaran ini.")
    return await _response(session, plan)


async def _replace_items(
    session: AsyncSession,
    *,
    organization_id: UUID,
    version: BudgetPlanVersion,
    payload_items: list[BudgetPlanItemRequest],
) -> Decimal:
    await _validated_lookup_maps(session, organization_id=organization_id, items=payload_items)
    total = normalize_money(sum((item_amount(item) for item in payload_items), Decimal("0.00")))
    await session.execute(
        delete(BudgetPlanItem).where(BudgetPlanItem.plan_version_id == version.id)
    )
    session.add_all(
        [
            BudgetPlanItem(
                organization_id=organization_id,
                plan_version_id=version.id,
                line_no=index,
                budget_category_id=item.budget_category_id,
                unit_of_measure_id=item.unit_of_measure_id,
                description=item.description.strip(),
                quantity=item.quantity,
                unit_price=normalize_money(item.unit_price),
                amount=item_amount(item),
                notes=item.notes.strip() if item.notes else None,
            )
            for index, item in enumerate(payload_items, start=1)
        ]
    )
    version.total_amount = total
    return total


async def create_budget_plan(
    session: AsyncSession,
    *,
    payload: BudgetPlanCreateRequest,
    actor_user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    allocation, unit = await _allocation_with_unit(
        session,
        organization_id=organization.id,
        allocation_id=payload.unit_allocation_id,
        lock=True,
    )
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="budget_plans.create",
        unit_id=unit.id,
    )
    fiscal_year = await _fiscal_year(session, organization.id, allocation.fiscal_year_id)
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Rencana anggaran hanya dapat dibuat saat tahun anggaran PLANNING.")
    if not unit.is_active or not unit.can_create_budget_plan:
        raise conflict("Unit organisasi tidak diizinkan membuat rencana anggaran.")

    await _validated_lookup_maps(session, organization_id=organization.id, items=payload.items)
    total = normalize_money(sum((item_amount(item) for item in payload.items), Decimal("0.00")))
    if total > allocation.amount:
        raise conflict("Total rencana anggaran tidak boleh melebihi alokasi unit.")

    plan = BudgetPlan(
        organization_id=organization.id,
        fiscal_year_id=fiscal_year.id,
        unit_allocation_id=allocation.id,
        organization_unit_id=unit.id,
        plan_number=f"BP-{fiscal_year.code}-{unit.code}-{uuid4().hex[:8].upper()}",
        status="DRAFT",
        current_version_no=1,
        row_version=1,
        created_by=actor_user_id,
    )
    session.add(plan)
    await session.flush()
    version = BudgetPlanVersion(
        organization_id=organization.id,
        budget_plan_id=plan.id,
        version_no=1,
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        total_amount=total,
        created_by=actor_user_id,
    )
    session.add(version)
    await session.flush()
    await _replace_items(
        session,
        organization_id=organization.id,
        version=version,
        payload_items=payload.items,
    )

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_PLAN_CREATED",
        entity_type="budget_plan",
        entity_id=plan.id,
        after_data={
            "plan_number": plan.plan_number,
            "organization_unit_id": str(unit.id),
            "version_no": 1,
            "total_amount": str(total),
        },
    )
    await session.commit()
    await session.refresh(plan)
    return await _response(session, plan)


async def update_budget_plan(
    session: AsyncSession,
    *,
    plan_id: UUID,
    payload: BudgetPlanUpdateRequest,
    actor_user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    plan = await session.scalar(
        select(BudgetPlan)
        .where(BudgetPlan.id == plan_id, BudgetPlan.organization_id == organization.id)
        .with_for_update()
    )
    if plan is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="budget_plans.update",
        unit_id=plan.organization_unit_id,
    )
    if plan.status != "DRAFT":
        raise conflict("Hanya rencana anggaran DRAFT yang dapat diubah.")
    if plan.row_version != payload.expected_row_version:
        raise conflict("Rencana anggaran sudah berubah. Muat ulang sebelum menyimpan.")

    allocation, unit = await _allocation_with_unit(
        session,
        organization_id=organization.id,
        allocation_id=plan.unit_allocation_id,
        lock=True,
    )
    fiscal_year = await _fiscal_year(session, organization.id, plan.fiscal_year_id)
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Rencana anggaran hanya dapat diubah saat tahun anggaran PLANNING.")
    if not unit.is_active or not unit.can_create_budget_plan:
        raise conflict("Unit organisasi tidak diizinkan membuat rencana anggaran.")

    version = await session.scalar(
        select(BudgetPlanVersion)
        .where(
            BudgetPlanVersion.budget_plan_id == plan.id,
            BudgetPlanVersion.version_no == plan.current_version_no,
        )
        .with_for_update()
    )
    if version is None:
        raise RuntimeError("Versi rencana anggaran tidak ditemukan.")

    before = {
        "row_version": plan.row_version,
        "title": version.title,
        "total_amount": str(version.total_amount),
    }
    total = normalize_money(sum((item_amount(item) for item in payload.items), Decimal("0.00")))
    if total > allocation.amount:
        raise conflict("Total rencana anggaran tidak boleh melebihi alokasi unit.")
    await _replace_items(
        session,
        organization_id=organization.id,
        version=version,
        payload_items=payload.items,
    )

    version.title = payload.title.strip()
    version.description = payload.description.strip() if payload.description else None
    plan.row_version += 1
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_PLAN_UPDATED",
        entity_type="budget_plan",
        entity_id=plan.id,
        before_data=before,
        after_data={
            "row_version": plan.row_version,
            "title": version.title,
            "total_amount": str(total),
        },
    )
    await session.commit()
    await session.refresh(plan)
    return await _response(session, plan)


def _approval_response(
    approval: BudgetPlanApproval,
    *,
    version_no: int,
) -> BudgetPlanApprovalResponse:
    return BudgetPlanApprovalResponse(
        id=approval.id,
        budget_plan_id=approval.budget_plan_id,
        plan_version_id=approval.plan_version_id,
        submission_no=approval.submission_no,
        version_no=version_no,
        status=BudgetPlanApprovalStatus(approval.status),
        requested_by=approval.requested_by,
        requested_at=approval.requested_at,
        decided_by=approval.decided_by,
        decided_at=approval.decided_at,
        decision_note=approval.decision_note,
        created_at=approval.created_at,
        updated_at=approval.updated_at,
    )


async def _current_version(
    session: AsyncSession,
    *,
    plan: BudgetPlan,
    lock: bool = False,
) -> BudgetPlanVersion:
    statement = select(BudgetPlanVersion).where(
        BudgetPlanVersion.budget_plan_id == plan.id,
        BudgetPlanVersion.version_no == plan.current_version_no,
    )
    if lock:
        statement = statement.with_for_update()
    version = await session.scalar(statement)
    if version is None:
        raise RuntimeError("Versi rencana anggaran tidak ditemukan.")
    return version


async def submit_budget_plan(
    session: AsyncSession,
    *,
    plan_id: UUID,
    payload: BudgetPlanSubmitRequest,
    actor_user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    plan = await session.scalar(
        select(BudgetPlan)
        .where(BudgetPlan.id == plan_id, BudgetPlan.organization_id == organization.id)
        .with_for_update()
    )
    if plan is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="budget_plans.submit",
        unit_id=plan.organization_unit_id,
    )
    if plan.status != BudgetPlanStatus.DRAFT.value:
        raise conflict("Hanya rencana anggaran DRAFT yang dapat diajukan.")
    if plan.row_version != payload.expected_row_version:
        raise conflict("Rencana anggaran sudah berubah. Muat ulang sebelum mengajukan.")

    fiscal_year = await _fiscal_year(session, organization.id, plan.fiscal_year_id)
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Rencana anggaran hanya dapat diajukan saat tahun anggaran PLANNING.")

    allocation, unit = await _allocation_with_unit(
        session,
        organization_id=organization.id,
        allocation_id=plan.unit_allocation_id,
        lock=True,
    )
    if not unit.is_active or not unit.can_create_budget_plan:
        raise conflict("Unit organisasi tidak diizinkan mengajukan rencana anggaran.")

    version = await _current_version(session, plan=plan, lock=True)
    if version.total_amount > allocation.amount:
        raise conflict("Total rencana anggaran tidak boleh melebihi alokasi unit.")

    submission_no = (
        int(
            await session.scalar(
                select(func.coalesce(func.max(BudgetPlanApproval.submission_no), 0)).where(
                    BudgetPlanApproval.budget_plan_id == plan.id
                )
            )
            or 0
        )
        + 1
    )
    now = datetime.now(UTC)
    approval = BudgetPlanApproval(
        organization_id=organization.id,
        budget_plan_id=plan.id,
        plan_version_id=version.id,
        submission_no=submission_no,
        status=BudgetPlanApprovalStatus.PENDING.value,
        requested_by=actor_user_id,
        requested_at=now,
    )
    session.add(approval)

    plan.status = BudgetPlanStatus.PENDING_APPROVAL.value
    plan.submitted_by = actor_user_id
    plan.submitted_at = now
    plan.approved_by = None
    plan.approved_at = None
    plan.rejection_reason = None
    plan.row_version += 1

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_PLAN_SUBMITTED",
        entity_type="budget_plan",
        entity_id=plan.id,
        before_data={"status": BudgetPlanStatus.DRAFT.value},
        after_data={
            "status": plan.status,
            "submission_no": submission_no,
            "version_no": version.version_no,
            "total_amount": str(version.total_amount),
        },
    )
    await session.commit()
    await session.refresh(plan)
    return await _response(session, plan)


async def _pending_approval_for_update(
    session: AsyncSession,
    *,
    plan_id: UUID,
) -> BudgetPlanApproval:
    approval = await session.scalar(
        select(BudgetPlanApproval)
        .where(
            BudgetPlanApproval.budget_plan_id == plan_id,
            BudgetPlanApproval.status == BudgetPlanApprovalStatus.PENDING.value,
        )
        .order_by(BudgetPlanApproval.submission_no.desc())
        .with_for_update()
    )
    if approval is None:
        raise conflict("Pengajuan rencana anggaran aktif tidak ditemukan.")
    return approval


async def _plan_for_decision(
    session: AsyncSession,
    *,
    plan_id: UUID,
    expected_row_version: int,
    expected_submission_no: int,
    expected_version_no: int,
    actor_user_id: UUID,
) -> tuple[BudgetPlan, BudgetPlanVersion, BudgetPlanApproval]:
    organization = await get_default_organization(session)
    plan = await session.scalar(
        select(BudgetPlan)
        .where(BudgetPlan.id == plan_id, BudgetPlan.organization_id == organization.id)
        .with_for_update()
    )
    if plan is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="budget_plans.approve",
        unit_id=plan.organization_unit_id,
    )
    if plan.status != BudgetPlanStatus.PENDING_APPROVAL.value:
        raise conflict("Hanya rencana anggaran PENDING_APPROVAL yang dapat diputuskan.")
    if plan.row_version != expected_row_version:
        raise conflict("Pengajuan sudah berubah. Muat ulang inbox approval sebelum memutuskan.")

    fiscal_year = await _fiscal_year(session, organization.id, plan.fiscal_year_id)
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Keputusan rencana anggaran hanya dapat dilakukan saat tahun PLANNING.")

    setting = await get_application_setting(session)
    if not setting.allow_self_approval and plan.submitted_by == actor_user_id:
        raise conflict("Self-approval tidak diperbolehkan oleh pengaturan aplikasi.")

    approval = await _pending_approval_for_update(session, plan_id=plan.id)
    if approval.submission_no != expected_submission_no:
        raise conflict("Nomor pengajuan sudah berubah. Muat ulang inbox approval.")
    version = await session.scalar(
        select(BudgetPlanVersion).where(BudgetPlanVersion.id == approval.plan_version_id)
    )
    if version is None:
        raise RuntimeError("Versi yang diajukan tidak ditemukan.")
    if version.version_no != plan.current_version_no:
        raise conflict("Versi rencana yang diajukan bukan versi aktif.")
    if version.version_no != expected_version_no:
        raise conflict("Versi yang ditinjau sudah berubah. Muat ulang inbox approval.")
    return plan, version, approval


async def approve_budget_plan(
    session: AsyncSession,
    *,
    plan_id: UUID,
    payload: BudgetPlanApproveRequest,
    actor_user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    plan, version, approval = await _plan_for_decision(
        session,
        plan_id=plan_id,
        expected_row_version=payload.expected_row_version,
        expected_submission_no=payload.expected_submission_no,
        expected_version_no=payload.expected_version_no,
        actor_user_id=actor_user_id,
    )
    allocation, _ = await _allocation_with_unit(
        session,
        organization_id=organization.id,
        allocation_id=plan.unit_allocation_id,
        lock=True,
    )
    committed_before = await _allocation_plan_total(
        session,
        allocation_id=allocation.id,
        statuses=(BudgetPlanStatus.APPROVED.value,),
    )
    committed_after = normalize_money(committed_before + version.total_amount)
    if committed_after > allocation.amount:
        raise conflict("Rencana tidak dapat disetujui karena saldo alokasi unit tidak mencukupi.")
    available_after = normalize_money(allocation.amount - committed_after)
    now = datetime.now(UTC)
    note = payload.decision_note.strip() if payload.decision_note else None

    approval.status = BudgetPlanApprovalStatus.APPROVED.value
    approval.decided_by = actor_user_id
    approval.decided_at = now
    approval.decision_note = note

    plan.status = BudgetPlanStatus.APPROVED.value
    plan.approved_by = actor_user_id
    plan.approved_at = now
    plan.rejection_reason = None
    plan.row_version += 1

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_PLAN_APPROVED",
        entity_type="budget_plan",
        entity_id=plan.id,
        before_data={"status": BudgetPlanStatus.PENDING_APPROVAL.value},
        after_data={
            "status": plan.status,
            "submission_no": approval.submission_no,
            "version_no": version.version_no,
            "total_amount": str(version.total_amount),
            "committed_before": str(committed_before),
            "committed_after": str(committed_after),
            "available_after": str(available_after),
            "decision_note": note,
        },
    )
    await session.commit()
    await session.refresh(plan)
    return await _response(session, plan)


async def reject_budget_plan(
    session: AsyncSession,
    *,
    plan_id: UUID,
    payload: BudgetPlanRejectRequest,
    actor_user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    plan, version, approval = await _plan_for_decision(
        session,
        plan_id=plan_id,
        expected_row_version=payload.expected_row_version,
        expected_submission_no=payload.expected_submission_no,
        expected_version_no=payload.expected_version_no,
        actor_user_id=actor_user_id,
    )
    reason = payload.reason.strip()
    if len(reason) < 3:
        raise conflict("Alasan penolakan wajib diisi minimal 3 karakter.")
    now = datetime.now(UTC)

    approval.status = BudgetPlanApprovalStatus.REJECTED.value
    approval.decided_by = actor_user_id
    approval.decided_at = now
    approval.decision_note = reason

    plan.status = BudgetPlanStatus.REJECTED.value
    plan.approved_by = None
    plan.approved_at = None
    plan.rejection_reason = reason
    plan.row_version += 1

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_PLAN_REJECTED",
        entity_type="budget_plan",
        entity_id=plan.id,
        before_data={"status": BudgetPlanStatus.PENDING_APPROVAL.value},
        after_data={
            "status": plan.status,
            "submission_no": approval.submission_no,
            "version_no": version.version_no,
            "total_amount": str(version.total_amount),
            "reason": reason,
        },
    )
    await session.commit()
    await session.refresh(plan)
    return await _response(session, plan)


async def revise_budget_plan(
    session: AsyncSession,
    *,
    plan_id: UUID,
    payload: BudgetPlanRevisionRequest,
    actor_user_id: UUID,
) -> BudgetPlanResponse:
    organization = await get_default_organization(session)
    plan = await session.scalar(
        select(BudgetPlan)
        .where(BudgetPlan.id == plan_id, BudgetPlan.organization_id == organization.id)
        .with_for_update()
    )
    if plan is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="budget_plans.revise",
        unit_id=plan.organization_unit_id,
    )
    if plan.status != BudgetPlanStatus.REJECTED.value:
        raise conflict("Hanya rencana anggaran REJECTED yang dapat direvisi.")
    if plan.row_version != payload.expected_row_version:
        raise conflict("Rencana anggaran sudah berubah. Muat ulang sebelum merevisi.")

    allocation, unit = await _allocation_with_unit(
        session,
        organization_id=organization.id,
        allocation_id=plan.unit_allocation_id,
        lock=True,
    )
    fiscal_year = await _fiscal_year(session, organization.id, plan.fiscal_year_id)
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Revisi hanya dapat dilakukan saat tahun anggaran PLANNING.")
    if not unit.is_active or not unit.can_create_budget_plan:
        raise conflict("Unit organisasi tidak diizinkan merevisi rencana anggaran.")

    await _validated_lookup_maps(session, organization_id=organization.id, items=payload.items)
    total = normalize_money(sum((item_amount(item) for item in payload.items), Decimal("0.00")))
    if total > allocation.amount:
        raise conflict("Total rencana anggaran tidak boleh melebihi alokasi unit.")

    next_version_no = plan.current_version_no + 1
    version = BudgetPlanVersion(
        organization_id=organization.id,
        budget_plan_id=plan.id,
        version_no=next_version_no,
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        total_amount=total,
        created_by=actor_user_id,
    )
    session.add(version)
    await session.flush()
    await _replace_items(
        session,
        organization_id=organization.id,
        version=version,
        payload_items=payload.items,
    )

    before = {
        "status": plan.status,
        "version_no": plan.current_version_no,
        "row_version": plan.row_version,
        "rejection_reason": plan.rejection_reason,
    }
    plan.current_version_no = next_version_no
    plan.status = BudgetPlanStatus.DRAFT.value
    plan.submitted_by = None
    plan.submitted_at = None
    plan.approved_by = None
    plan.approved_at = None
    plan.rejection_reason = None
    plan.row_version += 1

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_PLAN_REVISED",
        entity_type="budget_plan",
        entity_id=plan.id,
        before_data=before,
        after_data={
            "status": plan.status,
            "version_no": next_version_no,
            "row_version": plan.row_version,
            "total_amount": str(total),
        },
    )
    await session.commit()
    await session.refresh(plan)
    return await _response(session, plan)


async def list_budget_plan_approvals(
    session: AsyncSession,
    *,
    plan_id: UUID,
    user_id: UUID,
) -> list[BudgetPlanApprovalResponse]:
    organization = await get_default_organization(session)
    plan = await session.scalar(
        select(BudgetPlan).where(
            BudgetPlan.id == plan_id,
            BudgetPlan.organization_id == organization.id,
        )
    )
    if plan is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    if not await _can_read_plan(session, user_id=user_id, plan=plan):
        raise forbidden("Anda tidak memiliki scope untuk rencana anggaran ini.")

    rows = (
        await session.execute(
            select(BudgetPlanApproval, BudgetPlanVersion.version_no)
            .join(BudgetPlanVersion, BudgetPlanVersion.id == BudgetPlanApproval.plan_version_id)
            .where(BudgetPlanApproval.budget_plan_id == plan.id)
            .order_by(BudgetPlanApproval.submission_no.desc())
        )
    ).all()
    return [_approval_response(item, version_no=version_no) for item, version_no in rows]


async def list_pending_budget_plan_approvals(
    session: AsyncSession,
    *,
    user_id: UUID,
    fiscal_year_id: UUID | None = None,
) -> list[BudgetPlanPendingApprovalResponse]:
    organization = await get_default_organization(session)
    statement = (
        select(BudgetPlan, BudgetPlanApproval, BudgetPlanVersion)
        .join(BudgetPlanApproval, BudgetPlanApproval.budget_plan_id == BudgetPlan.id)
        .join(BudgetPlanVersion, BudgetPlanVersion.id == BudgetPlanApproval.plan_version_id)
        .where(
            BudgetPlan.organization_id == organization.id,
            BudgetPlan.status == BudgetPlanStatus.PENDING_APPROVAL.value,
            BudgetPlanApproval.status == BudgetPlanApprovalStatus.PENDING.value,
        )
        .order_by(BudgetPlanApproval.requested_at.asc())
    )
    if fiscal_year_id is not None:
        statement = statement.where(BudgetPlan.fiscal_year_id == fiscal_year_id)
    rows = (await session.execute(statement)).all()

    result: list[BudgetPlanPendingApprovalResponse] = []
    for plan, approval, version in rows:
        if not await can_access_unit(
            session,
            user_id=user_id,
            permission_code="budget_plans.approve",
            unit_id=plan.organization_unit_id,
        ):
            continue
        result.append(
            BudgetPlanPendingApprovalResponse(
                budget_plan=await _response(session, plan),
                approval=_approval_response(approval, version_no=version.version_no),
            )
        )
    return result
