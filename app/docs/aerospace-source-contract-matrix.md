# Aerospace Source Contract Matrix

This matrix is scoped to aerospace / aircraft-satellite source slices only.
It documents the current backend contract surface, required caveats, and current validation status.
It does not change source semantics.

## NOAA AWC

- Route:
  `/api/aviation-weather/airport-context`
- Source category:
  airport-area aviation weather context
- Evidence basis:
  contextual
- Source health fields:
  none in the response body;
  runtime status is exposed separately through `/api/status/sources` as `noaa-awc`
- Source mode fields:
  none in the response body;
  runtime mode is reflected through source-status/runtime behavior
- Empty behavior:
  METAR or TAF may be absent without failing the route
- Primary observations/events:
  METAR and TAF airport-context records
- Export metadata key:
  `aviationWeatherContext`
- UI card currently exists:
  yes
- Smoke coverage status:
  metadata assertions added;
  latest local aerospace smoke attempt was blocked before assertions by a Windows Playwright `spawn EPERM` launcher failure
- Caveats:
  airport-area context only,
  read-only situational evidence,
  may not match exact airborne conditions at target position or altitude
- Do-not-infer rules:
  do not infer flight intent from METAR or TAF alone

## FAA NAS Airport Status

- Route:
  `/api/aerospace/airports/{airport_code}/faa-nas-status`
- Source category:
  airport operational/advisory status context
- Evidence basis:
  advisory / contextual
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.sourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `record.sourceMode`
  `sourceHealth.sourceMode`
- Empty behavior:
  no airport event becomes a normalized `normal` record, not a route failure
- Primary observations/events:
  airport status categories such as delay, ground delay, ground stop, advisory, normal
- Export metadata key:
  `faaNasAirportStatus`
- UI card currently exists:
  yes
- Smoke coverage status:
  metadata assertions added;
  latest local aerospace smoke attempt was blocked before assertions by a Windows Playwright `spawn EPERM` launcher failure
- Caveats:
  airport context only,
  advisory only,
  not flight-specific
- Do-not-infer rules:
  do not infer aircraft intent from airport status alone

## NASA/JPL CNEOS

- Route:
  `/api/aerospace/space/cneos-events`
- Source category:
  space-event context
- Evidence basis:
  source-reported / contextual
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.closeApproachSourceUrl`
  `sourceHealth.fireballSourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `sourceHealth.sourceMode`
- Empty behavior:
  empty close-approach and fireball lists are valid, not failures
- Primary observations/events:
  close-approach records and fireball records
- Export metadata key:
  `cneosSpaceContext`
- UI card currently exists:
  yes
- Smoke coverage status:
  metadata assertions added;
  latest local aerospace smoke attempt was blocked before assertions by a Windows Playwright `spawn EPERM` launcher failure
- Caveats:
  source-reported contextual records only,
  not impact prediction,
  not imminent-threat signaling
- Do-not-infer rules:
  do not infer impact risk, threat, or operational hazard from this summary alone

## NOAA SWPC

- Route:
  `/api/aerospace/space/swpc-context`
- Source category:
  space-weather advisory context
- Evidence basis:
  advisory / contextual
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.summarySourceUrl`
  `sourceHealth.alertsSourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `sourceHealth.sourceMode`
  per-record `sourceMode`
- Empty behavior:
  empty summaries and alerts are valid, not failures
- Primary observations/events:
  space-weather summaries, alerts, watches, warnings, advisories
- Export metadata key:
  `swpcSpaceWeatherContext`
- UI card currently exists:
  yes
- Smoke coverage status:
  metadata assertions added;
  latest local aerospace smoke attempt was blocked before assertions by a Windows Playwright `spawn EPERM` launcher failure
- Caveats:
  advisory/contextual only,
  not proof of actual system degradation
- Do-not-infer rules:
  do not claim satellite, GPS, or radio failure unless the source explicitly says so

## NOAA NCEI Space Weather Portal

- Route:
  `/api/aerospace/space/ncei-space-weather-archive`
- Source category:
  archival space-weather collection metadata
- Evidence basis:
  archival / contextual
