"""phase 3b budget plan submission and approval

Revision ID: 20261004_0006
Revises: 20261004_0005
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0006"
down_revision: str | Sequence[str] | None = "20261004_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("budget_plans", sa.Column("submitted_by", sa.Uuid(), nullable=True))
    op.add_column(
        "budget_plans",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("budget_plans", sa.Column("approved_by", sa.Uuid(), nullable=True))
    op.add_column(
        "budget_plans",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("budget_plans", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_budget_plans_submitted_by_users",
        "budget_plans",
        "users",
        ["submitted_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_budget_plans_approved_by_users",
        "budget_plans",
        "users",
        ["approved_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_budget_plans_submitted_by", "budget_plans", ["submitted_by"])
    op.create_index("ix_budget_plans_approved_by", "budget_plans", ["approved_by"])

    op.create_table(
        "budget_plan_approvals",
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("budget_plan_id", sa.Uuid(), nullable=False),
        sa.Column("plan_version_id", sa.Uuid(), nullable=False),
        sa.Column("submission_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False),
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
            name="ck_budget_plan_approval_status",
        ),
        sa.CheckConstraint(
            "submission_no >= 1",
            name="ck_budget_plan_approval_submission_positive",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["budget_plan_id"], ["budget_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["plan_version_id"], ["budget_plan_versions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "budget_plan_id",
            "submission_no",
            name="uq_budget_plan_approval_submission",
        ),
    )
    for column in (
        "organization_id",
        "budget_plan_id",
        "plan_version_id",
        "status",
        "requested_by",
        "decided_by",
    ):
        op.create_index(
            f"ix_budget_plan_approvals_{column}",
            "budget_plan_approvals",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in (
        "decided_by",
        "requested_by",
        "status",
        "plan_version_id",
        "budget_plan_id",
        "organization_id",
    ):
        op.drop_index(f"ix_budget_plan_approvals_{column}", table_name="budget_plan_approvals")
    op.drop_table("budget_plan_approvals")

    op.drop_index("ix_budget_plans_approved_by", table_name="budget_plans")
    op.drop_index("ix_budget_plans_submitted_by", table_name="budget_plans")
    op.drop_constraint("fk_budget_plans_approved_by_users", "budget_plans", type_="foreignkey")
    op.drop_constraint("fk_budget_plans_submitted_by_users", "budget_plans", type_="foreignkey")
    op.drop_column("budget_plans", "rejection_reason")
    op.drop_column("budget_plans", "approved_at")
    op.drop_column("budget_plans", "approved_by")
    op.drop_column("budget_plans", "submitted_at")
    op.drop_column("budget_plans", "submitted_by")
