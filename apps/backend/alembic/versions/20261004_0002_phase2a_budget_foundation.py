"""phase 2a fiscal year and budget master foundation

Revision ID: 20261004_0002
Revises: 20261003_0001
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0002"
down_revision: str | Sequence[str] | None = "20261003_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fiscal_years",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="DRAFT", nullable=False),
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopened_by", sa.Uuid(), nullable=True),
        sa.Column("reopen_reason", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("start_date < end_date", name="ck_fiscal_year_dates"),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PLANNING', 'ACTIVE', 'CLOSED', 'ARCHIVED')",
            name="ck_fiscal_year_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reopened_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_fiscal_year_org_code"),
    )
    op.create_index(
        "ix_fiscal_years_organization_id",
        "fiscal_years",
        ["organization_id"],
        unique=False,
    )
    op.create_index("ix_fiscal_years_status", "fiscal_years", ["status"], unique=False)
    op.create_index("ix_fiscal_years_reopened_by", "fiscal_years", ["reopened_by"], unique=False)
    op.create_index(
        "uq_fiscal_year_one_active_per_org",
        "fiscal_years",
        ["organization_id"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )

    op.create_table(
        "budget_categories",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_budget_category_org_code"),
    )
    op.create_index(
        "ix_budget_categories_organization_id",
        "budget_categories",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "units_of_measure",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_uom_org_code"),
    )
    op.create_index(
        "ix_units_of_measure_organization_id",
        "units_of_measure",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_units_of_measure_organization_id", table_name="units_of_measure")
    op.drop_table("units_of_measure")

    op.drop_index("ix_budget_categories_organization_id", table_name="budget_categories")
    op.drop_table("budget_categories")

    op.drop_index("uq_fiscal_year_one_active_per_org", table_name="fiscal_years")
    op.drop_index("ix_fiscal_years_reopened_by", table_name="fiscal_years")
    op.drop_index("ix_fiscal_years_status", table_name="fiscal_years")
    op.drop_index("ix_fiscal_years_organization_id", table_name="fiscal_years")
    op.drop_table("fiscal_years")
