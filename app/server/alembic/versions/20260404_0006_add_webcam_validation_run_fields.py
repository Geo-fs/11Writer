"""add webcam validation run fields

Revision ID: 20260404_0006
Revises: 20260404_0005
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0006"
down_revision = "20260404_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "camera_source_runs",
        sa.Column("run_mode", sa.String(length=32), nullable=False, server_default="scheduled"),
    )
    op.add_column(
        "camera_source_runs",
        sa.Column("frame_probe_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "camera_source_runs",
        sa.Column("frame_status_counts_json", sa.Text(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "camera_source_runs",
        sa.Column("metadata_uncertainty_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("camera_source_runs", sa.Column("cadence_observation", sa.Text()))
    op.create_index("ix_camera_source_runs_run_mode", "camera_source_runs", ["run_mode"])


def downgrade() -> None:
    op.drop_index("ix_camera_source_runs_run_mode", table_name="camera_source_runs")
    op.drop_column("camera_source_runs", "cadence_observation")
    op.drop_column("camera_source_runs", "metadata_uncertainty_count")
    op.drop_column("camera_source_runs", "frame_status_counts_json")
    op.drop_column("camera_source_runs", "frame_probe_count")
    op.drop_column("camera_source_runs", "run_mode")
