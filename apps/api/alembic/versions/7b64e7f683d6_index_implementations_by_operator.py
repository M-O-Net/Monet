"""index implementations by operator

Revision ID: 7b64e7f683d6
Revises: 674d133f591b
Create Date: 2026-10-29 13:42:28.318229

"""

from collections.abc import Sequence

from alembic import op

revision: str = "7b64e7f683d6"
down_revision: str | None = "674d133f591b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_implementations_operator_id"), "implementations", ["operator_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_implementations_operator_id"), table_name="implementations")
