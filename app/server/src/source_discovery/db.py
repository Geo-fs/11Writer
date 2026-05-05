from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, sessionmaker

from src.reference.db import get_engine
from src.source_discovery.models import SourceDiscoveryBase


def init_db(database_url: str) -> None:
    engine = get_engine(database_url)
    SourceDiscoveryBase.metadata.create_all(engine)
    if database_url.startswith("sqlite"):
        _backfill_sqlite_columns(engine)


def _backfill_sqlite_columns(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    statements = []
    if "source_reputation_events" in table_names:
        existing = {column["name"] for column in inspector.get_columns("source_reputation_events")}
        if "reversed_at" not in existing:
            statements.append("ALTER TABLE source_reputation_events ADD COLUMN reversed_at VARCHAR(64)")
        if "reversal_reason" not in existing:
            statements.append("ALTER TABLE source_reputation_events ADD COLUMN reversal_reason TEXT")
    if "source_memories" in table_names:
        memory_columns = {column["name"] for column in inspector.get_columns("source_memories")}
        if "canonical_url" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN canonical_url VARCHAR(1024)")
        if "domain_scope" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN domain_scope VARCHAR(255) DEFAULT 'unknown'")
        if "owner_lane" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN owner_lane VARCHAR(64)")
        if "next_check_at" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN next_check_at VARCHAR(64)")
        if "last_discovery_scan_at" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN last_discovery_scan_at VARCHAR(64)")
        if "next_discovery_scan_at" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN next_discovery_scan_at VARCHAR(64)")
        if "discovery_scan_fail_count" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN discovery_scan_fail_count INTEGER DEFAULT 0")
        if "discovery_low_yield_count" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN discovery_low_yield_count INTEGER DEFAULT 0")
        if "health_check_fail_count" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN health_check_fail_count INTEGER DEFAULT 0")
        if "auth_requirement" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN auth_requirement VARCHAR(32) DEFAULT 'unknown'")
        if "captcha_requirement" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN captcha_requirement VARCHAR(32) DEFAULT 'unknown'")
        if "intake_disposition" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN intake_disposition VARCHAR(32) DEFAULT 'hold_review'")
        if "discovery_methods_json" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN discovery_methods_json TEXT DEFAULT '[]'")
        if "structure_hints_json" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN structure_hints_json TEXT DEFAULT '[]'")
        if "discovery_role" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN discovery_role VARCHAR(32) DEFAULT 'candidate'")
        if "seed_family" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN seed_family VARCHAR(64) DEFAULT 'other'")
        if "seed_packet_id" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN seed_packet_id VARCHAR(180)")
        if "seed_packet_title" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN seed_packet_title VARCHAR(300)")
        if "platform_family" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN platform_family VARCHAR(64) DEFAULT 'unknown'")
        if "source_family_tags_json" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN source_family_tags_json TEXT DEFAULT '[]'")
        if "scope_hints_json" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN scope_hints_json TEXT DEFAULT '{\"spatial\":[],\"language\":[],\"topic\":[]}'")
        if "last_discovery_outcome" not in memory_columns:
            statements.append("ALTER TABLE source_memories ADD COLUMN last_discovery_outcome TEXT")
    if "source_content_snapshots" in table_names:
        snapshot_columns = {column["name"] for column in inspector.get_columns("source_content_snapshots")}
        if "knowledge_node_id" not in snapshot_columns:
            statements.append("ALTER TABLE source_content_snapshots ADD COLUMN knowledge_node_id VARCHAR(180)")
        if "canonical_snapshot_id" not in snapshot_columns:
            statements.append("ALTER TABLE source_content_snapshots ADD COLUMN canonical_snapshot_id VARCHAR(180)")
        if "duplicate_class" not in snapshot_columns:
            statements.append("ALTER TABLE source_content_snapshots ADD COLUMN duplicate_class VARCHAR(64)")
        if "body_storage_mode" not in snapshot_columns:
            statements.append("ALTER TABLE source_content_snapshots ADD COLUMN body_storage_mode VARCHAR(32) DEFAULT 'full_text'")
    if "source_scheduler_ticks" in table_names:
        tick_columns = {column["name"] for column in inspector.get_columns("source_scheduler_ticks")}
        if "structure_scans_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN structure_scans_requested INTEGER DEFAULT 0")
        if "structure_scans_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN structure_scans_completed INTEGER DEFAULT 0")
        if "record_extract_jobs_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN record_extract_jobs_requested INTEGER DEFAULT 0")
        if "record_extract_jobs_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN record_extract_jobs_completed INTEGER DEFAULT 0")
        if "knowledge_backfill_jobs_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN knowledge_backfill_jobs_requested INTEGER DEFAULT 0")
        if "knowledge_backfill_jobs_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN knowledge_backfill_jobs_completed INTEGER DEFAULT 0")
        if "public_discovery_jobs_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN public_discovery_jobs_requested INTEGER DEFAULT 0")
        if "public_discovery_jobs_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN public_discovery_jobs_completed INTEGER DEFAULT 0")
        if "llm_tasks_requested" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN llm_tasks_requested INTEGER DEFAULT 0")
        if "llm_tasks_completed" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN llm_tasks_completed INTEGER DEFAULT 0")
        if "duplicate_snapshots_skipped" not in tick_columns:
            statements.append("ALTER TABLE source_scheduler_ticks ADD COLUMN duplicate_snapshots_skipped INTEGER DEFAULT 0")
    if "source_review_claim_candidates" in table_names:
        review_claim_columns = {column["name"] for column in inspector.get_columns("source_review_claim_candidates")}
        if "confidence_score" not in review_claim_columns:
            statements.append("ALTER TABLE source_review_claim_candidates ADD COLUMN confidence_score FLOAT DEFAULT 0.5")
        if "confidence_basis_json" not in review_claim_columns:
            statements.append("ALTER TABLE source_review_claim_candidates ADD COLUMN confidence_basis_json TEXT DEFAULT '[]'")
    if "source_discovery_jobs" in table_names:
        discovery_job_columns = {column["name"] for column in inspector.get_columns("source_discovery_jobs")}
        if "outcome_summary" not in discovery_job_columns:
            statements.append("ALTER TABLE source_discovery_jobs ADD COLUMN outcome_summary TEXT")
    if "source_media_artifacts" in table_names:
        media_artifact_columns = {column["name"] for column in inspector.get_columns("source_media_artifacts")}
        if "duplicate_cluster_id" not in media_artifact_columns:
            statements.append("ALTER TABLE source_media_artifacts ADD COLUMN duplicate_cluster_id VARCHAR(180)")
        if "sequence_id" not in media_artifact_columns:
            statements.append("ALTER TABLE source_media_artifacts ADD COLUMN sequence_id VARCHAR(180)")
        if "frame_index" not in media_artifact_columns:
            statements.append("ALTER TABLE source_media_artifacts ADD COLUMN frame_index INTEGER")
        if "sampled_at_ms" not in media_artifact_columns:
            statements.append("ALTER TABLE source_media_artifacts ADD COLUMN sampled_at_ms INTEGER")
    if "source_media_ocr_runs" in table_names:
        media_ocr_columns = {column["name"] for column in inspector.get_columns("source_media_ocr_runs")}
        if "attempt_index" not in media_ocr_columns:
            statements.append("ALTER TABLE source_media_ocr_runs ADD COLUMN attempt_index INTEGER DEFAULT 0")
        if "selected_result" not in media_ocr_columns:
            statements.append("ALTER TABLE source_media_ocr_runs ADD COLUMN selected_result BOOLEAN DEFAULT 0")
    if "source_media_interpretations" in table_names:
        media_interpret_columns = {column["name"] for column in inspector.get_columns("source_media_interpretations")}
        if "uncertainty_ceiling" not in media_interpret_columns:
            statements.append("ALTER TABLE source_media_interpretations ADD COLUMN uncertainty_ceiling FLOAT")
        if "place_basis" not in media_interpret_columns:
            statements.append("ALTER TABLE source_media_interpretations ADD COLUMN place_basis TEXT")
        if "time_of_day_basis" not in media_interpret_columns:
            statements.append("ALTER TABLE source_media_interpretations ADD COLUMN time_of_day_basis TEXT")
        if "season_basis" not in media_interpret_columns:
            statements.append("ALTER TABLE source_media_interpretations ADD COLUMN season_basis TEXT")
        if "geolocation_basis" not in media_interpret_columns:
            statements.append("ALTER TABLE source_media_interpretations ADD COLUMN geolocation_basis TEXT")
    if not statements:
        return
    if (
        "source_reputation_events" not in table_names
        and "source_memories" not in table_names
        and "source_content_snapshots" not in table_names
        and "source_scheduler_ticks" not in table_names
        and "source_review_claim_candidates" not in table_names
        and "source_media_artifacts" not in table_names
        and "source_media_ocr_runs" not in table_names
        and "source_media_interpretations" not in table_names
    ):
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(database_url), autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(database_url: str) -> Iterator[Session]:
    init_db(database_url)
    session = get_session_factory(database_url)()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
