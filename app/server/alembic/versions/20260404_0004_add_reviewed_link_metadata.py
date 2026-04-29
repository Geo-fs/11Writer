"""add reviewed link metadata

Revision ID: 20260404_0004
Revises: 20260404_0003
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0004"
down_revision = "20260404_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reference_links", sa.Column("review_status", sa.String(length=32), nullable=False, server_default="approved"))
    op.add_column("reference_links", sa.Column("reviewed_by", sa.String(length=255)))
    op.add_column("reference_links", sa.Column("reviewed_at", sa.String(length=64)))
    op.add_column("reference_links", sa.Column("review_source", sa.String(length=128)))
    op.add_column("reference_links", sa.Column("candidate_method", sa.String(length=128)))
    op.add_column("reference_links", sa.Column("candidate_score", sa.Float()))
    op.add_column("reference_links", sa.Column("created_at", sa.String(length=64)))
    op.add_column("reference_links", sa.Column("updated_at", sa.String(length=64)))

    op.create_index("ix_reference_links_review_status", "reference_links", ["review_status"])
    op.create_index("ix_reference_links_reviewed_by", "reference_links", ["reviewed_by"])
    op.create_index("ix_reference_links_reviewed_at", "reference_links", ["reviewed_at"])
    op.create_index("ix_reference_links_created_at", "reference_links", ["created_at"])
    op.create_index("ix_reference_links_updated_at", "reference_links", ["updated_at"])


def downgrade() -> None:
    op.drop_index("ix_reference_links_updated_at", table_name="reference_links")
    op.drop_index("ix_reference_links_created_at", table_name="reference_links")
    op.drop_index("ix_reference_links_reviewed_at", table_name="reference_links")
    op.drop_index("ix_reference_links_reviewed_by", table_name="reference_links")
    op.drop_index("ix_reference_links_review_status", table_name="reference_links")

    op.drop_column("reference_links", "updated_at")
    op.drop_column("reference_links", "created_at")
    op.drop_column("reference_links", "candidate_score")
    op.drop_column("reference_links", "candidate_method")
    op.drop_column("reference_links", "review_source")
    op.drop_column("reference_links", "reviewed_at")
    op.drop_column("reference_links", "reviewed_by")
    op.drop_column("reference_links", "review_status")
