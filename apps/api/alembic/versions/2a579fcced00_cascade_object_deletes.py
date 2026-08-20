"""cascade object deletes

Revision ID: 2a579fcced00
Revises: 28b130a7a6e8
Create Date: 2026-08-20 09:32:45.600307

"""
from collections.abc import Sequence

from alembic import op

revision: str = '2a579fcced00'
down_revision: str | None = '28b130a7a6e8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for table, column in (("relations", "operator_id"), ("top_level_objects", "object_id")):
        op.drop_constraint(f"{table}_{column}_fkey", table, type_="foreignkey")
        op.create_foreign_key(
            f"{table}_{column}_fkey", table, "objects", [column], ["id"], ondelete="CASCADE"
        )


def downgrade() -> None:
    for table, column in (("relations", "operator_id"), ("top_level_objects", "object_id")):
        op.drop_constraint(f"{table}_{column}_fkey", table, type_="foreignkey")
        op.create_foreign_key(f"{table}_{column}_fkey", table, "objects", [column], ["id"])
