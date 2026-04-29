"""add candidate inventory assessment fields

Revision ID: 20260428_0010
Revises: 20260405_0009
Create Date: 2026-04-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260428_0010"
down_revision = "20260405_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("camera_source_inventory", sa.Column("page_structure", sa.String(length=64), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("likely_camera_count", sa.Integer(), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("compliance_risk", sa.String(length=16), nullable=True))
    op.add_column("camera_source_inventory", sa.Column("extraction_feasibility", sa.String(length=16), nullable=True))
    op.create_index(op.f("ix_camera_source_inventory_page_structure"), "camera_source_inventory", ["page_structure"], unique=False)
    op.create_index(op.f("ix_camera_source_inventory_compliance_risk"), "camera_source_inventory", ["compliance_risk"], unique=False)
    op.create_index(op.f("ix_camera_source_inventory_extraction_feasibility"), "camera_source_inventory", ["extraction_feasibility"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_camera_source_inventory_extraction_feasibility"), table_name="camera_source_inventory")
    op.drop_index(op.f("ix_camera_source_inventory_compliance_risk"), table_name="camera_source_inventory")
    op.drop_index(op.f("ix_camera_source_inventory_page_structure"), table_name="camera_source_inventory")
    op.drop_column("camera_source_inventory", "extraction_feasibility")
    op.drop_column("camera_source_inventory", "compliance_risk")
    op.drop_column("camera_source_inventory", "likely_camera_count")
    op.drop_column("camera_source_inventory", "page_structure")
