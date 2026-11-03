"""store object search keys

Revision ID: 4c1d2e9f7a30
Revises: ced88bafd5e6
Create Date: 2026-11-03 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4c1d2e9f7a30"
down_revision: str | None = "ced88bafd5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


LATEX_KEY = (
    "lower(btrim(regexp_replace(regexp_replace(regexp_replace(latex, '\\\\[a-zA-Z]+', ' ', 'g'), "
    "'[{}$]', '', 'g'), '[\\s,&\\\\]+', ' ', 'g')))"
)
DESCRIPTION_KEY = LATEX_KEY.replace("(latex,", "(coalesce(description, ''),")


def upgrade() -> None:
    op.add_column("objects", sa.Column("latex_key", sa.Text(), sa.Computed(LATEX_KEY)))
    op.add_column(
        "objects",
        sa.Column("description_key", sa.Text(), sa.Computed(DESCRIPTION_KEY)),
    )


def downgrade() -> None:
    op.drop_column("objects", "description_key")
    op.drop_column("objects", "latex_key")
