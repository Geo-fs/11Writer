# 7Po8 API (current)

Base URL: `http://127.0.0.1:8000`

## Health
- `GET /health`

## Waves
- `GET /api/waves`
- `POST /api/waves`
- `GET /api/waves/{wave_id}`
- `PATCH /api/waves/{wave_id}`
- `DELETE /api/waves/{wave_id}`

## Connectors
- `GET /api/waves/{wave_id}/connectors`
- `POST /api/waves/{wave_id}/connectors`
- `PATCH /api/connectors/{connector_id}`
- `DELETE /api/connectors/{connector_id}`

## Records and ingest
- `GET /api/waves/{wave_id}/records`
- `POST /api/waves/{wave_id}/ingest/sample`
  - records filters: `text_search`, `connector_id`, `source_type`, `start_date`, `end_date`, `has_coordinates`, `sort`

## Scheduler
- `POST /api/scheduler/tick`

## Run history
- `GET /api/waves/{wave_id}/runs`
- `GET /api/connectors/{connector_id}/runs`

## Signals
- `GET /api/waves/{wave_id}/signals`
- `GET /api/connectors/{connector_id}/signals`
- `PATCH /api/signals/{signal_id}`
  - signal filters: `severity`, `status`, `signal_type`, `start_date`, `end_date`, `sort`

## Source discovery
- `POST /api/waves/{wave_id}/discover-sources`
- `GET /api/waves/{wave_id}/discovered-sources`
- `POST /api/waves/{wave_id}/check-discovered-sources`
- `PATCH /api/discovered-sources/{source_id}`
- `POST /api/discovered-sources/{source_id}/approve`
- `POST /api/discovered-sources/{source_id}/check`
- `GET /api/discovered-sources/{source_id}/checks`
  - discovered source filters: `status`, `source_type`, `min_relevance_score`, `min_stability_score`, `parent_domain`, `approved_only`, `new_only`, `sort`
  - source check filters: `status`, `reachable`, `parseable`, `start_date`, `end_date`, `content_type`, `sort`

## Discovery request example

```json
{
  "seed_urls": [
    "https://city.example.gov/alerts",
    "https://agency.example.gov/open-data"
  ]
}
```
