"""add relation references

Revision ID: 674d133f591b
Revises: 0307f3ff1223
Create Date: 2026-10-28 21:24:22.522762

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "674d133f591b"
down_revision: str | None = "0307f3ff1223"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "relation_references",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("relation_id", sa.Uuid(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["relation_id"], ["relations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("relation_id", "url"),
    )


def downgrade() -> None:
    op.drop_table("relation_references")
