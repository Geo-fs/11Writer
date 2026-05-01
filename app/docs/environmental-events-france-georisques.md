# France Georisques

Source:
- official API service family: `https://www.georisques.gouv.fr/api/v1/zonage_sismique`
- bounded first slice: commune seismic-zoning reference context only

Route:
- `GET /api/context/risk/france-georisques`

Params:
- `code_insee`
- or `latitude` and `longitude`
- `limit`

Normalized fields:
- `territory_id`
- `territory_name`
- `risk_type`
- `risk_level_code`
- `risk_level_label`
- `request_basis`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Behavior:
- fixture-first
- live mode stays on Géorisques `api/v1` only because current `api/v2` requires a token
- preserves request basis and request URL in metadata for export consumers
- empty lookups remain valid empty context, not fabricated failures

Evidence and caveats:
- seismic zoning is `reference` / `contextual`
- this slice does not claim a live earthquake, parcel-scale hazard, building safety, or realized damage
- commune zoning labels must not be promoted into incident truth

Export metadata:
- source id, source URL, request URL, request basis, territory id or lat/lon, source mode, fetched time, count, and caveat
