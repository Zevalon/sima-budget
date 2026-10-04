from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.annual_budgets.models import AnnualBudget
from app.modules.annual_budgets.schemas import AnnualBudgetStatus
from app.modules.audit.service import record_audit
from app.modules.auth.repository import get_default_organization
from app.modules.budget_foundation.models import FiscalYear
from app.modules.budget_foundation.schemas import FiscalYearStatus
from app.modules.organizations.models import OrganizationUnit
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.unit_allocations.schemas import (
    UnitAllocationCreateRequest,
    UnitAllocationOverviewResponse,
    UnitAllocationResponse,
    UnitAllocationUpdateRequest,
)

ZERO = Decimal("0.00")


def not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def normalize_amount(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def allocation_response(
    item: UnitAllocation,
    *,
    unit_code: str,
    unit_name: str,
) -> UnitAllocationResponse:
    return UnitAllocationResponse(
        id=item.id,
        fiscal_year_id=item.fiscal_year_id,
        annual_budget_id=item.annual_budget_id,
        organization_unit_id=item.organization_unit_id,
        organization_unit_code=unit_code,
        organization_unit_name=unit_name,
        amount=item.amount,
        notes=item.notes,
        version=item.version,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


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


async def _approved_budget_for_update(
    session: AsyncSession,
    *,
    organization_id: UUID,
    fiscal_year_id: UUID,
) -> AnnualBudget:
    item = await session.scalar(
        select(AnnualBudget)
        .where(
            AnnualBudget.organization_id == organization_id,
            AnnualBudget.fiscal_year_id == fiscal_year_id,
        )
        .with_for_update()
    )
    if item is None:
        raise conflict("Anggaran tahunan belum tersedia untuk tahun anggaran ini.")
    if item.status != AnnualBudgetStatus.APPROVED.value:
        raise conflict("Alokasi unit hanya dapat dibuat dari anggaran tahunan APPROVED.")
    return item


async def _eligible_unit(
    session: AsyncSession,
    *,
    organization_id: UUID,
    organization_unit_id: UUID,
) -> OrganizationUnit:
    unit = await session.scalar(
        select(OrganizationUnit).where(
            OrganizationUnit.id == organization_unit_id,
            OrganizationUnit.organization_id == organization_id,
        )
    )
    if unit is None:
        raise not_found("Unit organisasi tidak ditemukan.")
    if not unit.is_active:
        raise conflict("Unit organisasi tidak aktif.")
    if not unit.can_receive_budget:
        raise conflict("Unit organisasi tidak diizinkan menerima alokasi anggaran.")
    return unit


async def _allocated_total(
    session: AsyncSession,
    *,
    annual_budget_id: UUID,
    exclude_allocation_id: UUID | None = None,
) -> Decimal:
    statement = select(func.sum(UnitAllocation.amount)).where(
        UnitAllocation.annual_budget_id == annual_budget_id
    )
    if exclude_allocation_id is not None:
        statement = statement.where(UnitAllocation.id != exclude_allocation_id)
    value = await session.scalar(statement)
    return normalize_amount(value if value is not None else ZERO)


async def get_unit_allocation_overview(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
) -> UnitAllocationOverviewResponse:
    organization = await get_default_organization(session)
    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=fiscal_year_id,
    )
    annual_budget = await session.scalar(
        select(AnnualBudget).where(
            AnnualBudget.organization_id == organization.id,
            AnnualBudget.fiscal_year_id == fiscal_year.id,
        )
    )

    rows = (
        await session.execute(
            select(UnitAllocation, OrganizationUnit.code, OrganizationUnit.name)
            .join(
                OrganizationUnit,
                OrganizationUnit.id == UnitAllocation.organization_unit_id,
            )
            .where(
                UnitAllocation.organization_id == organization.id,
                UnitAllocation.fiscal_year_id == fiscal_year.id,
            )
            .order_by(OrganizationUnit.name.asc())
        )
    ).all()
    allocations = [
        allocation_response(item, unit_code=unit_code, unit_name=unit_name)
        for item, unit_code, unit_name in rows
    ]
    allocated = normalize_amount(sum((item.amount for item in allocations), ZERO))
    budget_amount = normalize_amount(annual_budget.amount) if annual_budget is not None else ZERO
    remaining = normalize_amount(max(budget_amount - allocated, ZERO))

    return UnitAllocationOverviewResponse(
        fiscal_year_id=fiscal_year.id,
        fiscal_year_code=fiscal_year.code,
        fiscal_year_status=FiscalYearStatus(fiscal_year.status),
        annual_budget_id=annual_budget.id if annual_budget is not None else None,
        annual_budget_status=(
            AnnualBudgetStatus(annual_budget.status) if annual_budget is not None else None
        ),
        annual_budget_amount=budget_amount,
        allocated_amount=allocated,
        remaining_amount=remaining,
        allocations=allocations,
    )


async def create_unit_allocation(
    session: AsyncSession,
    *,
    payload: UnitAllocationCreateRequest,
    actor_user_id: UUID,
) -> UnitAllocationResponse:
    organization = await get_default_organization(session)
    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=payload.fiscal_year_id,
    )
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Alokasi unit hanya dapat diubah saat tahun anggaran PLANNING.")

    annual_budget = await _approved_budget_for_update(
        session,
        organization_id=organization.id,
        fiscal_year_id=fiscal_year.id,
    )
    unit = await _eligible_unit(
        session,
        organization_id=organization.id,
        organization_unit_id=payload.organization_unit_id,
    )

    duplicate = await session.scalar(
        select(UnitAllocation.id).where(
            UnitAllocation.annual_budget_id == annual_budget.id,
            UnitAllocation.organization_unit_id == unit.id,
        )
    )
    if duplicate is not None:
        raise conflict("Unit organisasi ini sudah memiliki alokasi untuk tahun anggaran tersebut.")

    amount = normalize_amount(payload.amount)
    allocated = await _allocated_total(session, annual_budget_id=annual_budget.id)
    if allocated + amount > annual_budget.amount:
        raise conflict("Total alokasi unit tidak boleh melebihi anggaran tahunan yang disetujui.")

    item = UnitAllocation(
        organization_id=organization.id,
        fiscal_year_id=fiscal_year.id,
        annual_budget_id=annual_budget.id,
        organization_unit_id=unit.id,
        amount=amount,
        notes=payload.notes.strip() if payload.notes else None,
        version=1,
    )
    session.add(item)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict(
            "Unit organisasi ini sudah memiliki alokasi untuk tahun anggaran tersebut."
        ) from exc

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="UNIT_ALLOCATION_CREATED",
        entity_type="unit_allocation",
        entity_id=item.id,
        after_data={
            "fiscal_year_id": str(fiscal_year.id),
            "annual_budget_id": str(annual_budget.id),
            "organization_unit_id": str(unit.id),
            "amount": str(item.amount),
            "version": item.version,
        },
    )
    await session.commit()
    await session.refresh(item)
    return allocation_response(item, unit_code=unit.code, unit_name=unit.name)


