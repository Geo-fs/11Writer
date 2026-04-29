"""add camera source inventory

Revision ID: 20260404_0007
Revises: 20260404_0006
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0007"
down_revision = "20260404_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "camera_source_inventory",
        sa.Column("source_key", sa.String(length=128), primary_key=True),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_family", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("access_method", sa.String(length=32), nullable=False),
        sa.Column("onboarding_state", sa.String(length=32), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("authentication", sa.String(length=32), nullable=False),
        sa.Column("credentials_configured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rate_limit_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("coverage_geography", sa.Text(), nullable=False),
        sa.Column("coverage_states_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("coverage_regions_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("provides_exact_coordinates", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provides_direction_text", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provides_numeric_heading", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provides_direct_image", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provides_viewer_only", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("supports_embed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("supports_storage", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("attribution_text", sa.Text(), nullable=False),
        sa.Column("attribution_url", sa.Text()),
        sa.Column("terms_url", sa.Text()),
        sa.Column("license_summary", sa.Text()),
        sa.Column("requires_authentication", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("compliance_review_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("provenance_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("compliance_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("source_quality_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("source_stability_notes_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("blocked_reason", sa.Text()),
        sa.Column("approximate_camera_count", sa.Integer()),
        sa.Column("last_catalog_import_at", sa.String(length=64)),
        sa.Column("last_catalog_import_status", sa.String(length=32)),
        sa.Column("last_catalog_import_detail", sa.Text()),
    )
    op.create_index("ix_camera_source_inventory_source_name", "camera_source_inventory", ["source_name"])
    op.create_index("ix_camera_source_inventory_source_family", "camera_source_inventory", ["source_family"])
    op.create_index("ix_camera_source_inventory_source_type", "camera_source_inventory", ["source_type"])
    op.create_index("ix_camera_source_inventory_access_method", "camera_source_inventory", ["access_method"])
    op.create_index("ix_camera_source_inventory_onboarding_state", "camera_source_inventory", ["onboarding_state"])
    op.create_index("ix_camera_source_inventory_last_catalog_import_at", "camera_source_inventory", ["last_catalog_import_at"])

    op.create_table(
        "camera_source_inventory_runs",
        sa.Column("run_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "source_key",
            sa.String(length=128),
            sa.ForeignKey("camera_source_inventory.source_key", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("started_at", sa.String(length=64), nullable=False),
        sa.Column("completed_at", sa.String(length=64)),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("discovered_camera_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_camera_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("detail", sa.Text()),
    )
    op.create_index("ix_camera_source_inventory_runs_source_key", "camera_source_inventory_runs", ["source_key"])
    op.create_index("ix_camera_source_inventory_runs_started_at", "camera_source_inventory_runs", ["started_at"])
    op.create_index("ix_camera_source_inventory_runs_status", "camera_source_inventory_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_camera_source_inventory_runs_status", table_name="camera_source_inventory_runs")
    op.drop_index("ix_camera_source_inventory_runs_started_at", table_name="camera_source_inventory_runs")
    op.drop_index("ix_camera_source_inventory_runs_source_key", table_name="camera_source_inventory_runs")
    op.drop_table("camera_source_inventory_runs")

    op.drop_index("ix_camera_source_inventory_last_catalog_import_at", table_name="camera_source_inventory")
    op.drop_index("ix_camera_source_inventory_onboarding_state", table_name="camera_source_inventory")
    op.drop_index("ix_camera_source_inventory_access_method", table_name="camera_source_inventory")
    op.drop_index("ix_camera_source_inventory_source_type", table_name="camera_source_inventory")
    op.drop_index("ix_camera_source_inventory_source_family", table_name="camera_source_inventory")
    op.drop_index("ix_camera_source_inventory_source_name", table_name="camera_source_inventory")
    op.drop_table("camera_source_inventory")
