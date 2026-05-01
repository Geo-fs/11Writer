# UK EA Water Quality

Source:
- official Environment Agency linked-data API family used for this bounded slice:
  - `https://environment.data.gov.uk/data/bathing-water-quality/in-season/sample.json`
- bounded first slice: bathing-water in-season sample assessments only

Route:
- `GET /api/context/water-quality/uk-ea`

Params:
- `point_id`
- `sample_year`
- `district`
- `limit`
- `sort`

Normalized fields:
- `sample_id`
- `sampling_point_id`
- `sampling_point_label`
- `bathing_water_name`
- `district`
- `sample_date_time`
- `record_date`
- `sample_year`
- `sample_classification`
- `intestinal_enterococci_count`
- `e_coli_count`
- `source_url`
- `source_mode`
- `caveat`
- `evidence_basis`

Behavior:
- fixture-first
- live mode stays backend-only and bounded to the official bathing-water sample endpoint
- this slice preserves observed sample results only; it does not attempt broad Water Quality Explorer coverage
- sample time remains separate from fetch time

Evidence and caveats:
- bathing-water sample assessments are `observed`
- they are not continuous pollution alarms
- they do not by themselves establish area-wide contamination, health impact, or enforcement outcome
- source-provided free text is sanitized and remains inert source data only

Export metadata:
- source id, source URL, request URL, point/year/district filters, source mode, fetched time, raw count, count, and caveat
