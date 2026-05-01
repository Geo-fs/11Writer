from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.source_discovery.db import session_scope
from src.source_discovery.models import (
    SourceClaimOutcomeORM,
    SourceDiscoveryJobORM,
    SourceMemoryORM,
    SourceReputationEventORM,
    SourceWaveFitORM,
)
from src.types.source_discovery import (
    SourceDiscoveryCandidateSeed,
    SourceDiscoveryClaimOutcomeRequest,
    SourceDiscoveryClaimOutcomeResponse,
    SourceDiscoveryJobSummary,
    SourceDiscoveryMemory,
    SourceDiscoveryMemoryOverviewResponse,
    SourceDiscoverySeedUrlJobRequest,
    SourceDiscoverySeedUrlJobResponse,
    SourceDiscoveryWaveFit,
)


SOURCE_DISCOVERY_CAVEATS = [
    "Source reputation is learned from evidence over time; it is not proof that every future item is correct.",
    "Wave fit is separate from correctness: a source can be accurate but irrelevant to a specific wave.",
    "Discovered sources are not implemented or scheduled automatically.",
]

OUTCOME_SCORE_DELTAS = {
    "confirmed": 0.06,
    "contradicted": -0.10,
    "corrected": -0.03,
    "outdated": -0.02,
    "unresolved": 0.0,
    "not_applicable": 0.0,
}


