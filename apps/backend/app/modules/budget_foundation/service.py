from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.service import record_audit
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.budget_foundation.schemas import (
    BudgetCategoryCreateRequest,
    BudgetCategoryResponse,
    BudgetCategoryUpdateRequest,
    FiscalYearCreateRequest,
    FiscalYearReopenRequest,
    FiscalYearResponse,
    FiscalYearStatus,
    FiscalYearTransitionRequest,
    FiscalYearUpdateRequest,
    UnitOfMeasureCreateRequest,
    UnitOfMeasureResponse,
    UnitOfMeasureUpdateRequest,
)
from app.modules.organizations.models import Organization

LEGAL_TRANSITIONS: dict[FiscalYearStatus, FiscalYearStatus] = {
    FiscalYearStatus.DRAFT: FiscalYearStatus.PLANNING,
    FiscalYearStatus.PLANNING: FiscalYearStatus.ACTIVE,
    FiscalYearStatus.ACTIVE: FiscalYearStatus.CLOSED,
    FiscalYearStatus.CLOSED: FiscalYearStatus.ARCHIVED,
}


def conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


async def get_default_organization(session: AsyncSession) -> Organization:
    organization = await session.scalar(select(Organization).where(Organization.code == "DEFAULT"))
    if organization is None:
        raise RuntimeError("Default organization belum tersedia.")
    return organization


def fiscal_year_response(item: FiscalYear) -> FiscalYearResponse:
    return FiscalYearResponse(
        id=item.id,
        code=item.code,
        year=item.year,
        start_date=item.start_date,
        end_date=item.end_date,
        status=FiscalYearStatus(item.status),
        reopened_at=item.reopened_at,
        reopened_by=item.reopened_by,
        reopen_reason=item.reopen_reason,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def category_response(item: BudgetCategory) -> BudgetCategoryResponse:
    return BudgetCategoryResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        description=item.description,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def uom_response(item: UnitOfMeasure) -> UnitOfMeasureResponse:
    return UnitOfMeasureResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


async def list_fiscal_years(session: AsyncSession) -> list[FiscalYearResponse]:
    organization = await get_default_organization(session)
    items = (
        await session.scalars(
            select(FiscalYear)
            .where(FiscalYear.organization_id == organization.id)
            .order_by(FiscalYear.start_date.desc(), FiscalYear.code.desc())
        )
    ).all()
    return [fiscal_year_response(item) for item in items]


async def create_fiscal_year(
    session: AsyncSession,
    *,
    payload: FiscalYearCreateRequest,
    actor_user_id: UUID,
) -> FiscalYearResponse:
    organization = await get_default_organization(session)
    code = payload.code.strip().upper()

    existing = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.organization_id == organization.id,
            FiscalYear.code == code,
        )
    )
    if existing is not None:
        raise conflict("Kode tahun anggaran sudah digunakan.")

    item = FiscalYear(
        organization_id=organization.id,
        code=code,
        year=payload.year,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=FiscalYearStatus.DRAFT.value,
    )
    session.add(item)
    await session.flush()

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="FISCAL_YEAR_CREATED",
        entity_type="fiscal_year",
        entity_id=item.id,
        after_data={
            "code": item.code,
            "year": item.year,
            "start_date": item.start_date.isoformat(),
            "end_date": item.end_date.isoformat(),
            "status": item.status,
        },
    )
    await session.commit()
    await session.refresh(item)
    return fiscal_year_response(item)


async def update_fiscal_year(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    payload: FiscalYearUpdateRequest,
    actor_user_id: UUID,
) -> FiscalYearResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.id == fiscal_year_id,
            FiscalYear.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Tahun anggaran tidak ditemukan.")
    if item.status not in {FiscalYearStatus.DRAFT.value, FiscalYearStatus.PLANNING.value}:
        raise conflict("Tahun anggaran hanya dapat diubah saat DRAFT atau PLANNING.")

    before = fiscal_year_response(item).model_dump(mode="json")
    updates = payload.model_dump(exclude_unset=True)

    if "code" in updates and updates["code"] is not None:
        next_code = str(updates["code"]).strip().upper()
        duplicate = await session.scalar(
            select(FiscalYear.id).where(
                FiscalYear.organization_id == organization.id,
                FiscalYear.code == next_code,
                FiscalYear.id != item.id,
            )
        )
        if duplicate is not None:
            raise conflict("Kode tahun anggaran sudah digunakan.")
        item.code = next_code
    if "year" in updates:
        item.year = updates["year"]
    if "start_date" in updates and updates["start_date"] is not None:
        item.start_date = updates["start_date"]
    if "end_date" in updates and updates["end_date"] is not None:
        item.end_date = updates["end_date"]

    if item.start_date >= item.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tanggal mulai harus lebih awal daripada tanggal selesai.",
        )

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="FISCAL_YEAR_UPDATED",
        entity_type="fiscal_year",
        entity_id=item.id,
        before_data=before,
        after_data=fiscal_year_response(item).model_dump(mode="json"),
    )
    await session.commit()
    await session.refresh(item)
    return fiscal_year_response(item)


