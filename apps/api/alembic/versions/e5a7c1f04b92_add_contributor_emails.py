"""add contributor emails

Revision ID: e5a7c1f04b92
Revises: bd41ec2e5ccb
Create Date: 2026-11-03 17:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e5a7c1f04b92"
down_revision: str | None = "bd41ec2e5ccb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = ("editors", "events", "comments", "suggestions")


def upgrade() -> None:
    for table in TABLES:
        op.add_column(table, sa.Column("email", sa.String(), nullable=True))


def downgrade() -> None:
    for table in TABLES:
        op.drop_column(table, "email")
