"""phase 3a budget plan core and versioned items

Revision ID: 20261004_0005
Revises: 20261004_0004
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0005"
down_revision: str | Sequence[str] | None = "20261004_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "budget_plans",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("fiscal_year_id", sa.Uuid(), nullable=False),
        sa.Column("unit_allocation_id", sa.Uuid(), nullable=False),
        sa.Column("organization_unit_id", sa.Uuid(), nullable=False),
        sa.Column("plan_number", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="DRAFT", nullable=False),
        sa.Column("current_version_no", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("row_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
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
            "status IN ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'CANCELLED')",
            name="ck_budget_plan_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fiscal_year_id"], ["fiscal_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["unit_allocation_id"], ["unit_allocations.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["organization_unit_id"], ["organization_units.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "plan_number", name="uq_budget_plan_org_number"),
    )
    for column in (
        "organization_id",
        "fiscal_year_id",
        "unit_allocation_id",
        "organization_unit_id",
        "status",
        "created_by",
    ):
        op.create_index(f"ix_budget_plans_{column}", "budget_plans", [column], unique=False)

    op.create_table(
        "budget_plan_versions",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("budget_plan_id", sa.Uuid(), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
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
        sa.CheckConstraint("version_no >= 1", name="ck_budget_plan_version_no_positive"),
        sa.CheckConstraint("total_amount > 0", name="ck_budget_plan_version_total_nonnegative"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["budget_plan_id"], ["budget_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("budget_plan_id", "version_no", name="uq_budget_plan_version_number"),
    )
    for column in ("organization_id", "budget_plan_id", "created_by"):
        op.create_index(
            f"ix_budget_plan_versions_{column}",
            "budget_plan_versions",
            [column],
            unique=False,
        )

    op.create_table(
        "budget_plan_items",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("plan_version_id", sa.Uuid(), nullable=False),
        sa.Column("line_no", sa.Integer(), nullable=False),
        sa.Column("budget_category_id", sa.Uuid(), nullable=False),
        sa.Column("unit_of_measure_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.CheckConstraint("line_no >= 1", name="ck_budget_plan_item_line_positive"),
        sa.CheckConstraint("quantity > 0", name="ck_budget_plan_item_quantity_positive"),
        sa.CheckConstraint("unit_price > 0", name="ck_budget_plan_item_unit_price_positive"),
        sa.CheckConstraint("amount > 0", name="ck_budget_plan_item_amount_positive"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["budget_plan_versions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["budget_category_id"], ["budget_categories.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["unit_of_measure_id"], ["units_of_measure.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_version_id", "line_no", name="uq_budget_plan_item_version_line"),
    )
    for column in (
        "organization_id",
        "plan_version_id",
        "budget_category_id",
        "unit_of_measure_id",
    ):
        op.create_index(
            f"ix_budget_plan_items_{column}",
            "budget_plan_items",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in (
        "unit_of_measure_id",
        "budget_category_id",
        "plan_version_id",
        "organization_id",
    ):
        op.drop_index(f"ix_budget_plan_items_{column}", table_name="budget_plan_items")
    op.drop_table("budget_plan_items")

    for column in ("created_by", "budget_plan_id", "organization_id"):
        op.drop_index(f"ix_budget_plan_versions_{column}", table_name="budget_plan_versions")
    op.drop_table("budget_plan_versions")

    for column in (
        "created_by",
        "status",
        "organization_unit_id",
        "unit_allocation_id",
        "fiscal_year_id",
        "organization_id",
    ):
        op.drop_index(f"ix_budget_plans_{column}", table_name="budget_plans")
    op.drop_table("budget_plans")
