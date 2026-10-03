from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(250))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )


class OrganizationUnitType(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organization_unit_types"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_unit_type_org_code"),)

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )


class OrganizationUnit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organization_units"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_org_unit_org_code"),)

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unit_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_unit_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    can_receive_budget: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    can_create_budget_plan: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )


class UserUnitMembership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_unit_memberships"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_unit_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_title: Mapped[str | None] = mapped_column(String(150))
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    start_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
    )
    end_at: Mapped[date | None] = mapped_column(Date)
