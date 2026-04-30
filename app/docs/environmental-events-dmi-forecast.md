# DMI Forecast EDR Point Context

Source:
- DMI basics: [dmi.dk/friedata/dokumentation/basics](https://www.dmi.dk/friedata/dokumentation/basics)
- DMI Forecast Data EDR API: [dmi.dk/friedata/dokumentation/forecast-data-edr-api](https://www.dmi.dk/friedata/dokumentation/forecast-data-edr-api)

Official endpoint family and collection used:
- Forecast EDR API base: [opendataapi.dmi.dk/v1/forecastedr](https://opendataapi.dmi.dk/v1/forecastedr)
- Collection: `harmonie_dini_sf`
- Position query shape:
  [harmonie_dini_sf position example](https://opendataapi.dmi.dk/v1/forecastedr/collections/harmonie_dini_sf/position?coords=POINT(12.561%2055.715)&crs=crs84&parameter-name=temperature-0m)

Route:
- `GET /api/context/weather/dmi-forecast`

Query params:
- `latitude`
- `longitude`
- `limit`

First slice:
- one collection only: `harmonie_dini_sf`
- one point-query shape only: `position`
- one parameter only: `temperature-0m`

Normalized output:
- `metadata`
  - `source`
  - `source_name`
  - `source_url`
  - `request_url`
  - `collection`
  - `parameter_name`
  - `latitude`
  - `longitude`
  - `source_mode`
  - `fetched_at`
  - `first_forecast_time`
  - `last_forecast_time`
  - `count`
  - `caveat`
- `source_health`
- `samples`
- `caveats`

Normalized sample fields:
- `forecast_time`
- `air_temperature_c`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and requests one DMI CoverageJSON point response
- tests do not depend on live network access

Evidence and caveats:
- this slice is forecast context only
- forecast values are not observed weather
- fetched time is separate from forecast timestep time
- no local impact, damage, or realized-condition claims are inferred from the model output

Validation:
- `python -m pytest app/server/tests/test_dmi_forecast.py -q`
- `python -m compileall app/server/src`
