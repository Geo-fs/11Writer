"""merge webcam inventory and marine schema heads

Revision ID: 20260405_0009
Revises: 20260404_0007, 20260405_0008
Create Date: 2026-04-05 00:09:00.000000
"""

from __future__ import annotations

from alembic import op

revision = "20260405_0009"
down_revision = ("20260404_0007", "20260405_0008")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
