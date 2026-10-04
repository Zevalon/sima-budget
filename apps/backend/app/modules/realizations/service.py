from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import record_audit
from app.modules.auth.repository import get_default_organization
from app.modules.authorization.service import can_access_unit
from app.modules.budget_foundation.models import FiscalYear
from app.modules.budget_foundation.schemas import FiscalYearStatus
from app.modules.budget_plans.models import BudgetPlan, BudgetPlanVersion
from app.modules.budget_plans.schemas import BudgetPlanStatus
from app.modules.organizations.models import OrganizationUnit
from app.modules.realizations.models import Realization
from app.modules.realizations.schemas import (
    RealizationContextResponse,
    RealizationCreateRequest,
    RealizationPlanOption,
    RealizationPostRequest,
    RealizationResponse,
    RealizationStatus,
    RealizationUpdateRequest,
)

MONEY_QUANTUM = Decimal("0.01")


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def forbidden(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def normalize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


async def _fiscal_year(
    session: AsyncSession,
    *,
    organization_id: UUID,
    fiscal_year_id: UUID,
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


async def _plan_version(
    session: AsyncSession,
    *,
    plan: BudgetPlan,
) -> BudgetPlanVersion:
    version = await session.scalar(
        select(BudgetPlanVersion).where(
            BudgetPlanVersion.budget_plan_id == plan.id,
            BudgetPlanVersion.version_no == plan.current_version_no,
        )
    )
    if version is None:
        raise RuntimeError("Versi rencana anggaran tidak konsisten.")
    return version


async def _plan_with_unit(
    session: AsyncSession,
    *,
    organization_id: UUID,
    plan_id: UUID,
    lock: bool = False,
) -> tuple[BudgetPlan, OrganizationUnit]:
    statement = (
        select(BudgetPlan, OrganizationUnit)
        .join(OrganizationUnit, OrganizationUnit.id == BudgetPlan.organization_unit_id)
        .where(
            BudgetPlan.id == plan_id,
            BudgetPlan.organization_id == organization_id,
        )
    )
    if lock:
        statement = statement.with_for_update(of=BudgetPlan)
    row = (await session.execute(statement)).first()
    if row is None:
        raise not_found("Rencana anggaran tidak ditemukan.")
    plan, unit = row
    return plan, unit


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
        raise forbidden("Anda tidak memiliki scope untuk realisasi unit ini.")


async def _plan_financials(
    session: AsyncSession,
    *,
    plan_id: UUID,
    approved_amount: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    realized = await session.scalar(
        select(func.sum(Realization.amount)).where(
            Realization.budget_plan_id == plan_id,
            Realization.status == RealizationStatus.POSTED.value,
        )
    )
    pipeline = await session.scalar(
        select(func.sum(Realization.amount)).where(
            Realization.budget_plan_id == plan_id,
            Realization.status == RealizationStatus.DRAFT.value,
        )
    )
    realized_amount = normalize_money(realized or Decimal("0.00"))
    pipeline_amount = normalize_money(pipeline or Decimal("0.00"))
    remaining_amount = normalize_money(max(approved_amount - realized_amount, Decimal("0.00")))
    return realized_amount, pipeline_amount, remaining_amount


def _validate_realization_date(fiscal_year: FiscalYear, value: date) -> None:
    if value < fiscal_year.start_date or value > fiscal_year.end_date:
        raise conflict("Tanggal realisasi harus berada dalam periode tahun anggaran.")


async def _response(session: AsyncSession, item: Realization) -> RealizationResponse:
    fiscal_year = await _fiscal_year(
        session,
        organization_id=item.organization_id,
        fiscal_year_id=item.fiscal_year_id,
    )
    plan, unit = await _plan_with_unit(
        session,
        organization_id=item.organization_id,
        plan_id=item.budget_plan_id,
    )
    version = await session.scalar(
        select(BudgetPlanVersion).where(BudgetPlanVersion.id == item.plan_version_id)
    )
    if version is None:
        raise RuntimeError("Versi rencana pada realisasi tidak konsisten.")
    realized, pipeline, remaining = await _plan_financials(
        session,
        plan_id=plan.id,
        approved_amount=version.total_amount,
    )
    return RealizationResponse(
        id=item.id,
        fiscal_year_id=fiscal_year.id,
        fiscal_year_code=fiscal_year.code,
        budget_plan_id=plan.id,
        plan_version_id=version.id,
        plan_number=plan.plan_number,
        plan_title=version.title,
        plan_approved_amount=version.total_amount,
        plan_realized_amount=realized,
        plan_draft_pipeline_amount=pipeline,
        plan_remaining_amount=remaining,
        organization_unit_id=unit.id,
        organization_unit_code=unit.code,
        organization_unit_name=unit.name,
        realization_number=item.realization_number,
        status=RealizationStatus(item.status),
        realization_date=item.realization_date,
        reference_number=item.reference_number,
        description=item.description,
        vendor_name=item.vendor_name,
        amount=item.amount,
        row_version=item.row_version,
        created_by=item.created_by,
        posted_by=item.posted_by,
        posted_at=item.posted_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


async def get_realization_context(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    user_id: UUID,
) -> RealizationContextResponse:
    organization = await get_default_organization(session)
    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=fiscal_year_id,
    )
    rows = (
        await session.execute(
            select(BudgetPlan, BudgetPlanVersion, OrganizationUnit)
            .join(
                BudgetPlanVersion,
                and_(
                    BudgetPlanVersion.budget_plan_id == BudgetPlan.id,
                    BudgetPlanVersion.version_no == BudgetPlan.current_version_no,
                ),
            )
            .join(OrganizationUnit, OrganizationUnit.id == BudgetPlan.organization_unit_id)
            .where(
                BudgetPlan.organization_id == organization.id,
                BudgetPlan.fiscal_year_id == fiscal_year.id,
                BudgetPlan.status == BudgetPlanStatus.APPROVED.value,
            )
            .order_by(OrganizationUnit.name.asc(), BudgetPlan.plan_number.asc())
        )
    ).all()

    plans: list[RealizationPlanOption] = []
    for plan, version, unit in rows:
        if not await can_access_unit(
            session,
            user_id=user_id,
            permission_code="realizations.view",
            unit_id=unit.id,
        ):
            continue
        realized, pipeline, remaining = await _plan_financials(
            session,
            plan_id=plan.id,
            approved_amount=version.total_amount,
        )
        plans.append(
            RealizationPlanOption(
                budget_plan_id=plan.id,
                plan_version_id=version.id,
                organization_unit_id=unit.id,
                organization_unit_code=unit.code,
                organization_unit_name=unit.name,
                plan_number=plan.plan_number,
                title=version.title,
                approved_amount=version.total_amount,
                realized_amount=realized,
                draft_pipeline_amount=pipeline,
                remaining_amount=remaining,
            )
        )

    return RealizationContextResponse(
        fiscal_year_id=fiscal_year.id,
        fiscal_year_code=fiscal_year.code,
        fiscal_year_status=FiscalYearStatus(fiscal_year.status),
        scope_approved_amount=normalize_money(
            sum((plan.approved_amount for plan in plans), Decimal("0.00"))
        ),
        scope_realized_amount=normalize_money(
            sum((plan.realized_amount for plan in plans), Decimal("0.00"))
        ),
        scope_draft_pipeline_amount=normalize_money(
            sum((plan.draft_pipeline_amount for plan in plans), Decimal("0.00"))
        ),
        scope_remaining_amount=normalize_money(
            sum((plan.remaining_amount for plan in plans), Decimal("0.00"))
        ),
        plans=plans,
    )


async def list_realizations(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    user_id: UUID,
) -> list[RealizationResponse]:
    organization = await get_default_organization(session)
    await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=fiscal_year_id,
    )
    items = (
        await session.scalars(
            select(Realization)
            .where(
                Realization.organization_id == organization.id,
                Realization.fiscal_year_id == fiscal_year_id,
            )
            .order_by(Realization.realization_date.desc(), Realization.created_at.desc())
        )
    ).all()
    visible: list[RealizationResponse] = []
    for item in items:
        if await can_access_unit(
            session,
            user_id=user_id,
            permission_code="realizations.view",
            unit_id=item.organization_unit_id,
        ):
            visible.append(await _response(session, item))
    return visible


async def get_realization(
    session: AsyncSession,
    *,
    realization_id: UUID,
    user_id: UUID,
) -> RealizationResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(Realization).where(
            Realization.id == realization_id,
            Realization.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Realisasi tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=user_id,
        permission_code="realizations.view",
        unit_id=item.organization_unit_id,
    )
    return await _response(session, item)


async def create_realization(
    session: AsyncSession,
    *,
    payload: RealizationCreateRequest,
    actor_user_id: UUID,
) -> RealizationResponse:
    organization = await get_default_organization(session)
    plan, unit = await _plan_with_unit(
        session,
        organization_id=organization.id,
        plan_id=payload.budget_plan_id,
    )
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="realizations.create",
        unit_id=unit.id,
    )
    if plan.status != BudgetPlanStatus.APPROVED.value:
        raise conflict("Realisasi hanya dapat dibuat untuk rencana anggaran APPROVED.")

    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=plan.fiscal_year_id,
    )
    if fiscal_year.status != FiscalYearStatus.ACTIVE.value:
        raise conflict("Realisasi hanya dapat dibuat saat tahun anggaran ACTIVE.")
    _validate_realization_date(fiscal_year, payload.realization_date)

    version = await _plan_version(session, plan=plan)
    _, _, remaining = await _plan_financials(
        session,
        plan_id=plan.id,
        approved_amount=version.total_amount,
    )
    amount = normalize_money(payload.amount)
    if amount > remaining:
        raise conflict(
            "Nilai draft realisasi tidak boleh melebihi sisa rencana yang dapat direalisasi."
        )

    item = Realization(
        organization_id=organization.id,
        fiscal_year_id=fiscal_year.id,
        budget_plan_id=plan.id,
        plan_version_id=version.id,
        organization_unit_id=unit.id,
        realization_number=f"RLZ-{fiscal_year.code}-{unit.code}-{uuid4().hex[:8].upper()}",
        status=RealizationStatus.DRAFT.value,
        realization_date=payload.realization_date,
        reference_number=payload.reference_number.strip(),
        description=payload.description.strip(),
        vendor_name=payload.vendor_name.strip() if payload.vendor_name else None,
        amount=amount,
        row_version=1,
        created_by=actor_user_id,
    )
    session.add(item)
    await session.flush()
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="REALIZATION_CREATED",
        entity_type="realization",
        entity_id=item.id,
        after_data={
            "realization_number": item.realization_number,
            "budget_plan_id": str(plan.id),
            "plan_version_id": str(version.id),
            "amount": str(amount),
            "status": item.status,
        },
    )
    await session.commit()
    await session.refresh(item)
    return await _response(session, item)


