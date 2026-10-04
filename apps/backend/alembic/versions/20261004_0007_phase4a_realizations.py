"""phase 4a realization core

Revision ID: 20261004_0007
Revises: 20261004_0006
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0007"
down_revision: str | Sequence[str] | None = "20261004_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "realizations",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("fiscal_year_id", sa.Uuid(), nullable=False),
        sa.Column("budget_plan_id", sa.Uuid(), nullable=False),
        sa.Column("plan_version_id", sa.Uuid(), nullable=False),
        sa.Column("organization_unit_id", sa.Uuid(), nullable=False),
        sa.Column("realization_number", sa.String(length=90), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="DRAFT", nullable=False),
        sa.Column("realization_date", sa.Date(), nullable=False),
        sa.Column("reference_number", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("vendor_name", sa.String(length=250), nullable=True),
        sa.Column("amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("row_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("posted_by", sa.Uuid(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(
            "status IN ('DRAFT', 'POSTED', 'REVERSED', 'CANCELLED')",
            name="ck_realization_status",
        ),
        sa.CheckConstraint("amount > 0", name="ck_realization_amount_positive"),
        sa.CheckConstraint(
            "row_version >= 1",
            name="ck_realization_row_version_positive",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fiscal_year_id"], ["fiscal_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["budget_plan_id"], ["budget_plans.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["budget_plan_versions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["organization_unit_id"], ["organization_units.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "realization_number",
            name="uq_realization_org_number",
        ),
    )
    for column in (
        "organization_id",
        "fiscal_year_id",
        "budget_plan_id",
        "plan_version_id",
        "organization_unit_id",
        "status",
        "realization_date",
        "created_by",
        "posted_by",
    ):
        op.create_index(
            f"ix_realizations_{column}",
            "realizations",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in reversed(
        (
            "organization_id",
            "fiscal_year_id",
            "budget_plan_id",
            "plan_version_id",
            "organization_unit_id",
            "status",
            "realization_date",
            "created_by",
            "posted_by",
        )
    ):
        op.drop_index(f"ix_realizations_{column}", table_name="realizations")
    op.drop_table("realizations")
