# BC Wildfire Datamart

This bounded geospatial slice exposes public BC Wildfire Service Datamart fire-weather context only.

Route:
- `GET /api/context/fire-weather/bcws`

Query params:
- `station_code`
- `fire_centre`
- `resource=all|stations|danger-summaries`
- `limit`

Official public source family:
- documentation: [BCWS Datamart and API reference PDF](https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prepare/bcws_datamart_and_api_v2_1.pdf)
- stations endpoint family: [wfwx-datamart stations](https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations)
- danger summary endpoint family: [wfwx-datamart danger summaries](https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/danger-summaries)

Normalized response shape:
- `stations`
  - fire-weather station reference rows
  - `evidence_basis=reference`
- `danger_summaries`
  - fire-centre danger-class summary rows
  - `evidence_basis=contextual`
- `source_health`
- `metadata`

Behavior:
- fixture-first by default
- live mode is backend-only and optional
- no frontend/browser direct dependency
- no fake coordinates are created
- free-form station and fire-centre text is sanitized and remains inert source data only

Caveats:
- this slice is fire-weather and danger-class context only
- it is not wildfire incident truth
- it is not perimeter truth
- it is not evacuation status
- it is not spread prediction
- it is not damage or impact evidence

Family overview participation:
- included in `weather-flood-hydrology`
- summarized conservatively with source mode, source health, evidence basis, and caveats preserved
