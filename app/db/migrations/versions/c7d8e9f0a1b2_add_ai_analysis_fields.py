"""add AI analysis fields

Revision ID: c7d8e9f0a1b2
Revises: a5f224a59fe1
Create Date: 2026-09-30 22:50:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, Sequence[str], None] = "a5f224a59fe1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "incidents",
        sa.Column("reasoning", sa.Text(), nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("supporting_evidence", sa.Text(), nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("expected_impact", sa.Text(), nullable=True),
    )
    op.add_column(
        "incidents",
        sa.Column("risks", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("incidents", "risks")
    op.drop_column("incidents", "expected_impact")
    op.drop_column("incidents", "supporting_evidence")
    op.drop_column("incidents", "reasoning")
