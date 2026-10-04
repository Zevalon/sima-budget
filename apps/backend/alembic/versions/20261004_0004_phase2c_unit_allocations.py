"""phase 2c unit allocation core

Revision ID: 20261004_0004
Revises: 20261004_0003
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0004"
down_revision: str | Sequence[str] | None = "20261004_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "unit_allocations",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("fiscal_year_id", sa.Uuid(), nullable=False),
        sa.Column("annual_budget_id", sa.Uuid(), nullable=False),
        sa.Column("organization_unit_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
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
        sa.CheckConstraint("amount > 0", name="ck_unit_allocation_amount_positive"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fiscal_year_id"], ["fiscal_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["annual_budget_id"], ["annual_budgets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["organization_unit_id"], ["organization_units.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "annual_budget_id",
            "organization_unit_id",
            name="uq_unit_allocation_budget_unit",
        ),
    )
    op.create_index(
        "ix_unit_allocations_organization_id",
        "unit_allocations",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_unit_allocations_fiscal_year_id",
        "unit_allocations",
        ["fiscal_year_id"],
        unique=False,
    )
    op.create_index(
        "ix_unit_allocations_annual_budget_id",
        "unit_allocations",
        ["annual_budget_id"],
        unique=False,
    )
    op.create_index(
        "ix_unit_allocations_organization_unit_id",
        "unit_allocations",
        ["organization_unit_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_unit_allocations_organization_unit_id",
        table_name="unit_allocations",
    )
    op.drop_index(
        "ix_unit_allocations_annual_budget_id",
        table_name="unit_allocations",
    )
    op.drop_index(
        "ix_unit_allocations_fiscal_year_id",
        table_name="unit_allocations",
    )
    op.drop_index(
        "ix_unit_allocations_organization_id",
        table_name="unit_allocations",
    )
    op.drop_table("unit_allocations")
