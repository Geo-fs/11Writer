# geoBoundaries Admin

Source:
- [geoBoundaries API docs](https://www.geoboundaries.org/api.html)
- bounded official slice used here:
  - [gbOpen BEL ADM1](https://www.geoboundaries.org/api/current/gbOpen/BEL/ADM1/)

Route:
- `GET /api/context/reference/geoboundaries-admin`

Current bounded scope:
- one release family only:
  - `gbOpen`
- one country only:
  - `BEL`
- one admin level only:
  - `ADM1`

Query params:
- `shape_iso`
- `bbox`
- `limit`

Response behavior:
- returns bounded Belgium ADM1 reference rows only
- preserves:
  - source id
  - source mode
  - source health
  - release family
  - country ISO
  - admin level
  - boundary id
  - boundary source
  - license and provenance links
  - simplified geometry provenance
  - representative bbox and center summaries

Normalized row fields:
- `record_id`
- `shape_name`
- `shape_iso`
- `shape_group`
- `shape_type`
- `geometry_type`
- `center_longitude`
- `center_latitude`
- `bbox_min_lon`
- `bbox_min_lat`
- `bbox_max_lon`
- `bbox_max_lat`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis=reference`

Fixture-first behavior:
- default mode is `fixture`
- deterministic fixture:
  - [geoboundaries_admin_bel_adm1_fixture.json](C:/Users/mike/11Writer/app/server/data/geoboundaries_admin_bel_adm1_fixture.json)
- live mode is backend-only and still stays pinned to the same `gbOpen/BEL/ADM1` endpoint family

Guardrails:
- reference only
- not legal-jurisdiction truth
- not operational-control truth
- not live incident truth
- not impact, certainty, responsibility, or action guidance
- bbox and center values are representative geometry summaries only

Reporting integration:
- participates in `base-earth-reference` in the backend environmental source-family overview
- flows into:
  - `GET /api/context/environmental/base-earth-export-package`
  - `GET /api/context/environmental/base-earth-review-queue`
  - `GET /api/context/environmental/fusion-snapshot-input`

Validation:
- `python -m pytest app/server/tests/test_geoboundaries_admin.py -q`
