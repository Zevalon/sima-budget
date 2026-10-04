from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BudgetPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "budget_plans"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'CANCELLED')",
            name="ck_budget_plan_status",
        ),
        UniqueConstraint("organization_id", "plan_number", name="uq_budget_plan_org_number"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fiscal_year_id: Mapped[UUID] = mapped_column(
        ForeignKey("fiscal_years.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    unit_allocation_id: Mapped[UUID] = mapped_column(
        ForeignKey("unit_allocations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    organization_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    plan_number: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="DRAFT", index=True
    )
    current_version_no: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    submitted_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)


class BudgetPlanVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "budget_plan_versions"
    __table_args__ = (
        CheckConstraint("version_no >= 1", name="ck_budget_plan_version_no_positive"),
        CheckConstraint("total_amount > 0", name="ck_budget_plan_version_total_nonnegative"),
        UniqueConstraint("budget_plan_id", "version_no", name="uq_budget_plan_version_number"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    budget_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )


class BudgetPlanItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "budget_plan_items"
    __table_args__ = (
        CheckConstraint("line_no >= 1", name="ck_budget_plan_item_line_positive"),
        CheckConstraint("quantity > 0", name="ck_budget_plan_item_quantity_positive"),
        CheckConstraint("unit_price > 0", name="ck_budget_plan_item_unit_price_positive"),
        CheckConstraint("amount > 0", name="ck_budget_plan_item_amount_positive"),
        UniqueConstraint("plan_version_id", "line_no", name="uq_budget_plan_item_version_line"),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_plan_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_category_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    unit_of_measure_id: Mapped[UUID] = mapped_column(
        ForeignKey("units_of_measure.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class BudgetPlanApproval(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "budget_plan_approvals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_budget_plan_approval_status",
        ),
        CheckConstraint("submission_no >= 1", name="ck_budget_plan_approval_submission_positive"),
        UniqueConstraint(
            "budget_plan_id",
            "submission_no",
            name="uq_budget_plan_approval_submission",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    budget_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_plan_versions.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    submission_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="PENDING", index=True
    )
    requested_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_note: Mapped[str | None] = mapped_column(Text)