async def update_realization(
    session: AsyncSession,
    *,
    realization_id: UUID,
    payload: RealizationUpdateRequest,
    actor_user_id: UUID,
) -> RealizationResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(Realization)
        .where(
            Realization.id == realization_id,
            Realization.organization_id == organization.id,
        )
        .with_for_update()
    )
    if item is None:
        raise not_found("Realisasi tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="realizations.update",
        unit_id=item.organization_unit_id,
    )
    if item.status != RealizationStatus.DRAFT.value:
        raise conflict("Hanya draft realisasi yang dapat diubah.")
    if item.row_version != payload.expected_row_version:
        raise conflict("Data realisasi telah berubah. Muat ulang halaman sebelum menyimpan.")

    plan, _ = await _plan_with_unit(
        session,
        organization_id=organization.id,
        plan_id=item.budget_plan_id,
    )
    if plan.status != BudgetPlanStatus.APPROVED.value:
        raise conflict("Rencana anggaran tidak lagi berstatus APPROVED.")
    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=item.fiscal_year_id,
    )
    if fiscal_year.status != FiscalYearStatus.ACTIVE.value:
        raise conflict("Draft realisasi hanya dapat diubah saat tahun anggaran ACTIVE.")
    _validate_realization_date(fiscal_year, payload.realization_date)

    version = await session.scalar(
        select(BudgetPlanVersion).where(BudgetPlanVersion.id == item.plan_version_id)
    )
    if version is None:
        raise RuntimeError("Versi rencana pada realisasi tidak konsisten.")
    _, _, remaining = await _plan_financials(
        session,
        plan_id=plan.id,
        approved_amount=version.total_amount,
    )
    amount = normalize_money(payload.amount)
    if amount > remaining:
        raise conflict(
            "Nilai draft realisasi tidak boleh melebihi sisa rencana yang dapat direalisasi."
        )

    before = {
        "realization_date": item.realization_date.isoformat(),
        "reference_number": item.reference_number,
        "description": item.description,
        "vendor_name": item.vendor_name,
        "amount": str(item.amount),
        "row_version": item.row_version,
    }
    item.realization_date = payload.realization_date
    item.reference_number = payload.reference_number.strip()
    item.description = payload.description.strip()
    item.vendor_name = payload.vendor_name.strip() if payload.vendor_name else None
    item.amount = amount
    item.row_version += 1
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="REALIZATION_UPDATED",
        entity_type="realization",
        entity_id=item.id,
        before_data=before,
        after_data={
            "realization_date": item.realization_date.isoformat(),
            "reference_number": item.reference_number,
            "description": item.description,
            "vendor_name": item.vendor_name,
            "amount": str(item.amount),
            "row_version": item.row_version,
        },
    )
    await session.commit()
    await session.refresh(item)
    return await _response(session, item)


