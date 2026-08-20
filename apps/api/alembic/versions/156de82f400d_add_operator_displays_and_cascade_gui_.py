"""add operator_displays and cascade gui tables

Revision ID: 156de82f400d
Revises: 88932076788a
Create Date: 2026-08-20 05:19:50.784383

Hand-adjusted from autogenerate, in three places:

- `sqlmodel.sql.sqltypes.AutoString()` -> `sa.String()`. Autogenerate emits AutoString without
  importing sqlmodel, so the file does not even import; AutoString renders as VARCHAR anyway.
  Both earlier revisions carry the same fix.
- Named the top_level_objects foreign key explicitly. Autogenerate passed None for the new
  constraint's name and for the drop in downgrade(), which cannot resolve to anything.
- Added server_default to the booleans so a plain SQL insert doesn't have to name them.
  Alembic's compare_server_default is off, so this introduces no drift against the model.

No data migration flags the existing Element Of object as the membership operator: `just seed`
is the documented hard reset for v0, and matching on an object's latex would be exactly the
kind of name-coupling that OperatorDisplay.is_membership exists to avoid.
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
    # RESTRICT (the default) meant a curation row blocked deleting its own object, and
    # delete_object translated that into "still used as an operator or as a relation's
    # input/output" — which was simply untrue for an object that had no relations at all.
    op.drop_constraint(TOP_LEVEL_FK, 'top_level_objects', type_='foreignkey')
    op.create_foreign_key(
        TOP_LEVEL_FK, 'top_level_objects', 'objects', ['object_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint(TOP_LEVEL_FK, 'top_level_objects', type_='foreignkey')
    op.create_foreign_key(TOP_LEVEL_FK, 'top_level_objects', 'objects', ['object_id'], ['id'])
    op.drop_table('operator_displays')
