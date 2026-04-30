# Met Éireann Warnings

Source:
- Open data overview: [met.ie/about-us/specialised-services/open-data](https://www.met.ie/about-us/specialised-services/open-data)
- Warning feed description PDF: [Met Éireann Warning RSS/CAP/JSON Description](https://www.met.ie/Open_Data/Warnings/Met_Eireann_Warning_description_June2020.pdf)

Official endpoint/feed used:
- Current warning RSS feed: [warningsxml/rss.xml](https://www.met.ie/warningsxml/rss.xml)

Note on the older assignment pin:
- the older `https://www.met.ie/Open_Data/xml/warning_IRELAND.xml` pin did not resolve during inspection on April 30, 2026
- the current documented machine-readable warning feed in Met Éireann’s own warning-description PDF is `https://www.met.ie/warningsxml/rss.xml`
- this implementation uses the documented RSS feed plus linked CAP XML warning records

Route:
- `GET /api/events/met-eireann/warnings`

Query params:
- `level=all|green|yellow|orange|red|unknown`
- `limit`
- `sort=newest|level`

First slice:
- current warning RSS feed only
- linked CAP XML per warning item
- no forecast APIs
- no interactive-page scraping

Normalized output:
- `metadata`
  - `source`
  - `feed_name`
  - `feed_url`
  - `source_mode`
  - `fetched_at`
  - `count`
  - `caveat`
- `source_health`
- `warnings`
- `caveats`

Normalized warning fields:
- `event_id`
- `cap_id`
- `title`
- `warning_type`
- `level`
- `severity`
- `certainty`
- `urgency`
- `issued_at`
- `onset_at`
- `expires_at`
- `updated_at`
- `affected_area`
- `affected_codes`
- `description`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and reads the RSS feed plus linked CAP XML files
- tests do not depend on live network access

Evidence and caveats:
- warnings are advisory/contextual only
- title, level, severity, and text do not by themselves establish damage, flooding, travel disruption, or realized local conditions
- this slice intentionally excludes Met Éireann forecast APIs
- a currently empty live RSS feed is treated as an `empty` source-health state, not as a source failure

Related Ireland weather/reference context:
- [environmental-events-met-eireann-forecast.md](/C:/Users/mike/11Writer/app/docs/environmental-events-met-eireann-forecast.md)
- [environmental-events-ireland-wfd-catchments.md](/C:/Users/mike/11Writer/app/docs/environmental-events-ireland-wfd-catchments.md)
- warnings, forecasts, and WFD catchments are intentionally kept as separate advisory, forecast, and reference semantics

Validation:
- `python -m pytest app/server/tests/test_met_eireann_warnings.py -q`
- `python -m compileall app/server/src`
