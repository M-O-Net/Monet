"""add operator_displays and cascade gui tables

Revision ID: 156de82f400d
Revises: 88932076788a
Create Date: 2026-08-20 05:19:50.784383

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '156de82f400d'
down_revision: str | None = '88932076788a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TOP_LEVEL_FK = 'top_level_objects_object_id_fkey'


def upgrade() -> None:
    op.create_table(
        'operator_displays',
        sa.Column('operator_id', sa.Uuid(), nullable=False),
        sa.Column('template', sa.String(), nullable=True),
        sa.Column('hidden_by_default', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_membership', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(['operator_id'], ['objects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('operator_id'),
    )
    op.drop_constraint(TOP_LEVEL_FK, 'top_level_objects', type_='foreignkey')
    op.create_foreign_key(
        TOP_LEVEL_FK, 'top_level_objects', 'objects', ['object_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint(TOP_LEVEL_FK, 'top_level_objects', type_='foreignkey')
    op.create_foreign_key(TOP_LEVEL_FK, 'top_level_objects', 'objects', ['object_id'], ['id'])
    op.drop_table('operator_displays')
