from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class FiscalYear(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "fiscal_years"
    __table_args__ = (
        CheckConstraint("start_date < end_date", name="ck_fiscal_year_dates"),
        CheckConstraint(
            "status IN ('DRAFT', 'PLANNING', 'ACTIVE', 'CLOSED', 'ARCHIVED')",
            name="ck_fiscal_year_status",
        ),
        UniqueConstraint("organization_id", "code", name="uq_fiscal_year_org_code"),
        Index(
            "uq_fiscal_year_one_active_per_org",
            "organization_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="DRAFT",
        index=True,
    )
    reopened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reopened_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    reopen_reason: Mapped[str | None] = mapped_column(Text)


class BudgetCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "budget_categories"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_budget_category_org_code"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )


class UnitOfMeasure(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "units_of_measure"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_uom_org_code"),)

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
