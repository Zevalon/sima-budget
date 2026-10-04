"""phase 4b realization cancellation reversal and correction

Revision ID: 20261004_0008
Revises: 20261004_0007
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261004_0008"
down_revision: str | Sequence[str] | None = "20261004_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("realizations", sa.Column("correction_of_id", sa.Uuid(), nullable=True))
    op.add_column("realizations", sa.Column("cancelled_by", sa.Uuid(), nullable=True))
    op.add_column(
        "realizations", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "realizations", sa.Column("cancellation_reason", sa.String(length=500), nullable=True)
    )
    op.add_column("realizations", sa.Column("reversed_by", sa.Uuid(), nullable=True))
    op.add_column(
        "realizations", sa.Column("reversed_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "realizations", sa.Column("reversal_reason", sa.String(length=500), nullable=True)
    )

    op.create_foreign_key(
        "fk_realizations_correction_of_id_realizations",
        "realizations",
        "realizations",
        ["correction_of_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_realizations_cancelled_by_users",
        "realizations",
        "users",
        ["cancelled_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_realizations_reversed_by_users",
        "realizations",
        "users",
        ["reversed_by"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_realization_correction_of", "realizations", ["correction_of_id"]
    )
    op.create_check_constraint(
        "ck_realization_correction_not_self",
        "realizations",
        "correction_of_id IS NULL OR correction_of_id <> id",
    )
    op.create_check_constraint(
        "ck_realization_cancel_metadata",
        "realizations",
        "status <> 'CANCELLED' OR "
        "(cancelled_by IS NOT NULL AND cancelled_at IS NOT NULL "
        "AND cancellation_reason IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_realization_reverse_metadata",
        "realizations",
        "status <> 'REVERSED' OR "
        "(reversed_by IS NOT NULL AND reversed_at IS NOT NULL "
        "AND reversal_reason IS NOT NULL AND posted_at IS NOT NULL)",
    )

    for column in ("correction_of_id", "cancelled_by", "reversed_by"):
        op.create_index(f"ix_realizations_{column}", "realizations", [column], unique=False)


def downgrade() -> None:
    for column in reversed(("correction_of_id", "cancelled_by", "reversed_by")):
        op.drop_index(f"ix_realizations_{column}", table_name="realizations")

    op.drop_constraint("ck_realization_reverse_metadata", "realizations", type_="check")
    op.drop_constraint("ck_realization_cancel_metadata", "realizations", type_="check")
    op.drop_constraint("ck_realization_correction_not_self", "realizations", type_="check")
    op.drop_constraint("uq_realization_correction_of", "realizations", type_="unique")
    op.drop_constraint("fk_realizations_reversed_by_users", "realizations", type_="foreignkey")
    op.drop_constraint("fk_realizations_cancelled_by_users", "realizations", type_="foreignkey")
    op.drop_constraint(
        "fk_realizations_correction_of_id_realizations",
        "realizations",
        type_="foreignkey",
    )

    for column in (
        "reversal_reason",
        "reversed_at",
        "reversed_by",
        "cancellation_reason",
        "cancelled_at",
        "cancelled_by",
        "correction_of_id",
    ):
        op.drop_column("realizations", column)