async def transition_fiscal_year(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    payload: FiscalYearTransitionRequest,
    actor_user_id: UUID,
) -> FiscalYearResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.id == fiscal_year_id,
            FiscalYear.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Tahun anggaran tidak ditemukan.")

    current = FiscalYearStatus(item.status)
    expected = LEGAL_TRANSITIONS.get(current)
    if expected is None or payload.target_status != expected:
        raise conflict(
            f"Transisi {current.value} ke {payload.target_status.value} tidak diperbolehkan."
        )

    before = current.value
    item.status = payload.target_status.value
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        if payload.target_status == FiscalYearStatus.ACTIVE:
            raise conflict("Hanya satu tahun anggaran ACTIVE yang diperbolehkan.") from exc
        raise

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="FISCAL_YEAR_TRANSITIONED",
        entity_type="fiscal_year",
        entity_id=item.id,
        before_data={"status": before},
        after_data={"status": item.status},
        metadata_json={"reason": payload.reason} if payload.reason else None,
    )
    await session.commit()
    await session.refresh(item)
    return fiscal_year_response(item)


async def reopen_fiscal_year(
    session: AsyncSession,
    *,
    fiscal_year_id: UUID,
    payload: FiscalYearReopenRequest,
    actor_user_id: UUID,
) -> FiscalYearResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(FiscalYear).where(
            FiscalYear.id == fiscal_year_id,
            FiscalYear.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Tahun anggaran tidak ditemukan.")
    if item.status != FiscalYearStatus.CLOSED.value:
        raise conflict("Hanya tahun anggaran CLOSED yang dapat dibuka kembali.")

    item.status = FiscalYearStatus.ACTIVE.value
    item.reopened_at = datetime.now(UTC)
    item.reopened_by = actor_user_id
    item.reopen_reason = payload.reason.strip()

    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise conflict(
            "Tahun anggaran tidak dapat dibuka kembali karena sudah ada tahun ACTIVE."
        ) from exc

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="FISCAL_YEAR_REOPENED",
        entity_type="fiscal_year",
        entity_id=item.id,
        after_data={"status": item.status},
        metadata_json={"reason": item.reopen_reason},
    )
    await session.commit()
    await session.refresh(item)
    return fiscal_year_response(item)


async def list_budget_categories(session: AsyncSession) -> list[BudgetCategoryResponse]:
    organization = await get_default_organization(session)
    items = (
        await session.scalars(
            select(BudgetCategory)
            .where(BudgetCategory.organization_id == organization.id)
            .order_by(BudgetCategory.is_active.desc(), BudgetCategory.code)
        )
    ).all()
    return [category_response(item) for item in items]


async def create_budget_category(
    session: AsyncSession,
    *,
    payload: BudgetCategoryCreateRequest,
    actor_user_id: UUID,
) -> BudgetCategoryResponse:
    organization = await get_default_organization(session)
    code = payload.code.strip().upper()
    duplicate = await session.scalar(
        select(BudgetCategory.id).where(
            BudgetCategory.organization_id == organization.id,
            BudgetCategory.code == code,
        )
    )
    if duplicate is not None:
        raise conflict("Kode kategori anggaran sudah digunakan.")

    item = BudgetCategory(
        organization_id=organization.id,
        code=code,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        is_active=True,
    )
    session.add(item)
    await session.flush()
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_CATEGORY_CREATED",
        entity_type="budget_category",
        entity_id=item.id,
        after_data={"code": item.code, "name": item.name},
    )
    await session.commit()
    await session.refresh(item)
    return category_response(item)


