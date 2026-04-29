"""add webcam worker state

Revision ID: 20260404_0005
Revises: 20260404_0004
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0005"
down_revision = "20260404_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("camera_sources", sa.Column("last_started_at", sa.String(length=64)))
    op.add_column("camera_sources", sa.Column("last_completed_at", sa.String(length=64)))
    op.add_column("camera_sources", sa.Column("next_refresh_at", sa.String(length=64)))
    op.add_column("camera_sources", sa.Column("backoff_until", sa.String(length=64)))
    op.add_column("camera_sources", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("camera_sources", sa.Column("last_http_status", sa.Integer()))
    op.add_column("camera_sources", sa.Column("cadence_seconds", sa.Integer()))
    op.add_column("camera_sources", sa.Column("cadence_reason", sa.Text()))
    op.create_index("ix_camera_sources_next_refresh_at", "camera_sources", ["next_refresh_at"])
    op.create_index("ix_camera_sources_backoff_until", "camera_sources", ["backoff_until"])

    op.add_column("camera_health", sa.Column("last_metadata_refresh_at", sa.String(length=64)))
    op.add_column("camera_health", sa.Column("next_frame_refresh_at", sa.String(length=64)))
    op.add_column("camera_health", sa.Column("backoff_until", sa.String(length=64)))
    op.add_column("camera_health", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.create_index("ix_camera_health_last_metadata_refresh_at", "camera_health", ["last_metadata_refresh_at"])
    op.create_index("ix_camera_health_next_frame_refresh_at", "camera_health", ["next_frame_refresh_at"])
    op.create_index("ix_camera_health_backoff_until", "camera_health", ["backoff_until"])

    op.create_table(
        "camera_source_runs",
        sa.Column("run_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_key", sa.String(length=128), sa.ForeignKey("camera_sources.source_key", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.String(length=64), nullable=False),
        sa.Column("completed_at", sa.String(length=64)),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("camera_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("normalized_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("partial_failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("http_status", sa.Integer()),
        sa.Column("error_text", sa.Text()),
    )
    op.create_index("ix_camera_source_runs_source_key", "camera_source_runs", ["source_key"])
    op.create_index("ix_camera_source_runs_started_at", "camera_source_runs", ["started_at"])
    op.create_index("ix_camera_source_runs_completed_at", "camera_source_runs", ["completed_at"])
    op.create_index("ix_camera_source_runs_status", "camera_source_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_camera_source_runs_status", table_name="camera_source_runs")
    op.drop_index("ix_camera_source_runs_completed_at", table_name="camera_source_runs")
    op.drop_index("ix_camera_source_runs_started_at", table_name="camera_source_runs")
    op.drop_index("ix_camera_source_runs_source_key", table_name="camera_source_runs")
    op.drop_table("camera_source_runs")

    op.drop_index("ix_camera_health_backoff_until", table_name="camera_health")
    op.drop_index("ix_camera_health_next_frame_refresh_at", table_name="camera_health")
    op.drop_index("ix_camera_health_last_metadata_refresh_at", table_name="camera_health")
    op.drop_column("camera_health", "retry_count")
    op.drop_column("camera_health", "backoff_until")
    op.drop_column("camera_health", "next_frame_refresh_at")
    op.drop_column("camera_health", "last_metadata_refresh_at")

    op.drop_index("ix_camera_sources_backoff_until", table_name="camera_sources")
    op.drop_index("ix_camera_sources_next_refresh_at", table_name="camera_sources")
    op.drop_column("camera_sources", "cadence_reason")
    op.drop_column("camera_sources", "cadence_seconds")
    op.drop_column("camera_sources", "last_http_status")
    op.drop_column("camera_sources", "retry_count")
    op.drop_column("camera_sources", "backoff_until")
    op.drop_column("camera_sources", "next_refresh_at")
    op.drop_column("camera_sources", "last_completed_at")
    op.drop_column("camera_sources", "last_started_at")
