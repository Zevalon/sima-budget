"""phase 2b1 annual budget core and submission workflow

Revision ID: 20261004_0003
Revises: 20261004_0002
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0003"
down_revision: str | Sequence[str] | None = "20261004_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "annual_budgets",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("fiscal_year_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default="DRAFT",
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("submitted_by", sa.Uuid(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Uuid(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
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
        sa.CheckConstraint("amount > 0", name="ck_annual_budget_amount_positive"),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED')",
            name="ck_annual_budget_status",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fiscal_year_id"], ["fiscal_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "fiscal_year_id",
            name="uq_annual_budget_org_fiscal_year",
        ),
    )
    op.create_index(
        "ix_annual_budgets_organization_id",
        "annual_budgets",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        "ix_annual_budgets_fiscal_year_id",
        "annual_budgets",
        ["fiscal_year_id"],
        unique=False,
    )
    op.create_index("ix_annual_budgets_status", "annual_budgets", ["status"], unique=False)
    op.create_index(
        "ix_annual_budgets_submitted_by",
        "annual_budgets",
        ["submitted_by"],
        unique=False,
    )
    op.create_index(
        "ix_annual_budgets_approved_by",
        "annual_budgets",
        ["approved_by"],
        unique=False,
    )

    op.create_table(
        "annual_budget_approvals",
        sa.Column("annual_budget_id", sa.Uuid(), nullable=False),
        sa.Column("submission_no", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_by", sa.Uuid(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.Text(), nullable=True),
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
            "status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_annual_budget_approval_status",
        ),
        sa.ForeignKeyConstraint(["annual_budget_id"], ["annual_budgets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "annual_budget_id",
            "submission_no",
            name="uq_annual_budget_approval_submission",
        ),
    )
    op.create_index(
        "ix_annual_budget_approvals_annual_budget_id",
        "annual_budget_approvals",
        ["annual_budget_id"],
        unique=False,
    )
    op.create_index(
        "ix_annual_budget_approvals_status",
        "annual_budget_approvals",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_annual_budget_approvals_requested_by",
        "annual_budget_approvals",
        ["requested_by"],
        unique=False,
    )
    op.create_index(
        "ix_annual_budget_approvals_decided_by",
        "annual_budget_approvals",
        ["decided_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_annual_budget_approvals_decided_by",
        table_name="annual_budget_approvals",
    )
    op.drop_index(
        "ix_annual_budget_approvals_requested_by",
        table_name="annual_budget_approvals",
    )
    op.drop_index(
        "ix_annual_budget_approvals_status",
        table_name="annual_budget_approvals",
    )
    op.drop_index(
        "ix_annual_budget_approvals_annual_budget_id",
        table_name="annual_budget_approvals",
    )
    op.drop_table("annual_budget_approvals")

    op.drop_index("ix_annual_budgets_approved_by", table_name="annual_budgets")
    op.drop_index("ix_annual_budgets_submitted_by", table_name="annual_budgets")
    op.drop_index("ix_annual_budgets_status", table_name="annual_budgets")
    op.drop_index("ix_annual_budgets_fiscal_year_id", table_name="annual_budgets")
    op.drop_index("ix_annual_budgets_organization_id", table_name="annual_budgets")
    op.drop_table("annual_budgets")
