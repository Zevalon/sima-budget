from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Realization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "realizations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'POSTED', 'REVERSED', 'CANCELLED')",
            name="ck_realization_status",
        ),
        CheckConstraint("amount > 0", name="ck_realization_amount_positive"),
        CheckConstraint("row_version >= 1", name="ck_realization_row_version_positive"),
        CheckConstraint(
            "correction_of_id IS NULL OR correction_of_id <> id",
            name="ck_realization_correction_not_self",
        ),
        CheckConstraint(
            "status <> 'CANCELLED' OR "
            "(cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL "
            "AND cancellation_reason IS NOT NULL)",
            name="ck_realization_cancel_metadata",
        ),
        CheckConstraint(
            "status <> 'REVERSED' OR "
            "(reversed_by IS NOT NULL AND reversed_at IS NOT NULL "
            "AND reversal_reason IS NOT NULL AND posted_at IS NOT NULL)",
            name="ck_realization_reverse_metadata",
        ),
        UniqueConstraint(
            "organization_id",
            "realization_number",
            name="uq_realization_org_number",
        ),
        UniqueConstraint("correction_of_id", name="uq_realization_correction_of"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fiscal_year_id: Mapped[UUID] = mapped_column(
        ForeignKey("fiscal_years.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    budget_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_plans.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    plan_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_plan_versions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    organization_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    realization_number: Mapped[str] = mapped_column(String(90), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="DRAFT", index=True
    )
    realization_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    reference_number: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(String(250))
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    posted_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    correction_of_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("realizations.id", ondelete="RESTRICT"), index=True
    )
    cancelled_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[str | None] = mapped_column(String(500))
    reversed_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reversal_reason: Mapped[str | None] = mapped_column(String(500))
