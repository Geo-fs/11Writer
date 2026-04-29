"""create webcam schema

Revision ID: 20260404_0002
Revises: 20260404_0001
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0002"
down_revision = "20260404_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "camera_sources",
        sa.Column("source_key", sa.String(length=128), primary_key=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("coverage", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("authentication", sa.String(length=32), nullable=False),
        sa.Column("default_refresh_interval_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="never-fetched"),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("credentials_configured", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("blocked_reason", sa.Text()),
        sa.Column("degraded_reason", sa.Text()),
        sa.Column("review_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_attempt_at", sa.String(length=64)),
        sa.Column("last_success_at", sa.String(length=64)),
        sa.Column("last_failure_at", sa.String(length=64)),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_camera_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("attribution_text", sa.Text(), nullable=False),
        sa.Column("attribution_url", sa.Text()),
        sa.Column("terms_url", sa.Text()),
        sa.Column("license_summary", sa.Text()),
        sa.Column("requires_authentication", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("supports_embedding", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("supports_frame_storage", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("compliance_review_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provenance_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("compliance_notes_json", sa.Text(), nullable=False, server_default="[]"),
    )
    for name in ["source_type", "status"]:
        op.create_index(f"ix_camera_sources_{name}", "camera_sources", [name])

    op.create_table(
        "camera_records",
        sa.Column("camera_id", sa.String(length=255), primary_key=True),
        sa.Column("source_key", sa.String(length=128), sa.ForeignKey("camera_sources.source_key", ondelete="CASCADE"), nullable=False),
        sa.Column("source_camera_id", sa.String(length=255)),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("owner", sa.String(length=255)),
        sa.Column("state", sa.String(length=32)),
        sa.Column("county", sa.String(length=128)),
        sa.Column("region", sa.String(length=128)),
        sa.Column("roadway", sa.String(length=255)),
        sa.Column("direction", sa.String(length=64)),
        sa.Column("location_description", sa.Text()),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("altitude", sa.Float(), nullable=False, server_default="0"),
        sa.Column("heading", sa.Float()),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("feed_type", sa.String(length=32)),
        sa.Column("access_policy", sa.String(length=64)),
        sa.Column("external_url", sa.Text()),
        sa.Column("confidence", sa.Float()),
        sa.Column("position_kind", sa.String(length=32), nullable=False),
        sa.Column("position_confidence", sa.Float()),
        sa.Column("position_source", sa.Text()),
        sa.Column("position_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("orientation_kind", sa.String(length=32), nullable=False),
        sa.Column("orientation_degrees", sa.Float()),
        sa.Column("orientation_cardinal_direction", sa.String(length=64)),
        sa.Column("orientation_confidence", sa.Float()),
        sa.Column("orientation_source", sa.Text()),
        sa.Column("orientation_is_ptz", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("orientation_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("frame_status", sa.String(length=32), nullable=False),
        sa.Column("frame_refresh_interval_seconds", sa.Integer()),
        sa.Column("frame_image_url", sa.Text()),
        sa.Column("frame_thumbnail_url", sa.Text()),
        sa.Column("frame_stream_url", sa.Text()),
        sa.Column("frame_viewer_url", sa.Text()),
        sa.Column("frame_width", sa.Integer()),
        sa.Column("frame_height", sa.Integer()),
        sa.Column("last_frame_at", sa.String(length=64)),
        sa.Column("last_metadata_refresh_at", sa.String(length=64)),
        sa.Column("health_state", sa.String(length=32)),
        sa.Column("degraded_reason", sa.Text()),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("review_reason", sa.Text()),
        sa.Column("review_required_actions_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("review_issue_categories_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("nearest_reference_ref_id", sa.String(length=255)),
        sa.Column("reference_link_status", sa.String(length=64)),
        sa.Column("link_candidate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reference_hint_text", sa.Text()),
        sa.Column("facility_code_hint", sa.String(length=64)),
        sa.Column("raw_payload_json", sa.Text(), nullable=False, server_default="{}"),
    )
    for name in [
        "source_key",
        "source_camera_id",
        "label",
        "state",
        "roadway",
        "latitude",
        "longitude",
        "status",
        "position_kind",
        "orientation_kind",
        "last_frame_at",
        "last_metadata_refresh_at",
        "health_state",
        "review_status",
        "nearest_reference_ref_id",
    ]:
        op.create_index(f"ix_camera_records_{name}", "camera_records", [name])

    op.create_table(
        "camera_frames",
        sa.Column("frame_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("camera_id", sa.String(length=255), sa.ForeignKey("camera_records.camera_id", ondelete="CASCADE"), nullable=False),
        sa.Column("fetched_at", sa.String(length=64), nullable=False),
        sa.Column("captured_at", sa.String(length=64)),
        sa.Column("source_frame_url", sa.Text()),
        sa.Column("frame_hash", sa.String(length=128)),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("age_seconds", sa.Integer()),
    )
    for name in ["camera_id", "fetched_at", "captured_at", "frame_hash", "status"]:
        op.create_index(f"ix_camera_frames_{name}", "camera_frames", [name])

    op.create_table(
        "camera_health",
        sa.Column("camera_id", sa.String(length=255), sa.ForeignKey("camera_records.camera_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("health_state", sa.String(length=32), nullable=False),
        sa.Column("last_attempt_at", sa.String(length=64)),
        sa.Column("last_success_at", sa.String(length=64)),
        sa.Column("last_failure_at", sa.String(length=64)),
        sa.Column("freshness_seconds", sa.Integer()),
        sa.Column("stale_after_seconds", sa.Integer()),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("degraded_reason", sa.Text()),
        sa.Column("blocked_reason", sa.Text()),
        sa.Column("last_http_status", sa.Integer()),
    )
    for name in ["source_key", "health_state"]:
        op.create_index(f"ix_camera_health_{name}", "camera_health", [name])

    op.create_table(
        "camera_review_queue",
        sa.Column("review_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("camera_id", sa.String(length=255), sa.ForeignKey("camera_records.camera_id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("issue_category", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("required_action", sa.Text(), nullable=False),
        sa.Column("context_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("created_at", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("camera_id", "issue_category", "reason", name="uq_camera_review_issue"),
    )
    for name in ["camera_id", "source_key", "priority", "issue_category", "status", "created_at"]:
        op.create_index(f"ix_camera_review_queue_{name}", "camera_review_queue", [name])


def downgrade() -> None:
    for name in ["camera_id", "source_key", "priority", "issue_category", "status", "created_at"]:
        op.drop_index(f"ix_camera_review_queue_{name}", table_name="camera_review_queue")
    op.drop_table("camera_review_queue")

    for name in ["source_key", "health_state"]:
        op.drop_index(f"ix_camera_health_{name}", table_name="camera_health")
    op.drop_table("camera_health")

    for name in ["camera_id", "fetched_at", "captured_at", "frame_hash", "status"]:
        op.drop_index(f"ix_camera_frames_{name}", table_name="camera_frames")
    op.drop_table("camera_frames")

    for name in [
        "source_key",
        "source_camera_id",
        "label",
        "state",
        "roadway",
        "latitude",
        "longitude",
        "status",
        "position_kind",
        "orientation_kind",
        "last_frame_at",
        "last_metadata_refresh_at",
        "health_state",
        "review_status",
        "nearest_reference_ref_id",
    ]:
        op.drop_index(f"ix_camera_records_{name}", table_name="camera_records")
    op.drop_table("camera_records")

    for name in ["source_type", "status"]:
        op.drop_index(f"ix_camera_sources_{name}", table_name="camera_sources")
    op.drop_table("camera_sources")
