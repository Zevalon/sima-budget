from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ApplicationSetting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "application_settings"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    application_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        server_default="SIMA",
    )
    application_short_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default="SIMA",
    )
    organization_display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    logo_file_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    favicon_file_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True))
    primary_color: Mapped[str | None] = mapped_column(String(20))
    secondary_color: Mapped[str | None] = mapped_column(String(20))
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default="IDR",
    )
    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        server_default="Asia/Jakarta",
    )
    date_format: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default="DD/MM/YYYY",
    )
    allow_annual_budget_revision: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    allow_budget_transfer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    allow_self_approval: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