- Official upstream endpoint:
  `https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.stp.swx:space_weather_products;view=xml;responseType=text/xml`
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.metadataSourceUrl`
  `sourceHealth.landingPageUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `sourceHealth.sourceMode`
  per-record `sourceMode`
- Empty behavior:
  empty `records` is valid and explicit, not a route failure
- Primary observations/events:
  archived collection metadata including collection id,
  dataset identifier,
  title,
  summary,
  temporal coverage,
  metadata update date,
  progress status,
  and update frequency
- Export metadata key:
  `nceiSpaceWeatherArchiveContext`
- UI card currently exists:
  yes;
  compact aerospace-local `Space Weather Archive Context` section
- Smoke coverage status:
  metadata/text assertions prepared in aerospace smoke;
  execution still depends on host Playwright launch health
- Caveats:
  archival/contextual only,
  separate from NOAA SWPC current advisories,
  not operational target-state truth
- Do-not-infer rules:
  do not infer current GPS, radio, aircraft, or satellite failure from archival metadata alone,
  do not treat NCEI archive metadata as a replacement for current NOAA SWPC advisory context

## OpenSky Anonymous States

- Route:
  `/api/aerospace/aircraft/opensky/states`
- Source category:
  optional anonymous aircraft state-vector context
- Evidence basis:
  source-reported / observed-context
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.sourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  per-record `sourceMode`
  `sourceHealth.sourceMode`
- Empty behavior:
  empty `states` is valid, not a failure
- Primary observations/events:
  current anonymous state vectors
- Export metadata key:
  `openskyAnonymousContext`
- UI card currently exists:
  yes
- Smoke coverage status:
  metadata assertions added;
  latest local aerospace smoke attempt was blocked before assertions by a Windows Playwright `spawn EPERM` launcher failure
- Caveats:
  anonymous access is rate-limited,
  current-state-vector only,
  optional,
  source-reported,
  not guaranteed complete,
  not authoritative,
  not a replacement for the main aircraft workflow
- Do-not-infer rules:
  do not claim complete traffic coverage,
  do not replace the primary aircraft source,
  do not infer flight intent from OpenSky comparison results

## USGS Geomagnetism

- Route:
  `/api/context/geomagnetism/usgs`
- Source category:
  observatory geomagnetic-field context
- Evidence basis:
  observed / contextual
- Source health fields:
  `sourceHealth.sourceId`
  `sourceHealth.sourceLabel`
  `sourceHealth.enabled`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.loadedCount`
  `sourceHealth.lastFetchedAt`
  `sourceHealth.sourceGeneratedAt`
  `sourceHealth.detail`
  `sourceHealth.errorSummary`
  `sourceHealth.caveat`
- Source mode fields:
  `metadata.sourceMode`
  `sourceHealth.sourceMode`
- Empty behavior:
  empty `samples` is valid and explicit, not a route failure
- Primary observations/events:
  bounded current-day observatory samples for requested geomagnetic elements
- Export metadata key:
  `geomagnetismContext`
- UI card currently exists:
  yes
- Smoke coverage status:
  metadata assertions are prepared in aerospace smoke;
  current local aerospace smoke execution remains blocked before assertions by a Windows Playwright `spawn EPERM` launcher failure
- Caveats:
  observatory context only,
  optional aerospace-adjacent context,
  not target-specific truth,
  not authoritative aircraft or satellite state
- Do-not-infer rules:
  do not infer GPS, radio, aircraft, or satellite failure from geomagnetic values alone,
  do not treat observatory samples as target-position truth

## Washington VAAC Advisories

- Route:
  `/api/aerospace/space/washington-vaac-advisories`
- Source category:
  volcanic-ash advisory context
- Evidence basis:
  advisory / contextual
- Official upstream endpoint family:
  listing page:
  `https://www.ospo.noaa.gov/products/atmosphere/vaac/messages.html`
  advisory XML documents linked from that page under:
  `https://www.ospo.noaa.gov/products/atmosphere/vaac/volcanoes/xml_files/FVXX*.xml`
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.listingSourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `sourceHealth.sourceMode`
  per-advisory `sourceMode`
- Empty behavior:
  explicit empty advisory list with non-fatal caveat when the listing exposes no current XML advisory links
