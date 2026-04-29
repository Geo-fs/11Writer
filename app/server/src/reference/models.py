from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ReferenceObjectORM(Base):
    __tablename__ = "reference_objects"
    __table_args__ = (
        UniqueConstraint("object_type", "source_dataset", "source_key", name="uq_reference_objects_source"),
    )

    ref_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    object_type: Mapped[str] = mapped_column(String(32), index=True)
    canonical_name: Mapped[str] = mapped_column(String(255), index=True)
    primary_code: Mapped[str | None] = mapped_column(String(64), index=True)
    source_dataset: Mapped[str] = mapped_column(String(64), index=True)
    source_key: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="active")
    country_code: Mapped[str | None] = mapped_column(String(8), index=True)
    admin1_code: Mapped[str | None] = mapped_column(String(32), index=True)
    centroid_lat: Mapped[float | None] = mapped_column(Float)
    centroid_lon: Mapped[float | None] = mapped_column(Float)
    bbox_min_lat: Mapped[float | None] = mapped_column(Float)
    bbox_min_lon: Mapped[float | None] = mapped_column(Float)
    bbox_max_lat: Mapped[float | None] = mapped_column(Float)
    bbox_max_lon: Mapped[float | None] = mapped_column(Float)
    geometry_json: Mapped[str | None] = mapped_column(Text)
    coverage_tier: Mapped[str] = mapped_column(String(32), default="baseline")
    search_text: Mapped[str | None] = mapped_column(Text)
    source_version: Mapped[str | None] = mapped_column(String(64))
    last_ingested_at: Mapped[str | None] = mapped_column(String(64))

    airport: Mapped[AirportORM | None] = relationship(back_populates="reference", uselist=False)
    runway: Mapped[RunwayORM | None] = relationship(back_populates="reference", uselist=False)
    navaid: Mapped[NavaidORM | None] = relationship(back_populates="reference", uselist=False)
    fix: Mapped[FixORM | None] = relationship(back_populates="reference", uselist=False)
    region: Mapped[RegionORM | None] = relationship(back_populates="reference", uselist=False)
    aliases: Mapped[list[ReferenceAliasORM]] = relationship(
        back_populates="reference",
        cascade="all, delete-orphan",
    )
    links: Mapped[list[ReferenceLinkORM]] = relationship(
        back_populates="reference",
        cascade="all, delete-orphan",
    )


class AirportORM(Base):
    __tablename__ = "airports"

    ref_id: Mapped[str] = mapped_column(
        ForeignKey("reference_objects.ref_id", ondelete="CASCADE"),
        primary_key=True,
    )
    icao_code: Mapped[str | None] = mapped_column(String(16), index=True)
    iata_code: Mapped[str | None] = mapped_column(String(16), index=True)
    local_code: Mapped[str | None] = mapped_column(String(16), index=True)
    airport_type: Mapped[str | None] = mapped_column(String(64), index=True)
    elevation_ft: Mapped[float | None] = mapped_column(Float)
    municipality: Mapped[str | None] = mapped_column(String(255), index=True)
    iso_region: Mapped[str | None] = mapped_column(String(32), index=True)
    scheduled_service: Mapped[bool] = mapped_column(Boolean, default=False)
    gps_code: Mapped[str | None] = mapped_column(String(16), index=True)
    continent_code: Mapped[str | None] = mapped_column(String(8), index=True)
    timezone_name: Mapped[str | None] = mapped_column(String(64))
    keyword_text: Mapped[str | None] = mapped_column(Text)

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="airport")


class RunwayORM(Base):
    __tablename__ = "runways"

    ref_id: Mapped[str] = mapped_column(
        ForeignKey("reference_objects.ref_id", ondelete="CASCADE"),
        primary_key=True,
    )
    airport_ref_id: Mapped[str] = mapped_column(ForeignKey("airports.ref_id", ondelete="CASCADE"), index=True)
    le_ident: Mapped[str | None] = mapped_column(String(16), index=True)
    he_ident: Mapped[str | None] = mapped_column(String(16), index=True)
    length_ft: Mapped[float | None] = mapped_column(Float)
    width_ft: Mapped[float | None] = mapped_column(Float)
    surface: Mapped[str | None] = mapped_column(String(64))
    le_heading_deg: Mapped[float | None] = mapped_column(Float)
    he_heading_deg: Mapped[float | None] = mapped_column(Float)
    le_latitude_deg: Mapped[float | None] = mapped_column(Float)
    le_longitude_deg: Mapped[float | None] = mapped_column(Float)
    he_latitude_deg: Mapped[float | None] = mapped_column(Float)
    he_longitude_deg: Mapped[float | None] = mapped_column(Float)
    closed: Mapped[bool] = mapped_column(Boolean, default=False)
    lighted: Mapped[bool] = mapped_column(Boolean, default=False)
    surface_category: Mapped[str | None] = mapped_column(String(32), index=True)
    threshold_pair_code: Mapped[str | None] = mapped_column(String(32), index=True)
    center_latitude_deg: Mapped[float | None] = mapped_column(Float)
    center_longitude_deg: Mapped[float | None] = mapped_column(Float)

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="runway")


