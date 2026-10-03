"""add workflow approval fields

Revision ID: d8e9f0a1b2c3
Revises: c7d8e9f0a1b2
Create Date: 2026-09-30 23:45:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d8e9f0a1b2c3"
down_revision: Union[str, Sequence[str], None] = "c7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "incidents",
        sa.Column("thread_id", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("approval_status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("approval_reason", sa.Text(), nullable=True),
    )
    op.create_index(
        op.f("ix_incidents_thread_id"),
        "incidents",
        ["thread_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_incidents_thread_id"),
        table_name="incidents",
    )
    op.drop_column("incidents", "approval_reason")
    op.drop_column("incidents", "approval_status")
    op.drop_column("incidents", "thread_id")
