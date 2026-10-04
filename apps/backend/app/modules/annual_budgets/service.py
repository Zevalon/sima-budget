from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.annual_budgets.models import AnnualBudget, AnnualBudgetApproval
from app.modules.annual_budgets.schemas import (
    AnnualBudgetApprovalResponse,
    AnnualBudgetApprovalStatus,
    AnnualBudgetCreateRequest,
    AnnualBudgetResponse,
    AnnualBudgetStatus,
    AnnualBudgetUpdateRequest,
)
from app.modules.audit.service import record_audit
from app.modules.auth.repository import get_default_organization
from app.modules.budget_foundation.models import FiscalYear
from app.modules.budget_foundation.schemas import FiscalYearStatus


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def normalize_amount(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def annual_budget_response(item: AnnualBudget, fiscal_year_code: str) -> AnnualBudgetResponse:
    return AnnualBudgetResponse(
        id=item.id,
        fiscal_year_id=item.fiscal_year_id,
        fiscal_year_code=fiscal_year_code,
        amount=item.amount,
        notes=item.notes,
        status=AnnualBudgetStatus(item.status),
        version=item.version,
        submitted_by=item.submitted_by,
        submitted_at=item.submitted_at,
        approved_by=item.approved_by,
        approved_at=item.approved_at,
        rejection_reason=item.rejection_reason,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def approval_response(item: AnnualBudgetApproval) -> AnnualBudgetApprovalResponse:
    return AnnualBudgetApprovalResponse(
        id=item.id,
        annual_budget_id=item.annual_budget_id,
        submission_no=item.submission_no,
        status=AnnualBudgetApprovalStatus(item.status),
        requested_by=item.requested_by,
        requested_at=item.requested_at,
        decided_by=item.decided_by,
        decided_at=item.decided_at,
        decision_note=item.decision_note,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


async def _get_fiscal_year(
    session: AsyncSession,
    *,
    organization_id: UUID,
    fiscal_year_id: UUID,
) -> FiscalYear:
    fiscal_year = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.id == fiscal_year_id,
            FiscalYear.organization_id == organization_id,
        )
    )
    if fiscal_year is None:
        raise not_found("Tahun anggaran tidak ditemukan.")
    return fiscal_year


async def list_annual_budgets(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID | None = None,
) -> list[AnnualBudgetResponse]:
    organization = await get_default_organization(session)
    statement = (
        select(AnnualBudget, FiscalYear.code)
        .join(FiscalYear, FiscalYear.id == AnnualBudget.fiscal_year_id)
        .where(AnnualBudget.organization_id == organization.id)
        .order_by(FiscalYear.start_date.desc())
    )
    if fiscal_year_id is not None:
        statement = statement.where(AnnualBudget.fiscal_year_id == fiscal_year_id)

    rows = (await session.execute(statement)).all()
    return [annual_budget_response(item, fiscal_code) for item, fiscal_code in rows]


async def get_annual_budget(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
) -> AnnualBudgetResponse:
    organization = await get_default_organization(session)
    row = (
        await session.execute(
            select(AnnualBudget, FiscalYear.code)
            .join(FiscalYear, FiscalYear.id == AnnualBudget.fiscal_year_id)
            .where(
                AnnualBudget.id == annual_budget_id,
                AnnualBudget.organization_id == organization.id,
            )
        )
    ).one_or_none()
    if row is None:
        raise not_found("Anggaran tahunan tidak ditemukan.")
    item, fiscal_code = row
    return annual_budget_response(item, fiscal_code)


async def create_annual_budget(
    session: AsyncSession,
    *,
    payload: AnnualBudgetCreateRequest,
    actor_user_id: UUID,
) -> AnnualBudgetResponse:
    organization = await get_default_organization(session)
    fiscal_year = await _get_fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=payload.fiscal_year_id,
    )
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict(
            "Anggaran tahunan hanya dapat dibuat saat tahun anggaran berstatus PLANNING."
        )

    duplicate = await session.scalar(
        select(AnnualBudget.id).where(
            AnnualBudget.organization_id == organization.id,
            AnnualBudget.fiscal_year_id == fiscal_year.id,
        )
    )
    if duplicate is not None:
        raise conflict("Anggaran tahunan untuk tahun anggaran ini sudah tersedia.")

    item = AnnualBudget(
        organization_id=organization.id,
        fiscal_year_id=fiscal_year.id,
        amount=normalize_amount(payload.amount),
        notes=payload.notes.strip() if payload.notes else None,
        status=AnnualBudgetStatus.DRAFT.value,
        version=1,
    )
    session.add(item)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict("Anggaran tahunan untuk tahun anggaran ini sudah tersedia.") from exc

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ANNUAL_BUDGET_CREATED",
        entity_type="annual_budget",
        entity_id=item.id,
        after_data={
            "fiscal_year_id": str(item.fiscal_year_id),
            "amount": str(item.amount),
            "status": item.status,
            "version": item.version,
        },
    )
    await session.commit()
    await session.refresh(item)
    return annual_budget_response(item, fiscal_year.code)