async def update_unit_allocation(
    session: AsyncSession,
    *,
    allocation_id: UUID,
    payload: UnitAllocationUpdateRequest,
    actor_user_id: UUID,
) -> UnitAllocationResponse:
    organization = await get_default_organization(session)
    existing = (
        await session.execute(
            select(UnitAllocation.fiscal_year_id).where(
                UnitAllocation.id == allocation_id,
                UnitAllocation.organization_id == organization.id,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        raise not_found("Alokasi unit tidak ditemukan.")

    annual_budget = await _approved_budget_for_update(
        session,
        organization_id=organization.id,
        fiscal_year_id=existing,
    )
    item = await session.scalar(
        select(UnitAllocation)
        .where(
            UnitAllocation.id == allocation_id,
            UnitAllocation.organization_id == organization.id,
        )
        .with_for_update()
    )
    if item is None:
        raise not_found("Alokasi unit tidak ditemukan.")

    fiscal_year = await _fiscal_year(
        session,
        organization_id=organization.id,
        fiscal_year_id=item.fiscal_year_id,
    )
    if fiscal_year.status != FiscalYearStatus.PLANNING.value:
        raise conflict("Alokasi unit hanya dapat diubah saat tahun anggaran PLANNING.")
    if item.version != payload.expected_version:
        raise conflict(
            "Alokasi unit sudah berubah sejak halaman dimuat. Muat ulang data sebelum menyimpan."
        )
    changed_fields = payload.model_fields_set - {"expected_version"}
    if not changed_fields:
        raise conflict("Tidak ada perubahan alokasi yang dikirim.")

    unit = await _eligible_unit(
        session,
        organization_id=organization.id,
        organization_unit_id=item.organization_unit_id,
    )
    before = {
        "amount": str(item.amount),
        "notes": item.notes,
        "version": item.version,
    }

    if "amount" in changed_fields and payload.amount is not None:
        amount = normalize_amount(payload.amount)
        allocated_without_current = await _allocated_total(
            session,
            annual_budget_id=annual_budget.id,
            exclude_allocation_id=item.id,
        )
        if allocated_without_current + amount > annual_budget.amount:
            raise conflict(
                "Total alokasi unit tidak boleh melebihi anggaran tahunan yang disetujui."
            )
        item.amount = amount
    if "notes" in changed_fields:
        item.notes = payload.notes.strip() if payload.notes else None

    item.version += 1
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="UNIT_ALLOCATION_UPDATED",
        entity_type="unit_allocation",
        entity_id=item.id,
        before_data=before,
        after_data={
            "amount": str(item.amount),
            "notes": item.notes,
            "version": item.version,
        },
    )
    await session.commit()
    await session.refresh(item)
    return allocation_response(item, unit_code=unit.code, unit_name=unit.name)
