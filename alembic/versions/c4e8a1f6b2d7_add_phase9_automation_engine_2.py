"""add_phase9_automation_engine_2

Adds the Automation Engine 2.0 schema on top of the original Phase 1
``automations`` table, plus the idempotency key on ``automation_runs``.
Purely additive — existing automation rows and execution history are kept.

Revision ID: c4e8a1f6b2d7
Revises: b7f3c1d92a45
Create Date: 2026-10-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4e8a1f6b2d7'
down_revision: Union[str, Sequence[str], None] = 'b7f3c1d92a45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _inspector():
    return sa.inspect(op.get_bind())


def _existing_columns(table_name: str) -> set:
    inspector = _inspector()
    if table_name not in inspector.get_table_names():
        return set()
    return {c["name"] for c in inspector.get_columns(table_name)}


def _existing_indexes(table_name: str) -> set:
    inspector = _inspector()
    if table_name not in inspector.get_table_names():
        return set()
    return {i["name"] for i in inspector.get_indexes(table_name)}


def upgrade() -> None:
    """Upgrade schema (idempotent: skips anything that already exists)."""
    existing = _existing_columns("automations")
    if existing:
        wanted = {
            "description": sa.Column("description", sa.String(), nullable=True),
            "trigger_type": sa.Column(
                "trigger_type", sa.String(), nullable=False, server_default="schedule"
            ),
            "trigger_config": sa.Column("trigger_config", sa.JSON(), nullable=True),
            "conditions": sa.Column("conditions", sa.JSON(), nullable=True),
            "actions": sa.Column("actions", sa.JSON(), nullable=True),
            "timezone": sa.Column(
                "timezone", sa.String(), nullable=False, server_default="Asia/Kolkata"
            ),
            "next_run_at": sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
            "last_run_at": sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
            "failure_policy": sa.Column(
                "failure_policy", sa.String(), nullable=False, server_default="stop"
            ),
            "max_retries": sa.Column(
                "max_retries", sa.Integer(), nullable=False, server_default="1"
            ),
            "retry_delay_seconds": sa.Column(
                "retry_delay_seconds", sa.Float(), nullable=False, server_default="2.0"
            ),
            "archived_at": sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
            "updated_at": sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        }
        to_add = [col for name, col in wanted.items() if name not in existing]
        if to_add:
            with op.batch_alter_table("automations", schema=None) as batch_op:
                for column in to_add:
                    batch_op.add_column(column)

    # Idempotency key on execution history
    run_columns = _existing_columns("automation_runs")
    if run_columns and "execution_key" not in run_columns:
        with op.batch_alter_table("automation_runs", schema=None) as batch_op:
            batch_op.add_column(sa.Column("execution_key", sa.String(), nullable=True))

    run_indexes = _existing_indexes("automation_runs")
    if "uq_automation_runs_automation_execution_key" not in run_indexes:
        op.create_index(
            "uq_automation_runs_automation_execution_key",
            "automation_runs",
            ["automation_id", "execution_key"],
            unique=True,
        )

    automations_indexes = _existing_indexes("automations")
    if "ix_automations_user_id" not in automations_indexes:
        op.create_index("ix_automations_user_id", "automations", ["user_id"], unique=False)
    if "ix_automations_archived_at" not in automations_indexes:
        op.create_index("ix_automations_archived_at", "automations", ["archived_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema (drops the additive Automation Engine 2.0 columns)."""
    automations_indexes = _existing_indexes("automations")
    for name in ("ix_automations_archived_at", "ix_automations_user_id"):
        if name in automations_indexes:
            op.drop_index(name, table_name="automations")

    run_indexes = _existing_indexes("automation_runs")
    if "uq_automation_runs_automation_execution_key" in run_indexes:
        op.drop_index(
            "uq_automation_runs_automation_execution_key", table_name="automation_runs"
        )

    existing = _existing_columns("automations")
    if existing:
        with op.batch_alter_table("automations", schema=None) as batch_op:
            for name in ("updated_at", "archived_at", "retry_delay_seconds", "max_retries",
                         "failure_policy", "last_run_at", "next_run_at", "timezone",
                         "actions", "conditions", "trigger_config", "trigger_type",
                         "description"):
                if name in existing:
                    batch_op.drop_column(name)

    run_columns = _existing_columns("automation_runs")
    if run_columns and "execution_key" in run_columns:
        with op.batch_alter_table("automation_runs", schema=None) as batch_op:
            batch_op.drop_column("execution_key")