async def update_annual_budget(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
    payload: AnnualBudgetUpdateRequest,
    actor_user_id: UUID,
) -> AnnualBudgetResponse:
    organization = await get_default_organization(session)
    row = (
        await session.execute(
            select(AnnualBudget, FiscalYear)
            .join(FiscalYear, FiscalYear.id == AnnualBudget.fiscal_year_id)
            .where(
                AnnualBudget.id == annual_budget_id,
                AnnualBudget.organization_id == organization.id,
            )
        )
    ).one_or_none()
    if row is None:
        raise not_found("Anggaran tahunan tidak ditemukan.")

    item, fiscal_year = row
    if item.status != AnnualBudgetStatus.DRAFT.value:
        raise conflict("Hanya anggaran tahunan DRAFT yang dapat diubah.")
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Anggaran tahunan hanya dapat diubah saat tahun anggaran PLANNING.")

    before = {
        "amount": str(item.amount),
        "notes": item.notes,
        "status": item.status,
        "version": item.version,
    }
    if "amount" in payload.model_fields_set and payload.amount is not None:
        item.amount = normalize_amount(payload.amount)
    if "notes" in payload.model_fields_set:
        item.notes = payload.notes.strip() if payload.notes else None

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ANNUAL_BUDGET_UPDATED",
        entity_type="annual_budget",
        entity_id=item.id,
        before_data=before,
        after_data={
            "amount": str(item.amount),
            "notes": item.notes,
            "status": item.status,
            "version": item.version,
        },
    )
    await session.commit()
    await session.refresh(item)
    return annual_budget_response(item, fiscal_year.code)


async def submit_annual_budget(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
    actor_user_id: UUID,
) -> AnnualBudgetResponse:
    organization = await get_default_organization(session)
    row = (
        await session.execute(
            select(AnnualBudget, FiscalYear)
            .join(FiscalYear, FiscalYear.id == AnnualBudget.fiscal_year_id)
            .where(
                AnnualBudget.id == annual_budget_id,
                AnnualBudget.organization_id == organization.id,
            )
            .with_for_update()
        )
    ).one_or_none()
    if row is None:
        raise not_found("Anggaran tahunan tidak ditemukan.")

    item, fiscal_year = row
    if item.status != AnnualBudgetStatus.DRAFT.value:
        raise conflict("Hanya anggaran tahunan DRAFT yang dapat diajukan untuk persetujuan.")
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Pengajuan hanya dapat dilakukan saat tahun anggaran PLANNING.")

    latest_submission = await session.scalar(
        select(func.max(AnnualBudgetApproval.submission_no)).where(
            AnnualBudgetApproval.annual_budget_id == item.id
        )
    )
    submission_no = int(latest_submission or 0) + 1
    now = datetime.now(UTC)
    approval = AnnualBudgetApproval(
        annual_budget_id=item.id,
        submission_no=submission_no,
        status="PENDING",
        requested_by=actor_user_id,
        requested_at=now,
    )
    session.add(approval)

    item.status = AnnualBudgetStatus.PENDING_APPROVAL.value
    item.submitted_by = actor_user_id
    item.submitted_at = now
    item.rejection_reason = None

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ANNUAL_BUDGET_SUBMITTED",
        entity_type="annual_budget",
        entity_id=item.id,
        before_data={"status": AnnualBudgetStatus.DRAFT.value},
        after_data={
            "status": item.status,
            "submission_no": submission_no,
            "amount": str(item.amount),
        },
    )
    await session.commit()
    await session.refresh(item)
    return annual_budget_response(item, fiscal_year.code)


async def list_annual_budget_approvals(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
) -> list[AnnualBudgetApprovalResponse]:
    organization = await get_default_organization(session)
    exists = await session.scalar(
        select(AnnualBudget.id).where(
            AnnualBudget.id == annual_budget_id,
            AnnualBudget.organization_id == organization.id,
        )
    )
    if exists is None:
        raise not_found("Anggaran tahunan tidak ditemukan.")

    items = (
        await session.scalars(
            select(AnnualBudgetApproval)
            .where(AnnualBudgetApproval.annual_budget_id == annual_budget_id)
            .order_by(AnnualBudgetApproval.submission_no.desc())
        )
    ).all()
    return [approval_response(item) for item in items]