async def post_realization(
    session: AsyncSession,
    *,
    realization_id: UUID,
    payload: RealizationPostRequest,
    actor_user_id: UUID,
) -> RealizationResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(Realization)
        .where(
            Realization.id == realization_id,
            Realization.organization_id == organization.id,
        )
        .with_for_update()
    )
    if item is None:
        raise not_found("Realisasi tidak ditemukan.")
    await _assert_unit_permission(
        session,
        user_id=actor_user_id,
        permission_code="realizations.post",
        unit_id=item.organization_unit_id,
    )
    if item.status != RealizationStatus.DRAFT.value:
        raise conflict("Hanya draft realisasi yang dapat diposting.")
    if item.row_version != payload.expected_row_version:
        raise conflict("Data realisasi telah berubah. Muat ulang sebelum posting.")

    plan, _ = await _plan_with_unit(
        session,
        organization_id=organization.id,
        plan_id=item.budget_plan_id,
        lock=True,
    )
    if plan.status != BudgetPlanStatus.APPROVED.value:
        raise conflict("Rencana anggaran tidak lagi berstatus APPROVED.")
    if item.plan_version_id != (await _plan_version(session, plan=plan)).id:
        raise conflict("Versi rencana realisasi tidak lagi sesuai dengan versi APPROVED.")

    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=item.fiscal_year_id,
    )
    if fiscal_year.status != FiscalYearStatus.ACTIVE.value:
        raise conflict("Realisasi hanya dapat diposting saat tahun anggaran ACTIVE.")
    version = await _plan_version(session, plan=plan)
    realized, _, _ = await _plan_financials(
        session,
        plan_id=plan.id,
        approved_amount=version.total_amount,
    )
    if normalize_money(realized + item.amount) > version.total_amount:
        raise conflict("Total realisasi tidak boleh melebihi nilai rencana anggaran APPROVED.")

    now = datetime.now(UTC)
    item.status = RealizationStatus.POSTED.value
    item.posted_by = actor_user_id
    item.posted_at = now
    item.row_version += 1
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="REALIZATION_POSTED",
        entity_type="realization",
        entity_id=item.id,
        before_data={"status": RealizationStatus.DRAFT.value},
        after_data={
            "status": RealizationStatus.POSTED.value,
            "amount": str(item.amount),
            "row_version": item.row_version,
        },
        metadata_json={
            "budget_plan_id": str(plan.id),
            "plan_version_id": str(version.id),
        },
    )
    await session.commit()
    await session.refresh(item)
    return await _response(session, item)
