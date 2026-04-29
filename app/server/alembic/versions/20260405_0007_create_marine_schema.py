"""create marine schema

Revision ID: 20260405_0007
Revises: 20260404_0006
Create Date: 2026-04-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "20260405_0007"
down_revision = "20260404_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "marine_sources",
        sa.Column("source_key", sa.String(length=128), primary_key=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="never-fetched"),
        sa.Column("detail", sa.Text(), nullable=False, server_default=""),
        sa.Column("stale_after_seconds", sa.Integer()),
        sa.Column("cadence_seconds", sa.Integer()),
        sa.Column("freshness_seconds", sa.Integer()),
        sa.Column("last_success_at", sa.String(length=64)),
        sa.Column("last_attempt_at", sa.String(length=64)),
        sa.Column("last_failure_at", sa.String(length=64)),
        sa.Column("degraded_reason", sa.Text()),
        sa.Column("blocked_reason", sa.Text()),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provenance_notes_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.create_index("ix_marine_sources_status", "marine_sources", ["status"])
    op.create_index("ix_marine_sources_last_success_at", "marine_sources", ["last_success_at"])

    op.create_table(
        "marine_vessel_latest",
        sa.Column("vessel_id", sa.String(length=255), primary_key=True),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("mmsi", sa.String(length=32), nullable=False),
        sa.Column("imo", sa.String(length=32)),
        sa.Column("callsign", sa.String(length=64)),
        sa.Column("vessel_name", sa.String(length=255)),
        sa.Column("flag_state", sa.String(length=16)),
        sa.Column("vessel_class", sa.String(length=64)),
        sa.Column("nav_status", sa.String(length=64)),
        sa.Column("destination", sa.String(length=255)),
        sa.Column("eta", sa.String(length=64)),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("course", sa.Float()),
        sa.Column("heading", sa.Float()),
        sa.Column("speed", sa.Float()),
        sa.Column("observed_at", sa.String(length=64), nullable=False),
        sa.Column("fetched_at", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("source_detail", sa.Text()),
        sa.Column("external_url", sa.Text()),
        sa.Column("confidence", sa.Float()),
        sa.Column("quality_score", sa.Float()),
        sa.Column("quality_label", sa.String(length=64)),
        sa.Column("quality_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("stale", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("degraded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("degraded_reason", sa.Text()),
        sa.Column("source_health", sa.String(length=32)),
        sa.Column("observed_vs_derived", sa.String(length=32), nullable=False, server_default="observed"),
        sa.Column("geometry_provenance", sa.String(length=32), nullable=False, server_default="raw_observed"),
        sa.Column("reference_ref_id", sa.String(length=255)),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("bucket_date", sa.String(length=10), nullable=False),
        sa.Column("bucket_hour", sa.Integer(), nullable=False),
        sa.Column("vessel_shard", sa.Integer(), nullable=False),
        sa.Column("last_event_id", sa.Integer()),
    )
    for name in [
        "source_key",
        "mmsi",
        "imo",
        "callsign",
        "vessel_name",
        "flag_state",
        "vessel_class",
        "nav_status",
        "eta",
        "latitude",
        "longitude",
        "observed_at",
        "fetched_at",
        "status",
        "reference_ref_id",
        "bucket_date",
        "bucket_hour",
        "vessel_shard",
        "last_event_id",
    ]:
        op.create_index(f"ix_marine_vessel_latest_{name}", "marine_vessel_latest", [name])

    op.create_table(
        "marine_position_events",
        sa.Column("event_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("vessel_id", sa.String(length=255), nullable=False),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("mmsi", sa.String(length=32), nullable=False),
        sa.Column("imo", sa.String(length=32)),
        sa.Column("callsign", sa.String(length=64)),
        sa.Column("vessel_name", sa.String(length=255)),
        sa.Column("flag_state", sa.String(length=16)),
        sa.Column("vessel_class", sa.String(length=64)),
        sa.Column("nav_status", sa.String(length=64)),
        sa.Column("destination", sa.String(length=255)),
        sa.Column("eta", sa.String(length=64)),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("course", sa.Float()),
        sa.Column("heading", sa.Float()),
        sa.Column("speed", sa.Float()),
        sa.Column("observed_at", sa.String(length=64), nullable=False),
        sa.Column("fetched_at", sa.String(length=64), nullable=False),
        sa.Column("source_detail", sa.Text()),
        sa.Column("external_url", sa.Text()),
        sa.Column("confidence", sa.Float()),
        sa.Column("quality_score", sa.Float()),
        sa.Column("quality_label", sa.String(length=64)),
        sa.Column("quality_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("observed_vs_derived", sa.String(length=32), nullable=False, server_default="observed"),
        sa.Column("geometry_provenance", sa.String(length=32), nullable=False, server_default="raw_observed"),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("expected_reporting_interval_seconds", sa.Integer()),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("bucket_date", sa.String(length=10), nullable=False),
        sa.Column("bucket_hour", sa.Integer(), nullable=False),
        sa.Column("vessel_shard", sa.Integer(), nullable=False),
        sa.UniqueConstraint("vessel_id", "source_key", "observed_at", name="uq_marine_position_observation"),
    )
    for name in [
        "vessel_id",
        "source_key",
        "mmsi",
        "imo",
        "callsign",
        "vessel_name",
        "flag_state",
        "vessel_class",
        "nav_status",
        "eta",
        "latitude",
        "longitude",
        "observed_at",
        "fetched_at",
        "status",
        "bucket_date",
        "bucket_hour",
        "vessel_shard",
    ]:
        op.create_index(f"ix_marine_position_events_{name}", "marine_position_events", [name])

    op.create_table(
        "marine_gap_events",
        sa.Column("gap_event_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("vessel_id", sa.String(length=255), nullable=False),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("event_kind", sa.String(length=64), nullable=False),
        sa.Column("gap_start_observed_at", sa.String(length=64), nullable=False),
        sa.Column("gap_end_observed_at", sa.String(length=64)),
        sa.Column("gap_duration_seconds", sa.Integer()),
        sa.Column("start_latitude", sa.Float()),
        sa.Column("start_longitude", sa.Float()),
        sa.Column("end_latitude", sa.Float()),
        sa.Column("end_longitude", sa.Float()),
        sa.Column("distance_moved_m", sa.Float()),
        sa.Column("expected_interval_seconds", sa.Integer()),
        sa.Column("exceeds_expected_cadence", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("confidence_class", sa.String(length=16), nullable=False, server_default="low"),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("derivation_method", sa.String(length=64), nullable=False),
        sa.Column("input_event_ids_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("uncertainty_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("evidence_summary", sa.Text()),
        sa.Column("created_at", sa.String(length=64), nullable=False),
        sa.Column("bucket_date", sa.String(length=10), nullable=False),
        sa.Column("bucket_hour", sa.Integer(), nullable=False),
        sa.Column("vessel_shard", sa.Integer(), nullable=False),
    )
    for name in [
        "vessel_id",
        "source_key",
        "event_kind",
        "gap_start_observed_at",
        "gap_end_observed_at",
        "confidence_class",
        "created_at",
        "bucket_date",
        "bucket_hour",
        "vessel_shard",
    ]:
        op.create_index(f"ix_marine_gap_events_{name}", "marine_gap_events", [name])

    op.create_table(
        "marine_replay_snapshots",
        sa.Column("snapshot_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("snapshot_at", sa.String(length=64), nullable=False),
        sa.Column("bucket_date", sa.String(length=10), nullable=False),
        sa.Column("bucket_hour", sa.Integer(), nullable=False),
        sa.Column("scope_kind", sa.String(length=16), nullable=False, server_default="global"),
        sa.Column("bbox_min_lat", sa.Float()),
        sa.Column("bbox_min_lon", sa.Float()),
        sa.Column("bbox_max_lat", sa.Float()),
        sa.Column("bbox_max_lon", sa.Float()),
        sa.Column("vessel_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("position_event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("storage_key", sa.String(length=255)),
        sa.Column("chunk_id", sa.String(length=128)),
        sa.Column("derived_from_event_id", sa.Integer()),
        sa.Column("created_at", sa.String(length=64), nullable=False),
    )
    for name in [
        "snapshot_at",
        "bucket_date",
        "bucket_hour",
        "scope_kind",
        "storage_key",
        "chunk_id",
        "created_at",
    ]:
        op.create_index(f"ix_marine_replay_snapshots_{name}", "marine_replay_snapshots", [name])

    op.create_table(
        "marine_replay_snapshot_members",
        sa.Column("member_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("snapshot_id", sa.Integer(), sa.ForeignKey("marine_replay_snapshots.snapshot_id", ondelete="CASCADE"), nullable=False),
        sa.Column("vessel_id", sa.String(length=255), nullable=False),
        sa.Column("source_key", sa.String(length=128), nullable=False),
        sa.Column("mmsi", sa.String(length=32), nullable=False),
        sa.Column("vessel_name", sa.String(length=255)),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("course", sa.Float()),
        sa.Column("heading", sa.Float()),
        sa.Column("speed", sa.Float()),
        sa.Column("observed_at", sa.String(length=64), nullable=False),
        sa.Column("fetched_at", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column("geometry_provenance", sa.String(length=32), nullable=False, server_default="raw_observed"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
    )
    for name in [
        "snapshot_id",
        "vessel_id",
        "source_key",
        "mmsi",
        "vessel_name",
        "latitude",
        "longitude",
        "observed_at",
        "fetched_at",
        "status",
    ]:
        op.create_index(
            f"ix_marine_replay_snapshot_members_{name}",
            "marine_replay_snapshot_members",
            [name],
        )

    op.create_table(
        "marine_timeline_segments",
        sa.Column("segment_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("segment_start_at", sa.String(length=64), nullable=False),
        sa.Column("segment_end_at", sa.String(length=64), nullable=False),
        sa.Column("bucket_date", sa.String(length=10), nullable=False),
        sa.Column("bucket_hour", sa.Integer(), nullable=False),
        sa.Column("scope_kind", sa.String(length=16), nullable=False, server_default="global"),
        sa.Column("bbox_min_lat", sa.Float()),
        sa.Column("bbox_min_lon", sa.Float()),
        sa.Column("bbox_max_lat", sa.Float()),
        sa.Column("bbox_max_lon", sa.Float()),
        sa.Column("vessel_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("position_event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gap_event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("snapshot_id", sa.Integer()),
        sa.Column("chunk_id", sa.String(length=128)),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
    )
    for name in [
        "segment_start_at",
        "segment_end_at",
        "bucket_date",
        "bucket_hour",
        "scope_kind",
        "snapshot_id",
        "chunk_id",
    ]:
        op.create_index(f"ix_marine_timeline_segments_{name}", "marine_timeline_segments", [name])


def downgrade() -> None:
    for name in [
        "segment_start_at",
        "segment_end_at",
        "bucket_date",
        "bucket_hour",
        "scope_kind",
        "snapshot_id",
        "chunk_id",
    ]:
        op.drop_index(f"ix_marine_timeline_segments_{name}", table_name="marine_timeline_segments")
    op.drop_table("marine_timeline_segments")

    for name in [
        "snapshot_id",
        "vessel_id",
        "source_key",
        "mmsi",
        "vessel_name",
        "latitude",
        "longitude",
        "observed_at",
        "fetched_at",
        "status",
    ]:
        op.drop_index(
            f"ix_marine_replay_snapshot_members_{name}",
            table_name="marine_replay_snapshot_members",
        )
    op.drop_table("marine_replay_snapshot_members")

    for name in [
        "snapshot_at",
        "bucket_date",
        "bucket_hour",
        "scope_kind",
        "storage_key",
        "chunk_id",
        "created_at",
    ]:
        op.drop_index(f"ix_marine_replay_snapshots_{name}", table_name="marine_replay_snapshots")
    op.drop_table("marine_replay_snapshots")

    for name in [
        "vessel_id",
        "source_key",
        "event_kind",
        "gap_start_observed_at",
        "gap_end_observed_at",
        "confidence_class",
        "created_at",
        "bucket_date",
        "bucket_hour",
        "vessel_shard",
    ]:
        op.drop_index(f"ix_marine_gap_events_{name}", table_name="marine_gap_events")
    op.drop_table("marine_gap_events")

    for name in [
        "vessel_id",
        "source_key",
        "mmsi",
        "imo",
        "callsign",
        "vessel_name",
        "flag_state",
        "vessel_class",
        "nav_status",
        "eta",
        "latitude",
        "longitude",
        "observed_at",
        "fetched_at",
        "status",
        "bucket_date",
        "bucket_hour",
        "vessel_shard",
    ]:
        op.drop_index(f"ix_marine_position_events_{name}", table_name="marine_position_events")
    op.drop_table("marine_position_events")

    for name in [
        "source_key",
        "mmsi",
        "imo",
        "callsign",
        "vessel_name",
        "flag_state",
        "vessel_class",
        "nav_status",
        "eta",
        "latitude",
        "longitude",
        "observed_at",
        "fetched_at",
        "status",
        "reference_ref_id",
        "bucket_date",
        "bucket_hour",
        "vessel_shard",
        "last_event_id",
    ]:
        op.drop_index(f"ix_marine_vessel_latest_{name}", table_name="marine_vessel_latest")
    op.drop_table("marine_vessel_latest")

    op.drop_index("ix_marine_sources_last_success_at", table_name="marine_sources")
    op.drop_index("ix_marine_sources_status", table_name="marine_sources")
    op.drop_table("marine_sources")
