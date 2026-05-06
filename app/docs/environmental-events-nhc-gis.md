# NHC GIS Atlantic

This slice implements one bounded NOAA National Hurricane Center GIS follow-on over the official Atlantic GIS RSS feed.

Route:
- `GET /api/events/nhc-gis/recent`

Scope:
- Atlantic basin only
- fixture-first
- advisory/contextual tropical product-distribution records only
- source-provided storm-summary metadata and product links only

Supported params:
- `product_type`
  - `all`
  - `summary`
  - `atcf-xml`
  - `forecast`
  - `cone`
  - `watches-warnings`
  - `wind-field`
  - `wind-probabilities`
  - `outlook`
  - `best-track`
  - `surge`
  - `unknown`
- `storm_name`
- `limit`
- `sort`
  - `newest`
  - `product_type`

Normalized fields:
- `event_id`
- `title`
- `basin`
- `product_type`
- `storm_name`
- `storm_type`
- `wallet`
- `atcf_id`
- `advisory_number`
- `headline`
- `description`
- `published_at`
- `updated_at`
- `storm_center_text`
- `movement`
- `pressure`
- `geometry_summary`
- `latitude`
- `longitude`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Source posture:
- official provenance is preserved through feed and product URLs
- `source_health` is explicit
- `experimental_feed` stays visible in metadata
- source-provided storm-center coordinates remain representative advisory metadata only

Does not do:
- no HTML scraping fallback
- no frontend sweep
- no impact or damage claims
- no legal or responsibility claims
- no required-action claims
- no modeled-footprint or realized-hazard inference
- no basin-wide normalization into event truth beyond the bounded Atlantic advisory feed
