# 7Po8 Architecture (current)

## Local-first

7Po8 runs fully on the local machine:
- FastAPI backend on localhost
- React/Vite frontend on localhost
- SQLite persistence in local data path
- No required cloud infra, queues, or paid APIs

## Core entities

## Wave
- User-defined monitoring task (name, description, status, focus_type)
- Owns connectors, records, run history, signals, and discovered sources

## Connector
- Modular ingestion unit attached to a Wave
- Includes type, enabled flag, interval, strict type-specific config, and runtime state
- Current types:
  - `sample_news`
  - `rss_news`
  - `weather`

## Record
- Normalized collected result
- Stores source metadata, timestamps, optional geo fields, tags/raw payload, and dedupe key (`external_id`)

## RunHistory
- Persistent execution tracking per connector run
- Captures status, timings, errors, and records created

## Signal
- Deterministic user-facing alert derived from ingestion outcomes
- Includes severity, status lifecycle, summary, and dedupe cooldown key

## DiscoveredSource
- Candidate source discovered for a Wave
- Stores source classification, relevance, status lifecycle, connector suggestion, and metadata

## DomainTrustProfile
- Domain-level trust and approval policy configuration
- Controls whether discovered sources from a domain are blocked, manually reviewed, or auto-approved when stable
- Policy changes trigger deterministic re-evaluation of matching discovered sources

## SourceCheck
- Validation history row per discovered source
- Captures reachability, parseability, latency, content type, and status (`success`, `failed`, `skipped`)
- Feeds derived source-level reliability fields (`last_success_at`, `failure_count`, `stability_score`)

## Data flow

1. User creates a Wave and connectors in the UI.
2. Scheduler tick evaluates enabled connectors by interval eligibility.
3. Eligible connectors run through registry-dispatched runner logic.
4. New records are normalized, deduped, and persisted.
5. RunHistory entries and connector/wave runtime fields are updated.
6. Signal rules execute after each run.
7. UI reads wave details, connectors, records, run history, and signals.

## Discovery v1 flow

1. User triggers discovery for a Wave with optional seed URLs.
2. Discovery service derives candidates from:
   - seed URLs
   - Wave text/context URLs
   - existing connector/record source URLs
3. Seed pages are inspected for:
   - RSS/Atom links
   - JSON/API-like endpoints
   - PDF/document links
   - open-data style pages
4. Candidates are classified, scored, deduped, and stored as `DiscoveredSource`.
5. Source checks can be run manually per source or in batch for a wave.
6. Recent SourceCheck outcomes update stability scoring on the source.
7. Domain trust/policy evaluation can auto-approve, block, or mark sources for manual review.
8. Policy re-evaluation runs when domain trust changes, so backlog sources update immediately.
9. Approving an RSS source can auto-create an `rss_news` connector.

## Module boundaries

- `app/api`: route handlers and HTTP concerns
- `app/schemas`: request/response contracts
- `app/models`: SQLModel tables and relationships
- `app/services`: business logic and orchestration helpers
- `app/services/source_policy_service.py`: deterministic source-policy evaluation and re-evaluation
- `app/connectors`: connector interface + implementations + registry
- `app/scheduler`: polling eligibility and execution tick runner
- `app/db`: session/engine/init with Alembic-driven schema upgrade
- `alembic/`: migration environment and revision history
- `apps/frontend/src/api`: typed API client layer
- `apps/frontend/src/features/connectors`: registry-driven connector form architecture

## Current limits

- Migration source of truth is Alembic revision history
- CI drift detection validates Alembic head against SQLModel metadata, but it is still schema-only; it does not verify data migrations semantically
- Scheduler background loop is optional/manual; tick endpoint is primary control path
- Discovery is deterministic heuristic discovery, not broad autonomous crawling
- Discovery scope intentionally excludes social media and paid/private sources

## Recommended next extension

1. Add connector builders for discovered API/document sources.
2. Add per-wave discovery allowlist/blocklist controls.
3. Add richer domain/subdomain inheritance rules and per-wave trust overrides.
4. Add scheduled policy audits and policy-action history.
