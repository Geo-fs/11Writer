"""expand reference authority fields

Revision ID: 20260404_0003
Revises: 20260404_0002
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0003"
down_revision = "20260404_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reference_objects", sa.Column("search_text", sa.Text()))

    op.add_column("airports", sa.Column("continent_code", sa.String(length=8)))
    op.add_column("airports", sa.Column("timezone_name", sa.String(length=64)))
    op.add_column("airports", sa.Column("keyword_text", sa.Text()))
    op.create_index("ix_airports_continent_code", "airports", ["continent_code"])

    op.add_column("runways", sa.Column("closed", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("runways", sa.Column("lighted", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("runways", sa.Column("surface_category", sa.String(length=32)))
    op.add_column("runways", sa.Column("threshold_pair_code", sa.String(length=32)))
    op.add_column("runways", sa.Column("center_latitude_deg", sa.Float()))
    op.add_column("runways", sa.Column("center_longitude_deg", sa.Float()))
    op.create_index("ix_runways_surface_category", "runways", ["surface_category"])
    op.create_index("ix_runways_threshold_pair_code", "runways", ["threshold_pair_code"])

    op.add_column("navaids", sa.Column("power", sa.String(length=32)))
    op.add_column("navaids", sa.Column("usage", sa.String(length=64)))
    op.add_column("navaids", sa.Column("magnetic_variation_deg", sa.Float()))
    op.add_column("navaids", sa.Column("name_normalized", sa.String(length=255)))
    op.create_index("ix_navaids_name_normalized", "navaids", ["name_normalized"])

    op.add_column("fixes", sa.Column("artcc", sa.String(length=16)))
    op.add_column("fixes", sa.Column("state_code", sa.String(length=16)))
    op.add_column("fixes", sa.Column("route_usage", sa.String(length=64)))
    op.create_index("ix_fixes_artcc", "fixes", ["artcc"])
    op.create_index("ix_fixes_state_code", "fixes", ["state_code"])
    op.create_index("ix_fixes_route_usage", "fixes", ["route_usage"])

    op.add_column("regions", sa.Column("place_class", sa.String(length=32)))
    op.add_column("regions", sa.Column("population", sa.Integer()))
    op.add_column("regions", sa.Column("rank", sa.Integer()))
    op.create_index("ix_regions_place_class", "regions", ["place_class"])
    op.create_index("ix_regions_rank", "regions", ["rank"])


def downgrade() -> None:
    op.drop_index("ix_regions_rank", table_name="regions")
    op.drop_index("ix_regions_place_class", table_name="regions")
    op.drop_column("regions", "rank")
    op.drop_column("regions", "population")
    op.drop_column("regions", "place_class")

    op.drop_index("ix_fixes_route_usage", table_name="fixes")
    op.drop_index("ix_fixes_state_code", table_name="fixes")
    op.drop_index("ix_fixes_artcc", table_name="fixes")
    op.drop_column("fixes", "route_usage")
    op.drop_column("fixes", "state_code")
    op.drop_column("fixes", "artcc")

    op.drop_index("ix_navaids_name_normalized", table_name="navaids")
    op.drop_column("navaids", "name_normalized")
    op.drop_column("navaids", "magnetic_variation_deg")
    op.drop_column("navaids", "usage")
    op.drop_column("navaids", "power")

    op.drop_index("ix_runways_threshold_pair_code", table_name="runways")
    op.drop_index("ix_runways_surface_category", table_name="runways")
    op.drop_column("runways", "center_longitude_deg")
    op.drop_column("runways", "center_latitude_deg")
    op.drop_column("runways", "threshold_pair_code")
    op.drop_column("runways", "surface_category")
    op.drop_column("runways", "lighted")
    op.drop_column("runways", "closed")

    op.drop_index("ix_airports_continent_code", table_name="airports")
    op.drop_column("airports", "keyword_text")
    op.drop_column("airports", "timezone_name")
    op.drop_column("airports", "continent_code")

    op.drop_column("reference_objects", "search_text")
