"""add endpoint verification fields to camera source inventory

Revision ID: 20260429_0011
Revises: 20260428_0010
Create Date: 2026-04-29
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260429_0011"
down_revision = "20260428_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("camera_source_inventory", sa.Column("endpoint_verification_status", sa.String(length=32), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("candidate_endpoint_url", sa.Text(), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("machine_readable_endpoint_url", sa.Text(), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("last_endpoint_check_at", sa.String(length=64), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("last_endpoint_http_status", sa.Integer(), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("last_endpoint_content_type", sa.String(length=255), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("last_endpoint_result", sa.Text(), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("last_endpoint_notes_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("camera_source_inventory", sa.Column("verification_caveat", sa.Text(), nullable=True))
    op.create_index(
        op.f("ix_camera_source_inventory_endpoint_verification_status"),
        "camera_source_inventory",
        ["endpoint_verification_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_camera_source_inventory_last_endpoint_check_at"),
        "camera_source_inventory",
        ["last_endpoint_check_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_camera_source_inventory_last_endpoint_check_at"), table_name="camera_source_inventory")
    op.drop_index(op.f("ix_camera_source_inventory_endpoint_verification_status"), table_name="camera_source_inventory")
    op.drop_column("camera_source_inventory", "verification_caveat")
    op.drop_column("camera_source_inventory", "last_endpoint_notes_json")
    op.drop_column("camera_source_inventory", "last_endpoint_result")
    op.drop_column("camera_source_inventory", "last_endpoint_content_type")
    op.drop_column("camera_source_inventory", "last_endpoint_http_status")
    op.drop_column("camera_source_inventory", "last_endpoint_check_at")
    op.drop_column("camera_source_inventory", "machine_readable_endpoint_url")
    op.drop_column("camera_source_inventory", "candidate_endpoint_url")
    op.drop_column("camera_source_inventory", "endpoint_verification_status")
