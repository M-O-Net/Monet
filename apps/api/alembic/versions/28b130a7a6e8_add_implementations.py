"""add implementations

Revision ID: 28b130a7a6e8
Revises: 88932076788a
Create Date: 2026-08-20 00:58:45.979299

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "28b130a7a6e8"
down_revision: str | None = "88932076788a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "implementations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("operator_id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["operator_id"], ["objects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("implementations")
