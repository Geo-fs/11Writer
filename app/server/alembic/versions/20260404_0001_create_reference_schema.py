"""create reference schema

Revision ID: 20260404_0001
Revises:
Create Date: 2026-04-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260404_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reference_objects",
        sa.Column("ref_id", sa.String(length=255), primary_key=True),
        sa.Column("object_type", sa.String(length=32), nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("primary_code", sa.String(length=64)),
        sa.Column("source_dataset", sa.String(length=64), nullable=False),
        sa.Column("source_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("country_code", sa.String(length=8)),
        sa.Column("admin1_code", sa.String(length=32)),
        sa.Column("centroid_lat", sa.Float()),
        sa.Column("centroid_lon", sa.Float()),
        sa.Column("bbox_min_lat", sa.Float()),
        sa.Column("bbox_min_lon", sa.Float()),
        sa.Column("bbox_max_lat", sa.Float()),
        sa.Column("bbox_max_lon", sa.Float()),
        sa.Column("geometry_json", sa.Text()),
        sa.Column("coverage_tier", sa.String(length=32), nullable=False, server_default="baseline"),
        sa.Column("source_version", sa.String(length=64)),
        sa.Column("last_ingested_at", sa.String(length=64)),
        sa.UniqueConstraint("object_type", "source_dataset", "source_key", name="uq_reference_objects_source"),
    )
    op.create_index("ix_reference_objects_object_type", "reference_objects", ["object_type"])
    op.create_index("ix_reference_objects_canonical_name", "reference_objects", ["canonical_name"])
    op.create_index("ix_reference_objects_primary_code", "reference_objects", ["primary_code"])
    op.create_index("ix_reference_objects_source_dataset", "reference_objects", ["source_dataset"])
    op.create_index("ix_reference_objects_country_code", "reference_objects", ["country_code"])
    op.create_index("ix_reference_objects_admin1_code", "reference_objects", ["admin1_code"])

    op.create_table(
        "airports",
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("icao_code", sa.String(length=16)),
        sa.Column("iata_code", sa.String(length=16)),
        sa.Column("local_code", sa.String(length=16)),
        sa.Column("airport_type", sa.String(length=64)),
        sa.Column("elevation_ft", sa.Float()),
        sa.Column("municipality", sa.String(length=255)),
        sa.Column("iso_region", sa.String(length=32)),
        sa.Column("scheduled_service", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("gps_code", sa.String(length=16)),
    )
    for name in ["icao_code", "iata_code", "local_code", "airport_type", "municipality", "iso_region", "gps_code"]:
        op.create_index(f"ix_airports_{name}", "airports", [name])

    op.create_table(
        "runways",
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("airport_ref_id", sa.String(length=255), sa.ForeignKey("airports.ref_id", ondelete="CASCADE"), nullable=False),
        sa.Column("le_ident", sa.String(length=16)),
        sa.Column("he_ident", sa.String(length=16)),
        sa.Column("length_ft", sa.Float()),
        sa.Column("width_ft", sa.Float()),
        sa.Column("surface", sa.String(length=64)),
        sa.Column("le_heading_deg", sa.Float()),
        sa.Column("he_heading_deg", sa.Float()),
        sa.Column("le_latitude_deg", sa.Float()),
        sa.Column("le_longitude_deg", sa.Float()),
        sa.Column("he_latitude_deg", sa.Float()),
        sa.Column("he_longitude_deg", sa.Float()),
    )
    for name in ["airport_ref_id", "le_ident", "he_ident"]:
        op.create_index(f"ix_runways_{name}", "runways", [name])

    op.create_table(
        "navaids",
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("ident", sa.String(length=16)),
        sa.Column("navaid_type", sa.String(length=64)),
        sa.Column("frequency_khz", sa.Float()),
        sa.Column("elevation_ft", sa.Float()),
        sa.Column("associated_airport_ref_id", sa.String(length=255), sa.ForeignKey("airports.ref_id", ondelete="SET NULL")),
    )
    for name in ["ident", "navaid_type", "frequency_khz", "associated_airport_ref_id"]:
        op.create_index(f"ix_navaids_{name}", "navaids", [name])

    op.create_table(
        "fixes",
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("ident", sa.String(length=16)),
        sa.Column("fix_type", sa.String(length=64)),
        sa.Column("jurisdiction", sa.String(length=64)),
        sa.Column("usage_class", sa.String(length=64)),
    )
    for name in ["ident", "fix_type", "jurisdiction", "usage_class"]:
        op.create_index(f"ix_fixes_{name}", "fixes", [name])

    op.create_table(
        "regions",
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("region_kind", sa.String(length=32), nullable=False),
        sa.Column("parent_ref_id", sa.String(length=255), sa.ForeignKey("regions.ref_id", ondelete="SET NULL")),
        sa.Column("geometry_quality", sa.String(length=32)),
    )
    for name in ["region_kind", "parent_ref_id"]:
        op.create_index(f"ix_regions_{name}", "regions", [name])

    op.create_table(
        "reference_aliases",
        sa.Column("alias_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("normalized_alias", sa.String(length=255), nullable=False),
        sa.Column("alias_kind", sa.String(length=32), nullable=False, server_default="alternate"),
    )
    for name in ["ref_id", "alias", "normalized_alias"]:
        op.create_index(f"ix_reference_aliases_{name}", "reference_aliases", [name])

    op.create_table(
        "reference_links",
        sa.Column("link_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("external_system", sa.String(length=64), nullable=False),
        sa.Column("external_object_type", sa.String(length=64), nullable=False),
        sa.Column("external_object_id", sa.String(length=255), nullable=False),
        sa.Column("ref_id", sa.String(length=255), sa.ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), nullable=False),
        sa.Column("link_kind", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("method", sa.String(length=128), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.UniqueConstraint(
            "external_system",
            "external_object_type",
            "external_object_id",
            "ref_id",
            "link_kind",
            name="uq_reference_links_external",
        ),
    )
    for name in ["external_system", "external_object_type", "external_object_id", "ref_id", "link_kind"]:
        op.create_index(f"ix_reference_links_{name}", "reference_links", [name])

    op.create_table(
        "reference_dataset_loads",
        sa.Column("load_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("dataset_name", sa.String(length=64), nullable=False),
        sa.Column("dataset_version", sa.String(length=64)),
        sa.Column("coverage", sa.String(length=64)),
        sa.Column("checksum", sa.String(length=128)),
        sa.Column("source_path", sa.String(length=512)),
        sa.Column("loaded_at", sa.String(length=64), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text()),
    )
    op.create_index("ix_reference_dataset_loads_dataset_name", "reference_dataset_loads", ["dataset_name"])

    op.execute(
        """
        CREATE VIRTUAL TABLE reference_spatial_index USING rtree(
            ref_rowid,
            min_lat,
            max_lat,
            min_lon,
            max_lon
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS reference_spatial_index")
    op.drop_index("ix_reference_dataset_loads_dataset_name", table_name="reference_dataset_loads")
    op.drop_table("reference_dataset_loads")
    for name in ["external_system", "external_object_type", "external_object_id", "ref_id", "link_kind"]:
        op.drop_index(f"ix_reference_links_{name}", table_name="reference_links")
    op.drop_table("reference_links")
    for name in ["ref_id", "alias", "normalized_alias"]:
        op.drop_index(f"ix_reference_aliases_{name}", table_name="reference_aliases")
    op.drop_table("reference_aliases")
    for name in ["region_kind", "parent_ref_id"]:
        op.drop_index(f"ix_regions_{name}", table_name="regions")
    op.drop_table("regions")
    for name in ["ident", "fix_type", "jurisdiction", "usage_class"]:
        op.drop_index(f"ix_fixes_{name}", table_name="fixes")
    op.drop_table("fixes")
    for name in ["ident", "navaid_type", "frequency_khz", "associated_airport_ref_id"]:
        op.drop_index(f"ix_navaids_{name}", table_name="navaids")
    op.drop_table("navaids")
    for name in ["airport_ref_id", "le_ident", "he_ident"]:
        op.drop_index(f"ix_runways_{name}", table_name="runways")
    op.drop_table("runways")
    for name in ["icao_code", "iata_code", "local_code", "airport_type", "municipality", "iso_region", "gps_code"]:
        op.drop_index(f"ix_airports_{name}", table_name="airports")
    op.drop_table("airports")
    for name in ["object_type", "canonical_name", "primary_code", "source_dataset", "country_code", "admin1_code"]:
        op.drop_index(f"ix_reference_objects_{name}", table_name="reference_objects")
    op.drop_table("reference_objects")