- Primary observations/events:
  advisory number,
  issue time,
  observed/phenomenon time when available,
  volcano name/number,
  state or region,
  summit elevation when available,
  information source,
  eruption details,
  report status,
  motion fields when available,
  and upper flight-level text when exposed
- Export metadata key:
  combined aerospace consumer preserves this under `vaacContext`
- UI card currently exists:
  yes, inside the combined `Volcanic Ash Advisory Context` aerospace-local section
- Smoke coverage status:
  metadata/text assertions prepared through the combined `vaacContext` export path;
  execution still depends on host Playwright launch health
- Caveats:
  advisory/contextual only,
  no fake severity scale,
  no route-impact determination,
  no aircraft-exposure determination
- Do-not-infer rules:
  do not infer flight disruption, route impact, aircraft exposure, engine risk, threat, causation, or operational consequence from these advisories alone

## Anchorage VAAC Advisories

- Route:
  `/api/aerospace/space/anchorage-vaac-advisories`
- Source category:
  volcanic-ash advisory context
- Evidence basis:
  advisory / contextual
- Official upstream endpoint family:
  listing page:
  `https://www.weather.gov/vaac/`
  linked advisory text pages under:
  `https://forecast.weather.gov/product.php?site=CRH&issuedby=AK[1-5]&product=VAA&format=txt&version=1&glossary=1`
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.listingSourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `sourceHealth.sourceMode`
  per-advisory `sourceMode`
- Empty behavior:
  explicit empty advisory list is valid when the current linked header pages contain no recent advisories
- Primary observations/events:
  advisory number,
  issue time,
  observed-ash time when available,
  volcano name/number,
  area,
  source elevation text,
  eruption details,
  observed ash text,
  remarks,
  next-advisory text,
  and per-record source URL
- Export metadata key:
  combined aerospace consumer preserves this under `vaacContext`
- UI card currently exists:
  yes, inside the combined `Volcanic Ash Advisory Context` aerospace-local section
- Smoke coverage status:
  metadata/text assertions prepared through the combined `vaacContext` export path;
  execution still depends on host Playwright launch health
- Caveats:
  advisory/contextual only,
  header-page availability can be empty,
  no route-impact determination,
  no aircraft-exposure determination
- Do-not-infer rules:
  do not infer flight disruption, route impact, aircraft exposure, engine risk, threat, causation, or operational consequence from these advisories alone

## Tokyo VAAC Advisories

- Route:
  `/api/aerospace/space/tokyo-vaac-advisories`
- Source category:
  volcanic-ash advisory context
- Evidence basis:
  advisory / contextual
- Official upstream endpoint family:
  listing page:
  `https://www.data.jma.go.jp/vaac/data/vaac_list.html`
  linked advisory text pages under:
  `https://www.data.jma.go.jp/vaac/data/TextData/YYYY/*_Text.html`
- Source health fields:
  `sourceHealth.sourceName`
  `sourceHealth.sourceMode`
  `sourceHealth.health`
  `sourceHealth.detail`
  `sourceHealth.listingSourceUrl`
  `sourceHealth.lastUpdatedAt`
  `sourceHealth.state`
  `sourceHealth.caveats`
- Source mode fields:
  `sourceHealth.sourceMode`
  per-advisory `sourceMode`
- Empty behavior:
  explicit empty advisory list with non-fatal caveat when the current listing exposes no advisory text links
- Primary observations/events:
  advisory number,
  issue time,
  observed-ash time when available,
  volcano name/number,
  area,
  source elevation text,
  information source,
  eruption details,
  observed ash text,
  remarks,
  next-advisory text,
  and per-record source URL
- Export metadata key:
  combined aerospace consumer preserves this under `vaacContext`
- UI card currently exists:
  yes, inside the combined `Volcanic Ash Advisory Context` aerospace-local section
- Smoke coverage status:
  metadata/text assertions prepared through the combined `vaacContext` export path;
  execution still depends on host Playwright launch health
- Caveats:
  advisory/contextual only,
  text-page family is listed-page driven,
  no route-impact determination,
  no aircraft-exposure determination
- Do-not-infer rules:
  do not infer flight disruption, route impact, aircraft exposure, engine risk, threat, causation, or operational consequence from these advisories alone
