"""expand marine source and gap confidence fields

Revision ID: 20260405_0008
Revises: 20260405_0007
Create Date: 2026-04-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260405_0008"
down_revision = "20260405_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "marine_sources",
        sa.Column("provider_kind", sa.String(length=32), nullable=False, server_default="unknown"),
    )
    op.add_column(
        "marine_sources",
        sa.Column("coverage_scope", sa.String(length=64), nullable=False, server_default="unknown"),
    )
    op.add_column(
        "marine_sources",
        sa.Column("global_coverage_claimed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "marine_sources",
        sa.Column("assumptions_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "marine_sources",
        sa.Column("limitations_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.add_column("marine_sources", sa.Column("source_url", sa.Text()))

    op.add_column(
        "marine_gap_events",
        sa.Column(
            "normal_sparse_reporting_plausible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "marine_gap_events",
        sa.Column("confidence_breakdown_json", sa.Text(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("marine_gap_events", "confidence_breakdown_json")
    op.drop_column("marine_gap_events", "normal_sparse_reporting_plausible")

    op.drop_column("marine_sources", "source_url")
    op.drop_column("marine_sources", "limitations_json")
    op.drop_column("marine_sources", "assumptions_json")
    op.drop_column("marine_sources", "global_coverage_claimed")
    op.drop_column("marine_sources", "coverage_scope")
    op.drop_column("marine_sources", "provider_kind")