async def update_budget_category(
    session: AsyncSession,
    *,
    category_id: UUID,
    payload: BudgetCategoryUpdateRequest,
    actor_user_id: UUID,
) -> BudgetCategoryResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(BudgetCategory).where(
            BudgetCategory.id == category_id,
            BudgetCategory.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Kategori anggaran tidak ditemukan.")
    if not item.is_active:
        raise conflict("Kategori nonaktif tidak dapat diubah.")

    before = {"name": item.name, "description": item.description}
    if payload.name is not None:
        item.name = payload.name.strip()
    if "description" in payload.model_fields_set:
        item.description = payload.description.strip() if payload.description else None

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_CATEGORY_UPDATED",
        entity_type="budget_category",
        entity_id=item.id,
        before_data=before,
        after_data={"name": item.name, "description": item.description},
    )
    await session.commit()
    await session.refresh(item)
    return category_response(item)


async def deactivate_budget_category(
    session: AsyncSession,
    *,
    category_id: UUID,
    actor_user_id: UUID,
) -> None:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(BudgetCategory).where(
            BudgetCategory.id == category_id,
            BudgetCategory.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Kategori anggaran tidak ditemukan.")
    if not item.is_active:
        return
    item.is_active = False
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="BUDGET_CATEGORY_DEACTIVATED",
        entity_type="budget_category",
        entity_id=item.id,
    )
    await session.commit()


async def list_units_of_measure(session: AsyncSession) -> list[UnitOfMeasureResponse]:
    organization = await get_default_organization(session)
    items = (
        await session.scalars(
            select(UnitOfMeasure)
            .where(UnitOfMeasure.organization_id == organization.id)
            .order_by(UnitOfMeasure.is_active.desc(), UnitOfMeasure.code)
        )
    ).all()
    return [uom_response(item) for item in items]


async def create_unit_of_measure(
    session: AsyncSession,
    *,
    payload: UnitOfMeasureCreateRequest,
    actor_user_id: UUID,
) -> UnitOfMeasureResponse:
    organization = await get_default_organization(session)
    code = payload.code.strip().upper()
    duplicate = await session.scalar(
        select(UnitOfMeasure.id).where(
            UnitOfMeasure.organization_id == organization.id,
            UnitOfMeasure.code == code,
        )
    )
    if duplicate is not None:
        raise conflict("Kode satuan sudah digunakan.")

    item = UnitOfMeasure(
        organization_id=organization.id,
        code=code,
        name=payload.name.strip(),
        is_active=True,
    )
    session.add(item)
    await session.flush()
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="UNIT_OF_MEASURE_CREATED",
        entity_type="unit_of_measure",
        entity_id=item.id,
        after_data={"code": item.code, "name": item.name},
    )
    await session.commit()
    await session.refresh(item)
    return uom_response(item)


async def update_unit_of_measure(
    session: AsyncSession,
    *,
    unit_id: UUID,
    payload: UnitOfMeasureUpdateRequest,
    actor_user_id: UUID,
) -> UnitOfMeasureResponse:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(UnitOfMeasure).where(
            UnitOfMeasure.id == unit_id,
            UnitOfMeasure.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Satuan tidak ditemukan.")
    if not item.is_active:
        raise conflict("Satuan nonaktif tidak dapat diubah.")
    if payload.name is not None:
        item.name = payload.name.strip()

    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="UNIT_OF_MEASURE_UPDATED",
        entity_type="unit_of_measure",
        entity_id=item.id,
        after_data={"code": item.code, "name": item.name},
    )
    await session.commit()
    await session.refresh(item)
    return uom_response(item)


async def deactivate_unit_of_measure(
    session: AsyncSession,
    *,
    unit_id: UUID,
    actor_user_id: UUID,
) -> None:
    organization = await get_default_organization(session)
    item = await session.scalar(
        select(UnitOfMeasure).where(
            UnitOfMeasure.id == unit_id,
            UnitOfMeasure.organization_id == organization.id,
        )
    )
    if item is None:
        raise not_found("Satuan tidak ditemukan.")
    if not item.is_active:
        return
    item.is_active = False
    record_audit(
        session,
        organization_id=organization.id,
        actor_user_id=actor_user_id,
        action="UNIT_OF_MEASURE_DEACTIVATED",
        entity_type="unit_of_measure",
        entity_id=item.id,
    )
    await session.commit()
