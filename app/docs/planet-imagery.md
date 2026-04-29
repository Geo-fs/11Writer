# Planet Imagery

## Summary

The planet-view subsystem provides a 3D Cesium globe with a server-backed registry of globally coherent imagery modes. It is designed to keep imagery semantics honest:

- cloud-free composites are labeled as composites
- daily imagery is labeled as weather-affected
- seasonal views are labeled as seasonal composites
- optional Google photorealistic 3D tiles remain separate from imagery and are not required for the default globe experience

## Source Selection

The first imagery stack is built around free NASA products:

- NASA GIBS WMTS for global imagery delivery
- NASA Blue Marble / Blue Marble Next Generation for cloud-free default and seasonal composites
- NASA Black Marble for global night lights
- MODIS Terra corrected reflectance and snow products for analytical false-color and snow/ice modes

These sources were chosen because they are globally coherent, free to access, and explicit about whether they are composites or daily products.

## Mode Registry Contract

`/api/config/public` includes a `planet` section with:

- `defaultImageryModeId`
- `categories`
- `imageryModes`
- `terrain`

Each imagery mode includes:

- `id`
- `title`
- `category`
- `source`
- `sourceUrl`
- `shortDescription`
- `shortCaveat`
- `displayTags`
- `modeRole` (`default-basemap`, `optional-basemap`, `analysis-layer`)
- `sensorFamily` (`optical`, `radar`, `thematic`)
- `historicalFidelity` (`composite-reference`, `daily-approximate`, `multi-day-approximate`)
- `replayShortNote`
- `temporalNature`
- `cloudBehavior`
- `resolutionNotes`
- `licenseAccessNotes`
- `defaultReady`
- `analysisReady`
- `description`
- `interpretationCaveats`
- `providerType`
- provider construction fields such as `providerUrl`, `providerLayer`, `providerTileMatrixSetId`, `providerTimeStrategy`, and `providerTimeValue`

The client should use the registry rather than hardcoding imagery provider details.

For normal UI rendering:

- use `title` as the main label
- use `shortDescription` as the compact subtitle or summary line
- use `shortCaveat` anywhere the operator needs a one-line interpretation warning
- use `displayTags` for compact chips such as `Daily`, `Composite`, `Cloud-free`, or `Analysis-friendly`
- use `modeRole` to visually separate basemap-oriented modes from analysis layers
- use `sensorFamily` to clearly distinguish optical vs radar vs thematic products
- use `historicalFidelity` and `replayShortNote` anywhere replay/timeline context is shown
- keep `description`, `interpretationCaveats`, and `resolutionNotes` for expanded detail panels or docs

## Implemented Modes

| ID | Title | Source | Temporal nature | Cloud behavior | Default-ready | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `day-cloudless-default` | Cloudless Blue Marble | NASA Blue Marble | static-composite | cloud-free | yes | Default global beauty mode. Not live. |
| `day-daily-true-color` | Daily True Color | NASA GIBS / MODIS Terra | daily | weather-affected | no | Recent daily context with clouds and smoke still visible. |
| `night-lights` | Black Marble Night Lights | NASA Black Marble / VIIRS | static-composite | cloud-free | yes | Composite night-light context, not live electricity state. |
| `season-winter` | Winter Composite | NASA Blue Marble Next Generation | seasonal-composite | cloud-free | no | January proxy seasonal composite. |
| `season-spring` | Spring Composite | NASA Blue Marble Next Generation | seasonal-composite | cloud-free | no | April proxy seasonal composite. |
| `season-summer` | Summer Composite | NASA Blue Marble Next Generation | seasonal-composite | cloud-free | no | July proxy seasonal composite. |
| `season-fall` | Fall Composite | NASA Blue Marble Next Generation | seasonal-composite | cloud-free | no | October proxy seasonal composite. |
| `false-color-vegetation` | False Color Vegetation | NASA GIBS / MODIS Terra | daily | weather-affected | no | Bands 7-2-1 emphasize vegetation and surface contrast. |
| `snow-ice` | Snow and Ice Distinction | NASA GIBS / MODIS Terra | daily | weather-affected | no | Analytical snow-cover view, not photorealistic imagery. |
| `radar-sar-opera-rtc` | SAR Backscatter (OPERA RTC-S1) | NASA GIBS / OPERA RTC-S1 | multi-day | cloud-insensitive | no | False-color SAR backscatter analysis layer, not optical imagery. |

## What Users Are Seeing

- `day-cloudless-default`: a cloud-free Blue Marble composite for a stable and attractive whole-Earth basemap
- `day-daily-true-color`: recent daily satellite imagery with real cloud and weather limitations
- `night-lights`: a night-light composite intended for human settlement patterns and macro context
- `season-*`: seasonal proxy views based on Blue Marble monthly composites, not current-year seasonality
- `false-color-vegetation`: analytical false-color imagery for land-surface differentiation
- `snow-ice`: a thematic snow-cover layer for cryosphere and seasonal snow interpretation
- `radar-sar-opera-rtc`: false-color Sentinel-1 SAR backscatter where brightness represents radar response rather than optical reflectance

