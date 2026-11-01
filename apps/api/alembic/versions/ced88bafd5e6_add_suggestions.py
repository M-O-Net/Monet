"""add suggestions

Revision ID: ced88bafd5e6
Revises: 7b64e7f683d6
Create Date: 2026-11-01 13:43:37.144415

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "ced88bafd5e6"
down_revision: str | None = "7b64e7f683d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "suggestions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.String(), nullable=False),
        sa.Column("page_path", sa.String(), nullable=False),
        sa.Column("contributor", sa.String(), nullable=True),
        sa.Column(
            "at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_suggestions_at"), "suggestions", ["at"], unique=False)
    op.create_table(
        "suggestion_screenshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("suggestion_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("media_type", sa.String(), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.ForeignKeyConstraint(["suggestion_id"], ["suggestions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_suggestion_screenshots_suggestion_id"),
        "suggestion_screenshots",
        ["suggestion_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_suggestion_screenshots_suggestion_id"), table_name="suggestion_screenshots"
    )
    op.drop_table("suggestion_screenshots")
    op.drop_index(op.f("ix_suggestions_at"), table_name="suggestions")
    op.drop_table("suggestions")
