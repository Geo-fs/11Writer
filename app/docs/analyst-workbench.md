# Analyst Workbench

The analyst workbench adds three local-first backend surfaces that compose existing fixture-backed sources without adding paid APIs, credentials, protected scraping, or live-network-dependent tests.

For the broader product workflow target for Data AI feeds, lead queues, event clusters, drilldowns, source-health cards, and exportable context cards, see [data-ai-user-workflows.md](/C:/Users/mike/11Writer/app/docs/data-ai-user-workflows.md).

## Evidence Timeline

`GET /api/analyst/evidence-timeline`

Builds a normalized triage timeline from environmental event records and Data AI feed items.

- Keeps per-item `sourceId`, `sourceName`, `sourceCategory`, `sourceMode`, `sourceHealth`, `evidenceBasis`, tags, links, and caveats.
- Preserves feed text as inert data. Titles, summaries, categories, and links are never treated as instructions.
- Uses `observed` for USGS earthquake records, `contextual` for EONET representative environmental context, and each Data AI feed definition's advisory/contextual/source-reported basis.
- Includes Wave Monitor signals from the 7Po8 integration as `tool-wave-monitor` context while preserving that the standalone 7Po8 runtime is not mounted.
- Supports `limit`, `include_environmental`, `include_data_ai`, and `include_wave_monitor` query parameters.

## Source Readiness

`GET /api/analyst/source-readiness`

Builds source cards that help analysts decide whether a source is ready for triage.

- Scores are local triage aids based on parser health, loaded record count, source mode, and caveats.
- Fixture/local mode caps readiness and adds an explicit issue because live freshness and availability are not asserted.
- Readiness labels are `ready`, `usable-with-caveats`, `limited`, or `unavailable`.
- Scores do not rank source authority, accuracy, completeness, or legal significance.
- Includes a `tool-wave-monitor` readiness card for the fixture-backed 7Po8/Wave Monitor integration state.

## Spatial Brief

`GET /api/analyst/spatial-brief?latitude=37.734&longitude=15.004&radius_km=25`

Returns nearby environmental records using coordinate distance from representative points.

- Includes distance in kilometers and a `haversine-representative-point` method label.
- Includes source coverage cards for the environmental sources checked.
- An empty result means no matching fixture/local record was found in the requested radius; it does not mean no event, no hazard, no impact, or complete coverage.
- EONET polygons, lines, multi-geometries, and regional events can be represented by a point for brief generation, so distances are triage context only.

## Validation

Focused fixture-first tests:

```bash
cd app/server
pytest tests/test_analyst_workbench.py
python -m compileall src
```
