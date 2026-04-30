# Met Eireann Forecast

Source:
- Open data overview: [met.ie/about-us/specialised-services/open-data](https://www.met.ie/about-us/specialised-services/open-data)
- data.gov.ie forecast dataset page: [Met Eireann forecast API](https://data.gov.ie/en_GB/dataset/met-eireann-forecast-api/resource/5d156b15-38b8-4de9-921b-0ffc8704c88e)

Official endpoint used:
- Point forecast XML: [openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603](https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=53.3498;long=-6.2603)

Route:
- `GET /api/context/weather/met-eireann-forecast`

Query params:
- `latitude`
- `longitude`
- `limit`

First slice:
- one point-query shape only
- one endpoint family only
- no archive behavior
- no batching
- no observed-weather semantics

Normalized output:
- `metadata`
  - `source`
  - `source_name`
  - `source_url`
  - `request_url`
  - `latitude`
  - `longitude`
  - `source_mode`
  - `fetched_at`
  - `generated_at`
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
- `precipitation_mm`
- `wind_speed_mps`
- `wind_direction_deg`
- `symbol_code`
- `evidence_basis`

Fixture-first behavior:
- default mode is fixture
- live mode is backend-only and requests the point XML endpoint directly
- tests do not depend on live network access

Client helper coverage:
- `useMetEireannForecastQuery(...)`
- `useMetEireannWarningsQuery(...)`

Ireland weather-context bundle notes:
- Met Eireann warnings stay advisory/contextual and should be read separately from forecast model output
- Met Eireann forecast values stay forecast/context only and are not observed weather
- Ireland EPA WFD catchments remain reference/context only and are not a weather source
- these sources are intentionally discoverable together without being merged into one truth model

Evidence and caveats:
- forecast values are model context only
- forecast time is separate from fetch time
- forecast output does not by itself establish rain occurrence, flooding, travel disruption, damage, or realized local conditions
- warning records and forecast samples should not be merged into an impact claim

Validation:
- `python -m pytest app/server/tests/test_met_eireann_warnings.py app/server/tests/test_met_eireann_forecast.py -q`
- `python -m compileall app/server/src`
- `cmd /c npm.cmd run lint`
- `cmd /c npm.cmd run build`
