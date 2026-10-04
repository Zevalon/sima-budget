from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UnitAllocation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "unit_allocations"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_unit_allocation_amount_positive"),
        UniqueConstraint(
            "annual_budget_id",
            "organization_unit_id",
            name="uq_unit_allocation_budget_unit",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fiscal_year_id: Mapped[UUID] = mapped_column(
        ForeignKey("fiscal_years.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    annual_budget_id: Mapped[UUID] = mapped_column(
        ForeignKey("annual_budgets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    organization_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