class NavaidORM(Base):
    __tablename__ = "navaids"

    ref_id: Mapped[str] = mapped_column(
        ForeignKey("reference_objects.ref_id", ondelete="CASCADE"),
        primary_key=True,
    )
    ident: Mapped[str | None] = mapped_column(String(16), index=True)
    navaid_type: Mapped[str | None] = mapped_column(String(64), index=True)
    frequency_khz: Mapped[float | None] = mapped_column(Float, index=True)
    elevation_ft: Mapped[float | None] = mapped_column(Float)
    associated_airport_ref_id: Mapped[str | None] = mapped_column(
        ForeignKey("airports.ref_id", ondelete="SET NULL"),
        index=True,
    )
    power: Mapped[str | None] = mapped_column(String(32))
    usage: Mapped[str | None] = mapped_column(String(64))
    magnetic_variation_deg: Mapped[float | None] = mapped_column(Float)
    name_normalized: Mapped[str | None] = mapped_column(String(255), index=True)

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="navaid")


class FixORM(Base):
    __tablename__ = "fixes"

    ref_id: Mapped[str] = mapped_column(
        ForeignKey("reference_objects.ref_id", ondelete="CASCADE"),
        primary_key=True,
    )
    ident: Mapped[str | None] = mapped_column(String(16), index=True)
    fix_type: Mapped[str | None] = mapped_column(String(64), index=True)
    jurisdiction: Mapped[str | None] = mapped_column(String(64), index=True)
    usage_class: Mapped[str | None] = mapped_column(String(64), index=True)
    artcc: Mapped[str | None] = mapped_column(String(16), index=True)
    state_code: Mapped[str | None] = mapped_column(String(16), index=True)
    route_usage: Mapped[str | None] = mapped_column(String(64), index=True)

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="fix")


class RegionORM(Base):
    __tablename__ = "regions"

    ref_id: Mapped[str] = mapped_column(
        ForeignKey("reference_objects.ref_id", ondelete="CASCADE"),
        primary_key=True,
    )
    region_kind: Mapped[str] = mapped_column(String(32), index=True)
    parent_ref_id: Mapped[str | None] = mapped_column(
        ForeignKey("regions.ref_id", ondelete="SET NULL"),
        index=True,
    )
    geometry_quality: Mapped[str | None] = mapped_column(String(32))
    place_class: Mapped[str | None] = mapped_column(String(32), index=True)
    population: Mapped[int | None] = mapped_column(Integer)
    rank: Mapped[int | None] = mapped_column(Integer, index=True)

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="region")


class ReferenceAliasORM(Base):
    __tablename__ = "reference_aliases"

    alias_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref_id: Mapped[str] = mapped_column(ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), index=True)
    alias: Mapped[str] = mapped_column(String(255), index=True)
    normalized_alias: Mapped[str] = mapped_column(String(255), index=True)
    alias_kind: Mapped[str] = mapped_column(String(32), default="alternate")

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="aliases")


class ReferenceLinkORM(Base):
    __tablename__ = "reference_links"
    __table_args__ = (
        UniqueConstraint(
            "external_system",
            "external_object_type",
            "external_object_id",
            "ref_id",
            "link_kind",
            name="uq_reference_links_external",
        ),
    )

    link_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_system: Mapped[str] = mapped_column(String(64), index=True)
    external_object_type: Mapped[str] = mapped_column(String(64), index=True)
    external_object_id: Mapped[str] = mapped_column(String(255), index=True)
    ref_id: Mapped[str] = mapped_column(ForeignKey("reference_objects.ref_id", ondelete="CASCADE"), index=True)
    link_kind: Mapped[str] = mapped_column(String(32), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    method: Mapped[str] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(32), default="approved", index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(255), index=True)
    reviewed_at: Mapped[str | None] = mapped_column(String(64), index=True)
    review_source: Mapped[str | None] = mapped_column(String(128))
    candidate_method: Mapped[str | None] = mapped_column(String(128))
    candidate_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[str | None] = mapped_column(String(64), index=True)
    updated_at: Mapped[str | None] = mapped_column(String(64), index=True)

    reference: Mapped[ReferenceObjectORM] = relationship(back_populates="links")


class DatasetLoadORM(Base):
    __tablename__ = "reference_dataset_loads"

    load_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_name: Mapped[str] = mapped_column(String(64), index=True)
    dataset_version: Mapped[str | None] = mapped_column(String(64))
    coverage: Mapped[str | None] = mapped_column(String(64))
    checksum: Mapped[str | None] = mapped_column(String(128))
    source_path: Mapped[str | None] = mapped_column(String(512))
    loaded_at: Mapped[str] = mapped_column(String(64))
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
