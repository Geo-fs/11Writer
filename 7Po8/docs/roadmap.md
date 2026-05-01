# 7Po8 Roadmap

## Phase 1 (Complete)

- Local backend + frontend baseline
- Wave/Connector/Record data model
- Deterministic sample ingestion
- Core tests and lint/type gates

## Phase 2 (Mostly complete)

- Alembic migration setup
- Background scheduler worker loop
- Job execution logs and retry state
- Frontend controls for wave edit/delete
- Domain trust and approval policy controls
- Source discovery policy re-evaluation
- CI schema drift validation

## Phase 3

- Real source connector integrations:
  - public incident logs
  - permit/development feeds
- Historical backfill hooks
- Connector health and rate controls
- Connector generation from discovered API/document sources

## Phase 4

- Signal/anomaly model and detection tasks
- Export endpoints
- Smarter wave-level orchestration and adaptive polling