class SourceDiscoveryService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def overview(self, *, limit: int = 100) -> SourceDiscoveryMemoryOverviewResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = list(
                session.scalars(
                    select(SourceMemoryORM)
                    .order_by(SourceMemoryORM.global_reputation_score.desc(), SourceMemoryORM.source_id)
                    .limit(limit)
                )
            )
            fits = list(
                session.scalars(
                    select(SourceWaveFitORM)
                    .order_by(SourceWaveFitORM.wave_id, SourceWaveFitORM.fit_score.desc())
                    .limit(limit * 3)
                )
            )
            jobs = list(
                session.scalars(
                    select(SourceDiscoveryJobORM)
                    .order_by(SourceDiscoveryJobORM.started_at.desc())
                    .limit(20)
                )
            )
            return SourceDiscoveryMemoryOverviewResponse(
                metadata={
                    "source": "source-discovery-memory",
                    "storageMode": "persistent-sqlite",
                    "reputationMode": "claim-outcome-v1",
                    "count": len(memories),
                },
                memories=[_serialize_memory(memory) for memory in memories],
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                recent_jobs=[_serialize_job(job) for job in jobs],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def upsert_candidate(self, seed: SourceDiscoveryCandidateSeed) -> SourceDiscoveryMemory:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = _upsert_candidate_row(session, seed, now=_utc_now())
            session.flush()
            return _serialize_memory(memory)

    def upsert_candidates(self, seeds: list[SourceDiscoveryCandidateSeed]) -> list[SourceDiscoveryMemory]:
        with session_scope(self._settings.source_discovery_database_url) as session:
            now = _utc_now()
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            session.flush()
            return [_serialize_memory(memory) for memory in memories]

    def record_claim_outcome(
        self,
        request: SourceDiscoveryClaimOutcomeRequest,
    ) -> SourceDiscoveryClaimOutcomeResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            now = _utc_now()
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                memory = _upsert_candidate_row(
                    session,
                    SourceDiscoveryCandidateSeed(
                        source_id=request.source_id,
                        title=request.source_id,
                        url="unknown",
                        parent_domain="unknown",
                        source_type="unknown",
                        source_class="unknown",
                        wave_id=request.wave_id,
                        lifecycle_state="discovered",
                        caveats=["Memory was created from a claim outcome before candidate metadata existed."],
                    ),
                    now=now,
                )

            observed_at = request.observed_at or now
            session.add(
                SourceClaimOutcomeORM(
                    source_id=request.source_id,
                    wave_id=request.wave_id,
                    claim_text=request.claim_text,
                    claim_type=request.claim_type,
                    outcome=request.outcome,
                    evidence_basis=request.evidence_basis,
                    observed_at=observed_at,
                    assessed_at=now,
                    corroborating_source_ids_json=json.dumps(request.corroborating_source_ids),
                    contradiction_source_ids_json=json.dumps(request.contradiction_source_ids),
                    caveats_json=json.dumps(request.caveats),
                )
            )
            _apply_claim_outcome(session, memory, request, now)
            fits = _fits_for_source(session, request.source_id)
            session.flush()
            return SourceDiscoveryClaimOutcomeResponse(
                memory=_serialize_memory(memory),
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_seed_url_job(self, request: SourceDiscoverySeedUrlJobRequest) -> SourceDiscoverySeedUrlJobResponse:
        now = _utc_now()
        parsed = urlparse(request.seed_url)
        job_id = f"source-discovery-job:{_safe_id(request.seed_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="seed_url",
                status="rejected",
                seed_url=request.seed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Seed URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(["Rejected before network access or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoverySeedUrlJobResponse(
                    job=_serialize_job(job),
                    memory=None,
                    wave_fits=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        classification = _classify_seed_url(request.seed_url)
        source_id = request.source_id or f"source:{_safe_id(parsed.netloc + parsed.path)[:120]}"
        title = request.title or parsed.netloc
        seed = SourceDiscoveryCandidateSeed(
            source_id=source_id,
            title=title,
            url=request.seed_url,
            parent_domain=parsed.netloc,
            source_type=classification["source_type"],
            source_class=classification["source_class"],  # type: ignore[arg-type]
            wave_id=request.wave_id,
            wave_title=request.wave_title,
            lifecycle_state="candidate",
            source_health="unknown",
            policy_state=classification["policy_state"],
            access_result=classification["access_result"],
            machine_readable_result=classification["machine_readable_result"],
            wave_fit_score=0.55 if request.wave_id else 0.5,
            relevance_basis=[
                request.discovery_reason,
                "Seed URL job created a candidate only; no automatic polling was enabled.",
            ],
            caveats=caveats + classification["caveats"],
        )
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = _upsert_candidate_row(session, seed, now=now)
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="seed_url",
                status="completed",
                seed_url=request.seed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([source_id]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps([
                    "Seed URL job is classification-only in this slice; no deep crawl or polling was run.",
                    "Candidate reputation remains thin until claim outcomes and source health accumulate.",
                ]),
            )
            session.add(job)
            session.flush()
            fits = _fits_for_source(session, source_id)
            return SourceDiscoverySeedUrlJobResponse(
                job=_serialize_job(job),
                memory=_serialize_memory(memory),
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )


def _upsert_candidate_row(
    session: Session,
    seed: SourceDiscoveryCandidateSeed,
    *,
    now: str,
) -> SourceMemoryORM:
    memory = session.get(SourceMemoryORM, seed.source_id)
    if memory is None:
        memory = SourceMemoryORM(
            source_id=seed.source_id,
            title=seed.title,
            url=seed.url,
            parent_domain=seed.parent_domain or _domain_from_url(seed.url),
            source_type=seed.source_type,
            source_class=seed.source_class,
            lifecycle_state=seed.lifecycle_state,
            source_health=seed.source_health,
            policy_state=seed.policy_state,
            access_result=seed.access_result,
            machine_readable_result=seed.machine_readable_result,
            first_seen_at=now,
            last_seen_at=now,
            caveats_json=json.dumps(seed.caveats),
            reputation_basis_json=json.dumps([
                "Initial reputation is thin until claim outcomes accumulate.",
            ]),
            known_aliases_json=json.dumps([]),
        )
        session.add(memory)
    else:
        memory.title = seed.title or memory.title
        memory.url = seed.url or memory.url
        memory.parent_domain = seed.parent_domain or memory.parent_domain
        memory.source_type = seed.source_type or memory.source_type
        memory.source_class = seed.source_class if seed.source_class != "unknown" else memory.source_class
        memory.lifecycle_state = seed.lifecycle_state or memory.lifecycle_state
        memory.source_health = seed.source_health or memory.source_health
        memory.policy_state = seed.policy_state or memory.policy_state
        memory.access_result = seed.access_result or memory.access_result
        memory.machine_readable_result = seed.machine_readable_result or memory.machine_readable_result
        memory.last_seen_at = now
        memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + seed.caveats)))

    if seed.wave_id:
        _upsert_wave_fit(session, seed, now=now)
    return memory


def _upsert_wave_fit(session: Session, seed: SourceDiscoveryCandidateSeed, *, now: str) -> None:
    fit = session.scalar(
        select(SourceWaveFitORM).where(
            SourceWaveFitORM.source_id == seed.source_id,
            SourceWaveFitORM.wave_id == seed.wave_id,
        )
    )
    if fit is None:
        fit = SourceWaveFitORM(
            source_id=seed.source_id,
            wave_id=seed.wave_id or "",
            wave_title=seed.wave_title or "",
            fit_score=seed.wave_fit_score,
            fit_state="candidate",
            relevance_basis_json=json.dumps(seed.relevance_basis),
            last_seen_at=now,
        )
        session.add(fit)
    else:
        fit.wave_title = seed.wave_title or fit.wave_title
        fit.fit_score = seed.wave_fit_score
        fit.relevance_basis_json = json.dumps(
            sorted(set(_loads_list(fit.relevance_basis_json) + seed.relevance_basis))
        )
        fit.last_seen_at = now


def _apply_claim_outcome(
    session: Session,
    memory: SourceMemoryORM,
    request: SourceDiscoveryClaimOutcomeRequest,
    now: str,
) -> None:
    before = memory.global_reputation_score
    delta = OUTCOME_SCORE_DELTAS[request.outcome]
    if request.outcome == "confirmed":
        memory.confirmed_claim_count += 1
    elif request.outcome == "contradicted":
        memory.contradicted_claim_count += 1
    elif request.outcome == "corrected":
        memory.corrected_claim_count += 1
        memory.correction_score = _clamp(memory.correction_score + 0.04)
    elif request.outcome == "outdated":
        memory.outdated_claim_count += 1
        memory.timeliness_score = _clamp(memory.timeliness_score - 0.03)
    elif request.outcome == "unresolved":
        memory.unresolved_claim_count += 1
    elif request.outcome == "not_applicable":
        memory.not_applicable_claim_count += 1
        if request.wave_id:
            _lower_wave_fit_for_not_applicable(session, request.source_id, request.wave_id, now)

    memory.global_reputation_score = _clamp(memory.global_reputation_score + delta)
    memory.domain_reputation_score = _clamp(memory.domain_reputation_score + delta)
    memory.confidence_level = _confidence_level(memory)
    memory.last_reputation_event_at = now
    basis = _loads_list(memory.reputation_basis_json)
    basis.append(f"{request.outcome}: {request.claim_text[:140]}")
    memory.reputation_basis_json = json.dumps(basis[-20:])
    session.add(
        SourceReputationEventORM(
            source_id=request.source_id,
            wave_id=request.wave_id,
            event_type="claim_outcome",
            outcome=request.outcome,
            score_before=before,
            score_after=memory.global_reputation_score,
            reason=request.claim_text[:500],
            created_at=now,
        )
    )


def _lower_wave_fit_for_not_applicable(session: Session, source_id: str, wave_id: str, now: str) -> None:
    fit = session.scalar(
        select(SourceWaveFitORM).where(
            SourceWaveFitORM.source_id == source_id,
            SourceWaveFitORM.wave_id == wave_id,
        )
    )
    if fit is None:
        return
    fit.fit_score = _clamp(fit.fit_score - 0.08)
    fit.fit_state = "low_fit" if fit.fit_score < 0.35 else fit.fit_state
    fit.last_seen_at = now


def _fits_for_source(session: Session, source_id: str) -> list[SourceWaveFitORM]:
    return list(
        session.scalars(
            select(SourceWaveFitORM)
            .where(SourceWaveFitORM.source_id == source_id)
            .order_by(SourceWaveFitORM.wave_id)
        )
    )


def _serialize_memory(memory: SourceMemoryORM) -> SourceDiscoveryMemory:
    return SourceDiscoveryMemory(
        source_id=memory.source_id,
        title=memory.title,
        url=memory.url,
        parent_domain=memory.parent_domain,
        source_type=memory.source_type,
        source_class=memory.source_class,  # type: ignore[arg-type]
        lifecycle_state=memory.lifecycle_state,
        source_health=memory.source_health,
        policy_state=memory.policy_state,
        access_result=memory.access_result,
        machine_readable_result=memory.machine_readable_result,
        global_reputation_score=memory.global_reputation_score,
        domain_reputation_score=memory.domain_reputation_score,
        source_health_score=memory.source_health_score,
        timeliness_score=memory.timeliness_score,
        correction_score=memory.correction_score,
        confidence_level=memory.confidence_level,
        claim_outcomes={
            "confirmed": memory.confirmed_claim_count,
            "contradicted": memory.contradicted_claim_count,
            "corrected": memory.corrected_claim_count,
            "outdated": memory.outdated_claim_count,
            "unresolved": memory.unresolved_claim_count,
            "notApplicable": memory.not_applicable_claim_count,
        },
        caveats=_loads_list(memory.caveats_json),
        reputation_basis=_loads_list(memory.reputation_basis_json),
        known_aliases=_loads_list(memory.known_aliases_json),
        first_seen_at=memory.first_seen_at,
        last_seen_at=memory.last_seen_at,
        last_reputation_event_at=memory.last_reputation_event_at,
    )


def _serialize_wave_fit(fit: SourceWaveFitORM) -> SourceDiscoveryWaveFit:
    return SourceDiscoveryWaveFit(
        source_id=fit.source_id,
        wave_id=fit.wave_id,
        wave_title=fit.wave_title,
        fit_score=fit.fit_score,
        fit_state=fit.fit_state,
        relevance_basis=_loads_list(fit.relevance_basis_json),
        last_seen_at=fit.last_seen_at,
    )


def _serialize_job(job: SourceDiscoveryJobORM) -> SourceDiscoveryJobSummary:
    return SourceDiscoveryJobSummary(
        job_id=job.job_id,
        job_type=job.job_type,
        status=job.status,
        seed_url=job.seed_url,
        wave_id=job.wave_id,
        wave_title=job.wave_title,
        discovered_source_ids=_loads_list(job.discovered_source_ids_json),
        rejected_reason=job.rejected_reason,
        request_budget=job.request_budget,
        used_requests=job.used_requests,
        started_at=job.started_at,
        finished_at=job.finished_at,
        caveats=_loads_list(job.caveats_json),
    )


def _classify_seed_url(url: str) -> dict[str, object]:
    lowered = url.lower()
    caveats = [
        "Classification is URL-shape based in this first slice; later jobs should fetch metadata within budget.",
    ]
    if any(token in lowered for token in ("/rss", "feed", ".xml", ".atom")):
        return {
            "source_type": "rss",
            "source_class": "live",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible feed candidate; parser validation still required."],
        }
    if any(token in lowered for token in (".json", ".geojson", ".csv", ".kml", ".netcdf", ".nc")):
        return {
            "source_type": "dataset",
            "source_class": "dataset",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible machine-readable dataset candidate; schema validation still required."],
        }
    if any(token in lowered for token in ("twitter.com", "x.com", "instagram.com", "facebook.com", "tiktok.com")):
        return {
            "source_type": "social",
            "source_class": "social_image",
            "access_result": "unknown",
            "machine_readable_result": "unknown",
            "policy_state": "manual_review",
            "caveats": caveats + [
                "Public social source must not be accessed through login-only, app-only, CAPTCHA, or ToS-hostile routes.",
                "Social/image evidence remains candidate evidence until corroborated.",
            ],
        }
    return {
        "source_type": "web",
        "source_class": "article",
        "access_result": "unknown",
        "machine_readable_result": "unknown",
        "policy_state": "manual_review",
        "caveats": caveats + ["Article/web candidate requires allowed full-text fetch before claim assessment."],
    }


def _confidence_level(memory: SourceMemoryORM) -> str:
    total = (
        memory.confirmed_claim_count
        + memory.contradicted_claim_count
        + memory.corrected_claim_count
        + memory.outdated_claim_count
        + memory.unresolved_claim_count
    )
    if total >= 25:
        return "mature"
    if total >= 8:
        return "developing"
    return "thin"


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or "unknown"


def _loads_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:20]


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "unknown"
