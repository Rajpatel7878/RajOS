"""add_phase8_task_productivity_fields

Adds the Phase 8 (Productivity Intelligence) columns to the existing ``tasks``
table.  Purely additive — no data is modified or dropped.

Revision ID: b7f3c1d92a45
Revises: 2a1a5f704789
Create Date: 2026-10-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f3c1d92a45'
down_revision: Union[str, Sequence[str], None] = '2a1a5f704789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_columns(table_name: str) -> set:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {c["name"] for c in inspector.get_columns(table_name)}


def upgrade() -> None:
    """Upgrade schema (idempotent: skips columns that already exist)."""
    existing = _existing_columns("tasks")
    if not existing:
        return

    columns_to_add = []
    if "category" not in existing:
        columns_to_add.append(sa.Column("category", sa.String(), nullable=True))
    if "tags" not in existing:
        columns_to_add.append(sa.Column("tags", sa.String(), nullable=True))
    if "estimated_duration" not in existing:
        columns_to_add.append(sa.Column("estimated_duration", sa.Integer(), nullable=True))
    if "actual_duration" not in existing:
        columns_to_add.append(sa.Column("actual_duration", sa.Integer(), nullable=True))
    if "parent_task_id" not in existing:
        columns_to_add.append(sa.Column("parent_task_id", sa.Integer(), nullable=True))
    if "metadata_json" not in existing:
        columns_to_add.append(sa.Column("metadata_json", sa.JSON(), nullable=True))

    if not columns_to_add:
        return

    with op.batch_alter_table("tasks", schema=None) as batch_op:
        for column in columns_to_add:
            batch_op.add_column(column)


def downgrade() -> None:
    """Downgrade schema (drops the additive Phase 8 columns)."""
    existing = _existing_columns("tasks")
    if not existing:
        return

    with op.batch_alter_table("tasks", schema=None) as batch_op:
        for name in ("metadata_json", "parent_task_id", "actual_duration",
                     "estimated_duration", "tags", "category"):
            if name in existing:
                batch_op.drop_column(name)