## SAR Evaluation

Evaluated free/open practical options:

- NASA GIBS `OPERA_L2_Radiometric_Terrain_Corrected_SAR_Sentinel-1`:
  - practical and integrated as `radar-sar-opera-rtc`
  - globally available browse product with analysis value
  - multi-day temporal behavior, not true live global coverage
- NASA GIBS `OPERA_L3_Dynamic_Surface_Water_Extent-Sentinel-1`:
  - radar-derived thematic water product
  - useful as a specialized hydrology analysis layer, but not a general SAR backscatter mode
  - left as a possible later addition to avoid picker clutter in the first SAR rollout

Chosen implementation:

- one global-style SAR analysis mode via OPERA RTC-S1 browse tiles
- categorized under `Radar / SAR`
- explicitly marked analysis-oriented, non-default, and non-photorealistic

## Runtime Behavior

- The Cesium viewer starts without a hardcoded imagery provider.
- Once public config loads, the client installs the default imagery mode from the registry.
- Changing imagery mode swaps only the imagery layer. The viewer is not recreated.
- Initial mode restore precedence is: permalink/view-state mode, then locally stored mode, then configured default mode.
- Restore is applied once during initial catalog bootstrap so periodic config refetch does not unexpectedly override an operator-selected mode.
- If a configured mode id is unknown, the client falls back to `day-cloudless-default`.
- If provider construction fails for a non-default mode, the client falls back to the default cloudless mode and surfaces a warning in the viewport status.
- If a provider repeatedly fails at runtime, the client surfaces a warning and falls back to the default mode when the failing mode is not already the default.

## Share and Snapshot State

Permalink/share state:

- imagery mode id is encoded in view-state as `imagery=<mode-id>`
- initial restore precedence is deterministic:
  - permalink imagery mode if valid
  - local stored imagery mode if valid
  - configured default imagery mode
  - first available mode only if the configured default is missing

Snapshot/export context:

- snapshot footer should include active imagery context fields:
  - mode id
  - mode title
  - source
  - `modeRole`
  - `sensorFamily`
  - `historicalFidelity`
  - short caveat
  - replay short note
- this keeps shared evidence exports interpretable without requiring external docs

## Replay and Timeline Contract

Replay/timeline consumers should treat tracked entities and imagery as separate truth domains:

- tracked data (aircraft, satellites, etc.) may be historical point-in-time observations
- imagery mode is contextual backdrop and is often composite or approximate, not same-time ground truth

Use the active imagery context fields to keep this explicit:

- `historicalFidelity=composite-reference`: backdrop is a reference composite; never interpret as same-time capture
- `historicalFidelity=daily-approximate`: backdrop is date-based but may not align to replay timestamp/timezone
- `historicalFidelity=multi-day-approximate`: backdrop aggregates or represents multi-day analysis context

The client exposes a narrow helper contract for cross-layer use:

- `buildActiveImageryContextFromHud(...)` for runtime-safe context reads
- `formatReplayImageryDisclosure(...)` for concise replay disclaimers in HUD/export surfaces
- `getImageryContextDisplay(...)` for normalized user-facing labels and safe display fields
- `getReplayImageryWarning(...)` for severity-scored replay interpretation warnings

Reusable UI components:

- `ImageryContextBadge` for compact HUD/topbar/runtime context
- `ImageryContextPanel` for expanded snapshot/export/inspector-style context blocks
- optional feature export path: `app/client/src/features/imagery`
  - `import { ImageryContextBadge, ImageryContextPanel } from "../features/imagery";`

Ownership boundary:

- geospatial/planet-imagery owns imagery semantics, caveats, and replay warning policy
- marine layers should consume these helpers/components and should not re-implement imagery caveat logic
- aerospace layers should consume these helpers/components and should not re-implement imagery caveat logic
- webcam layers should consume these helpers/components and should not re-implement imagery caveat logic
- reference layers should consume imagery context if needed but should not redefine imagery warning language
- downstream replay/entity layers own entity history correctness, not imagery semantics

## Downstream Integration Patterns

These are usage patterns for downstream agents; they are not claims that those domain surfaces already implemented these components.

Marine replay / vessel anomaly surfaces:

```tsx
import { buildActiveImageryContextFromHud, getReplayImageryWarning } from "../../lib/imageryContext";
import { ImageryContextBadge } from "../../features/imagery";

const imageryContext = buildActiveImageryContextFromHud(hud);
const replayWarning = getReplayImageryWarning(imageryContext);

<ImageryContextBadge context={imageryContext} isReplayContext={isReplayMode} />
{isReplayMode && replayWarning.shouldShowInReplay ? <small>{replayWarning.message}</small> : null}
```

