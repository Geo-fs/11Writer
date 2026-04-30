# NASA POWER Meteorology Solar

Source:
- POWER temporal API docs: [power.larc.nasa.gov/docs/services/api/temporal/](https://power.larc.nasa.gov/docs/services/api/temporal/)
- POWER daily API docs: [power.larc.nasa.gov/docs/services/api/temporal/daily/](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)

Official endpoint used:
- Daily point query: [power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,ALLSKY_SFC_SW_DWN&community=RE&longitude=-6.2603&latitude=53.3498&start=20250101&end=20250103&format=JSON](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,ALLSKY_SFC_SW_DWN&community=RE&longitude=-6.2603&latitude=53.3498&start=20250101&end=20250103&format=JSON)

Route:
- `GET /api/context/weather/nasa-power`

Query params:
- `latitude`
- `longitude`
- `start`
- `end`
- `limit`

Bounded parameter set:
- `T2M`
- `ALLSKY_SFC_SW_DWN`

First slice:
- one point query only
- one temporal family only: daily point
- one small modeled/context parameter set only
- no bulk grids
- no broader POWER product expansion

Normalized output:
- `metadata`
  - `source`
  - `source_name`
  - `source_url`
  - `request_url`
  - `latitude`
  - `longitude`
  - `elevation_m`
  - `source_mode`
  - `fetched_at`
  - `time_standard`
  - `start_date`
  - `end_date`
  - `parameter_names`
  - `parameter_units`
  - `model_sources`
  - `count`
  - `caveat`
- `source_health`
- `samples`
- `caveats`

Normalized sample fields:
- `date`
- `air_temperature_c`
- `all_sky_surface_shortwave_downward_irradiance_kwh_m2_day`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and requests the official POWER daily point endpoint directly
- tests do not depend on live network access

Evidence and caveats:
- values are modeled/contextual only
- modeled time range is preserved separately from fetch time
- values are not observed local weather or incident truth
- do not infer energy impact, infrastructure impact, disruption, flooding, or damage from one modeled point query

Validation:
- `python -m pytest app/server/tests/test_nasa_power_meteorology_solar.py -q`
- `python -m compileall app/server/src`
