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
    AnnualBudgetApproveRequest,
    AnnualBudgetCreateRequest,
    AnnualBudgetRejectRequest,
    AnnualBudgetResponse,
    AnnualBudgetStatus,
    AnnualBudgetUpdateRequest,
)
from app.modules.audit.service import record_audit
from app.modules.auth.repository import get_default_organization
from app.modules.budget_foundation.models import FiscalYear
from app.modules.budget_foundation.schemas import FiscalYearStatus
from app.modules.settings.service import get_application_setting


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


async def list_pending_annual_budgets(session: AsyncSession) -> list[AnnualBudgetResponse]:
    organization = await get_default_organization(session)
    rows = (
        await session.execute(
            select(AnnualBudget, FiscalYear.code)
            .join(FiscalYear, FiscalYear.id == AnnualBudget.fiscal_year_id)
            .where(
                AnnualBudget.organization_id == organization.id,
                AnnualBudget.status == AnnualBudgetStatus.PENDING_APPROVAL.value,
            )
            .order_by(AnnualBudget.submitted_at.asc(), FiscalYear.start_date.asc())
        )
    ).all()
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
            .with_for_update()
        )
    ).one_or_none()
    if row is None:
        raise not_found("Anggaran tahunan tidak ditemukan.")

    item, fiscal_year = row
    if item.status not in {
        AnnualBudgetStatus.DRAFT.value,
        AnnualBudgetStatus.REJECTED.value,
    }:
        raise conflict("Hanya anggaran tahunan DRAFT atau REJECTED yang dapat diubah.")
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Anggaran tahunan hanya dapat diubah saat tahun anggaran PLANNING.")
    if not payload.model_fields_set:
        raise conflict("Tidak ada perubahan anggaran tahunan yang dikirim.")

    previous_status = item.status
    before = {
        "amount": str(item.amount),
        "notes": item.notes,
        "status": item.status,
        "version": item.version,
        "rejection_reason": item.rejection_reason,
    }
    if "amount" in payload.model_fields_set and payload.amount is not None:
        item.amount = normalize_amount(payload.amount)
    if "notes" in payload.model_fields_set:
        item.notes = payload.notes.strip() if payload.notes else None

    action = "ANNUAL_BUDGET_UPDATED"
    if previous_status == AnnualBudgetStatus.REJECTED.value:
        item.status = AnnualBudgetStatus.DRAFT.value
        item.version += 1
        item.submitted_by = None
        item.submitted_at = None
        item.approved_by = None
        item.approved_at = None
        item.rejection_reason = None
        action = "ANNUAL_BUDGET_REVISED_AFTER_REJECTION"

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action=action,
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
        status=AnnualBudgetApprovalStatus.PENDING.value,
        requested_by=actor_user_id,
        requested_at=now,
    )
    session.add(approval)

    item.status = AnnualBudgetStatus.PENDING_APPROVAL.value
    item.submitted_by = actor_user_id
    item.submitted_at = now
    item.approved_by = None
    item.approved_at = None
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


async def _pending_approval_for_update(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
) -> AnnualBudgetApproval:
    approval = await session.scalar(
        select(AnnualBudgetApproval)
        .where(
            AnnualBudgetApproval.annual_budget_id == annual_budget_id,
            AnnualBudgetApproval.status == AnnualBudgetApprovalStatus.PENDING.value,
        )
        .order_by(AnnualBudgetApproval.submission_no.desc())
        .with_for_update()
    )
    if approval is None:
        raise conflict("Pengajuan persetujuan aktif tidak ditemukan.")
    return approval


async def _budget_for_decision(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
    actor_user_id: UUID,
) -> tuple[AnnualBudget, FiscalYear, AnnualBudgetApproval]:
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
    if item.status != AnnualBudgetStatus.PENDING_APPROVAL.value:
        raise conflict("Hanya anggaran PENDING_APPROVAL yang dapat diputuskan.")
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Keputusan anggaran hanya dapat dilakukan saat tahun anggaran PLANNING.")

    setting = await get_application_setting(session)
    if not setting.allow_self_approval and item.submitted_by == actor_user_id:
        raise conflict("Self-approval tidak diperbolehkan oleh pengaturan aplikasi.")

    approval = await _pending_approval_for_update(
        session,
        annual_budget_id=annual_budget_id,
    )
    return item, fiscal_year, approval


async def approve_annual_budget(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
    payload: AnnualBudgetApproveRequest,
    actor_user_id: UUID,
) -> AnnualBudgetResponse:
    organization = await get_default_organization(session)
    item, fiscal_year, approval = await _budget_for_decision(
        session,
        annual_budget_id=annual_budget_id,
        actor_user_id=actor_user_id,
    )
    now = datetime.now(UTC)
    note = payload.decision_note.strip() if payload.decision_note else None

    approval.status = AnnualBudgetApprovalStatus.APPROVED.value
    approval.decided_by = actor_user_id
    approval.decided_at = now
    approval.decision_note = note

    item.status = AnnualBudgetStatus.APPROVED.value
    item.approved_by = actor_user_id
    item.approved_at = now
    item.rejection_reason = None

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ANNUAL_BUDGET_APPROVED",
        entity_type="annual_budget",
        entity_id=item.id,
        before_data={"status": AnnualBudgetStatus.PENDING_APPROVAL.value},
        after_data={
            "status": item.status,
            "submission_no": approval.submission_no,
            "amount": str(item.amount),
            "decision_note": note,
        },
    )
    await session.commit()
    await session.refresh(item)
    return annual_budget_response(item, fiscal_year.code)


async def reject_annual_budget(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
    payload: AnnualBudgetRejectRequest,
    actor_user_id: UUID,
) -> AnnualBudgetResponse:
    organization = await get_default_organization(session)
    item, fiscal_year, approval = await _budget_for_decision(
        session,
        annual_budget_id=annual_budget_id,
        actor_user_id=actor_user_id,
    )
    reason = payload.reason.strip()
    if len(reason) < 3:
        raise conflict("Alasan penolakan wajib diisi minimal 3 karakter.")

    now = datetime.now(UTC)
    approval.status = AnnualBudgetApprovalStatus.REJECTED.value
    approval.decided_by = actor_user_id
    approval.decided_at = now
    approval.decision_note = reason

    item.status = AnnualBudgetStatus.REJECTED.value
    item.approved_by = None
    item.approved_at = None
    item.rejection_reason = reason

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="ANNUAL_BUDGET_REJECTED",
        entity_type="annual_budget",
        entity_id=item.id,
        before_data={"status": AnnualBudgetStatus.PENDING_APPROVAL.value},
        after_data={
            "status": item.status,
            "submission_no": approval.submission_no,
            "amount": str(item.amount),
            "reason": reason,
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