Aerospace selected-target replay/history surfaces:

```tsx
import { buildActiveImageryContextFromHud, getImageryContextDisplay } from "../../lib/imageryContext";
import { ImageryContextPanel } from "../../features/imagery";

const imageryContext = buildActiveImageryContextFromHud(hud);
const imageryDisplay = getImageryContextDisplay(imageryContext);

<ImageryContextPanel context={imageryContext} isReplayContext={selectedReplayIndex != null} />
<small>{imageryDisplay.modeRoleLabel} | {imageryDisplay.sensorFamilyLabel}</small>
```

Snapshot/export previews:

```ts
const imageryContext = buildActiveImageryContextFromHud(hud);
const imageryDisplay = getImageryContextDisplay(imageryContext);
const replayWarning = getReplayImageryWarning(imageryContext);

// include in preview/export text:
// title, source, modeRoleLabel, sensorFamilyLabel, historicalFidelityLabel, replayShortNote, shortCaveat
// if replayWarning.shouldShowInReplay -> include replayWarning.title/message
```

Generic inspector/side-panel usage:

```tsx
import { ImageryContextPanel } from "../../features/imagery";

<ImageryContextPanel context={buildActiveImageryContextFromHud(hud)} isReplayContext={Boolean(isReplayContext)} />
```

When to use which API:

- Use `ImageryContextBadge` for dense runtime strips, HUD chips, and compact toolbars.
- Use `ImageryContextPanel` for expanded context blocks in side panels, inspectors, and export previews.
- Use `getImageryContextDisplay(context)` for normalized labels so every surface uses the same wording.
- Use `getReplayImageryWarning(context)` for replay caveat severity and message selection.

Recommended replay disclosure behavior:

- `resolutionSource` equivalent for imagery should be visual, not hidden
- show `title`, `source`, `modeRole`, `sensorFamily`, `shortCaveat`
- also show one replay line derived from `historicalFidelity + replayShortNote`
- never imply that replay overlays are temporally synchronized with composite/thematic/radar layers unless explicitly proven

Replay warning interpretation examples:

- `composite-reference` + optical basemap: `info` warning (reference backdrop, not same-time capture)
- `daily-approximate`: `info` warning (date-aligned context may still miss exact replay timestamp)
- `multi-day-approximate` or analysis-layer context: `warning` (stronger caution for precise temporal interpretation)
- `sensorFamily=radar`: `warning` (radar/backscatter interpretation, not optical ground truth)

## UI Guidance

- Group imagery modes by the registry category titles:
  - Base / Day
  - Night
  - Seasonal
  - Infrared / False Color
  - Analysis / Thematic
  - Analysis / Radar-SAR
- Show `title`, `temporalNature`, and `cloudBehavior` whenever a mode is selected.
- Show `shortDescription` directly in compact selectors or cards.
- Show `shortCaveat` in the HUD, inspector, or selector card so operators can see the main interpretation warning without opening docs.
- Show `displayTags` as compact chips or inline labels.
- For SAR/radar modes, always show an explicit "radar analysis" cue and do not present it as a photographic Earth view.
- In picker labels, explicitly mark `analysis-layer` entries so they cannot be confused with baseline Earth views.
- Prefer `day-cloudless-default` as the first-run globe experience.
- Offer `day-daily-true-color` and analysis modes as explicit opt-in modes, not the default.

Recommended operator workflow:

- runtime view: show active `title`, `source`, and `shortCaveat`
- runtime view: also show `modeRole` and `sensorFamily` in compact form
- runtime replay/timeline view: include `historicalFidelity` and `replayShortNote`
- runtime replay/timeline view: show `getReplayImageryWarning(...)` output when `isReplayContext` is true
- snapshot/export view: include `modeId`, `title`, `source`, `modeRole`, `sensorFamily`, `historicalFidelity`, `shortCaveat`, and `replayShortNote`
- imagery picker: show `title`, `shortDescription`, and `displayTags`
- expanded mode details: show `description`, `interpretationCaveats`, and `resolutionNotes`
- provenance/diagnostics surfaces: show `source`, `sourceUrl`, `licenseAccessNotes`, and provider fields

## Limitations

- Free global imagery does not provide a truly photorealistic, globally cloud-free, current live Earth at high resolution.
- Daily true-color and analytical daily layers can be cloudy, smoky, or delayed by acquisition cadence.
- Seasonal modes are proxies based on composites and should not be represented as current live season conditions.
- The platform does not currently ship a free global photorealistic 3D tiles dependency as a requirement for the imagery system.
- Free SAR as globally coherent browse imagery is feasible, but true globally current, high-resolution, low-latency SAR everywhere is not practical in this mode system without moving into specialized/on-demand workflows.
