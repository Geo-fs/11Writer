import type { AerospaceAirportStatusSummary } from "./aerospaceAirportStatusContext";
import type { AerospaceGeomagnetismContextSummary } from "./aerospaceGeomagnetismContext";
import type { AerospaceOperationalPresetId } from "../../lib/store";
import type { AerospaceReferenceContextSummary } from "./aerospaceReferenceContext";
import type { AerospaceSpaceContextSummary } from "./aerospaceSpaceContext";
import type { AerospaceSpaceWeatherArchiveContextSummary } from "./aerospaceSpaceWeatherArchiveContext";
import type { AerospaceSpaceWeatherContextSummary } from "./aerospaceSpaceWeatherContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";
import type { AerospaceVaacContextSummary } from "./aerospaceVaacContext";
import type { AerospaceWeatherContextSummary } from "./aerospaceWeatherContext";

export interface AerospaceOperationalContextSummary {
  presetId: AerospaceOperationalPresetId;
  presetLabel: string;
  emphasizedContextTypes: string[];
  isCustomPreset: boolean;
  presetCaveat: string;
  sourceCount: number;
  healthySourceCount: number;
  sourceModes: string[];
  availableContextTypes: string[];
  aviationWeatherAvailable: boolean;
  airportStatusAvailable: boolean;
  spaceEventsAvailable: boolean;
  spaceWeatherAvailable: boolean;
  spaceWeatherArchiveAvailable: boolean;
  geomagnetismAvailable: boolean;
  referenceContextAvailable: boolean;
  vaacAvailable: boolean;
  airportContextSummary: string | null;
  weatherSummary: string | null;
  referenceContextSummary: string | null;
  spaceContextSummary: string | null;
  spaceWeatherArchiveSummary: string | null;
  geomagnetismSummary: string | null;
  vaacSummary: string | null;
  healthSummary: string;
  caveats: string[];
  displayLines: string[];
  exportLines: string[];
  metadata: {
    presetId: AerospaceOperationalPresetId;
    presetLabel: string;
    emphasizedContextTypes: string[];
    presetCaveat: string;
    sourceCount: number;
    healthySourceCount: number;
    sourceModes: string[];
    availableContextTypes: string[];
    healthSummary: string;
    topSummaries: {
      aviationWeather: string | null;
      airportStatus: string | null;
      referenceContext: string | null;
      spaceEvents: string | null;
      spaceWeather: string | null;
      spaceWeatherArchive: string | null;
      geomagnetism: string | null;
      vaac: string | null;
    };
    caveats: string[];
  };
}

export interface AerospaceOperationalPresetDefinition {
  id: AerospaceOperationalPresetId;
  label: string;
  description: string;
  emphasizedContextTypes: string[];
  caveat: string;
}

export const AEROSPACE_OPERATIONAL_PRESETS: AerospaceOperationalPresetDefinition[] = [
  {
    id: "full-aerospace-context",
    label: "Full Aerospace Context",
    description: "Emphasizes airport, weather, space-event, space-weather, and target health context together.",
    emphasizedContextTypes: ["aviation-weather", "airport-status", "ourairports-reference", "space-events", "volcanic-ash-advisories", "space-weather", "space-weather-archive", "data-health"],
    caveat: "Full context combines multiple advisory/contextual sources and does not imply causation."
  },
  {
    id: "airport-operations-review",
    label: "Airport Operations Review",
    description: "Emphasizes airport operational status, aviation weather, and nearest-airport context.",
    emphasizedContextTypes: ["airport-status", "aviation-weather", "ourairports-reference", "airport-context", "data-health"],
    caveat: "Airport operations review does not explain selected-aircraft behavior by itself."
  },
  {
    id: "weather-review",
    label: "Weather Review",
    description: "Emphasizes aviation weather, space weather, and target data health.",
    emphasizedContextTypes: ["aviation-weather", "space-weather", "space-weather-archive", "geomagnetism-context", "data-health"],
    caveat: "Weather review does not prove operational impact or aircraft/satellite response."
  },
  {
    id: "space-context-review",
    label: "Space Context Review",
    description: "Emphasizes CNEOS and SWPC context with selected-target health.",
    emphasizedContextTypes: ["space-events", "volcanic-ash-advisories", "space-weather", "space-weather-archive", "geomagnetism-context", "data-health"],
    caveat: "Space context review does not imply target-specific danger, failure, or impact."
  },
  {
    id: "selected-target-evidence-review",
    label: "Selected-Target Evidence Review",
    description: "Emphasizes selected-target evidence basis and whichever contextual sources are already available.",
    emphasizedContextTypes: ["data-health", "aviation-weather", "airport-status", "ourairports-reference", "space-events", "volcanic-ash-advisories", "space-weather", "space-weather-archive"],
    caveat: "Selected-target evidence review is an analyst aid over already-loaded data only."
  }
];

export function buildAerospaceOperationalContextSummary(input: {
  presetId?: AerospaceOperationalPresetId;
  weatherSummary?: AerospaceWeatherContextSummary | null;
  airportStatusSummary?: AerospaceAirportStatusSummary | null;
  geomagnetismSummary?: AerospaceGeomagnetismContextSummary | null;
  referenceSummary?: AerospaceReferenceContextSummary | null;
  spaceContextSummary?: AerospaceSpaceContextSummary | null;
  spaceWeatherSummary?: AerospaceSpaceWeatherContextSummary | null;
  spaceWeatherArchiveSummary?: AerospaceSpaceWeatherArchiveContextSummary | null;
  vaacContextSummary?: AerospaceVaacContextSummary | null;
  dataHealthSummary?: AerospaceSourceHealthSummary | null;
}): AerospaceOperationalContextSummary | null {
  const weather = input.weatherSummary ?? null;
  const airportStatus = input.airportStatusSummary ?? null;
  const geomagnetism = input.geomagnetismSummary ?? null;
  const reference = input.referenceSummary ?? null;
  const spaceEvents = input.spaceContextSummary ?? null;
  const spaceWeather = input.spaceWeatherSummary ?? null;
  const spaceWeatherArchive = input.spaceWeatherArchiveSummary ?? null;
  const vaac = input.vaacContextSummary ?? null;
  const dataHealth = input.dataHealthSummary ?? null;

  const contexts = [
    weather ? { kind: "aviation-weather", mode: "contextual", healthy: weather.sourceHealthState === "healthy" } : null,
    airportStatus ? { kind: "airport-status", mode: airportStatus.sourceMode, healthy: airportStatus.sourceHealth === "normal" } : null,
    geomagnetism ? { kind: "geomagnetism-context", mode: geomagnetism.sourceMode, healthy: geomagnetism.sourceHealth === "loaded" } : null,
    reference ? { kind: "ourairports-reference", mode: reference.sourceMode, healthy: reference.airportMatchStatus === "exact-airport-code" || reference.airportMatchStatus === "airport-name-match" } : null,
    spaceEvents ? { kind: "space-events", mode: spaceEvents.sourceMode, healthy: spaceEvents.sourceHealth === "normal" } : null,
    spaceWeather ? { kind: "space-weather", mode: spaceWeather.sourceMode, healthy: spaceWeather.sourceHealth === "normal" } : null,
    spaceWeatherArchive ? { kind: "space-weather-archive", mode: spaceWeatherArchive.sourceMode, healthy: spaceWeatherArchive.sourceHealth === "normal" } : null,
    vaac ? { kind: "volcanic-ash-advisories", mode: vaac.sourceModes[0] ?? "unknown", healthy: vaac.healthySourceCount > 0 } : null,
  ].filter((value): value is { kind: string; mode: string; healthy: boolean } => Boolean(value));

  if (contexts.length === 0 && !dataHealth) {
    return null;
  }

  const preset =
    AEROSPACE_OPERATIONAL_PRESETS.find((item) => item.id === (input.presetId ?? "full-aerospace-context")) ??
    AEROSPACE_OPERATIONAL_PRESETS[0];

  const airportContextSummary =
    airportStatus != null
      ? `${displayAirport(airportStatus.airportCode, airportStatus.airportName)} | ${airportStatus.statusType}`
      : weather != null
        ? `${displayAirport(weather.airportCode, weather.airportName)} | airport weather context`
        : null;
  const weatherSummaryLine =
    weather != null
      ? `METAR ${weather.metarAvailable ? "available" : "unavailable"} | TAF ${weather.tafAvailable ? "available" : "unavailable"}`
      : null;
  const referenceSummaryLine =
    reference != null
      ? reference.comparisonLine.replace("Reference comparison: ", "")
      : null;
  const spaceContextSummaryLine =
    spaceEvents != null
      ? `${spaceEvents.closeApproachCount} close approaches | ${spaceEvents.fireballCount} fireballs`
      : spaceWeather != null
        ? `${spaceWeather.summaryCount} summaries | ${spaceWeather.alertCount} advisories`
        : null;
  const spaceWeatherArchiveSummaryLine =
    spaceWeatherArchive != null
      ? `${spaceWeatherArchive.title ?? "archive metadata"} | ${spaceWeatherArchive.temporalStart ?? "unknown start"} to ${spaceWeatherArchive.temporalEnd ?? "unknown end"}`
      : null;
  const geomagnetismSummaryLine =
    geomagnetism != null
      ? `${geomagnetism.observatoryId} | ${formatGeomagnetismInterval(geomagnetism.samplingPeriodSeconds)} | ${geomagnetism.sampleCount} samples`
      : null;
  const vaacSummaryLine =
    vaac != null
      ? `${vaac.availableSourceCount} sources with records | ${vaac.totalAdvisoryCount} advisories`
      : null;
  const topVaacAdvisory = vaac?.sources.find((source) => source.topAdvisory != null)?.topAdvisory ?? null;
  const healthSummary = dataHealth
    ? `${formatSourceKind(dataHealth.sourceKind)} | ${dataHealth.freshness} | ${dataHealth.health}`
    : "selected-target data health unavailable";

  const caveats = Array.from(
    new Set([
      "Aerospace Operational Context is a compact context composition only and does not imply aircraft/satellite behavior or causation.",
      "Weather, airport status, space events, and space weather remain separate contextual/advisory sources.",
      ...(dataHealth ? [buildDataHealthCaveat(dataHealth)] : []),
      ...weather?.caveats.slice(0, 1) ?? [],
      ...airportStatus?.caveats.slice(0, 1) ?? [],
      ...geomagnetism?.caveats.slice(0, 1) ?? [],
      ...reference?.caveats.slice(0, 1) ?? [],
      ...spaceEvents?.caveats.slice(0, 1) ?? [],
      ...spaceWeather?.caveats.slice(0, 1) ?? [],
      ...spaceWeatherArchive?.caveats.slice(0, 1) ?? [],
      ...vaac?.caveats.slice(0, 1) ?? [],
    ].filter((value): value is string => Boolean(value))
    )
  );

  const orderedDisplayLines = orderContextLines(
    [
      { kind: "meta", line: `Sources: ${contexts.length} available | ${contexts.filter((item) => item.healthy).length} healthy` },
      {
        kind: "meta",
        line: contexts.length > 0 ? `Source modes: ${Array.from(new Set(contexts.map((item) => item.mode))).join(", ")}` : "Source modes: unavailable"
      },
      { kind: "airport-context", line: airportContextSummary ? `Airport context: ${airportContextSummary}` : "Airport context: unavailable" },
      { kind: "aviation-weather", line: weatherSummaryLine ? `Weather: ${weatherSummaryLine}` : "Weather: unavailable" },
      {
        kind: "ourairports-reference",
        line: referenceSummaryLine ? `Reference baseline: ${referenceSummaryLine}` : "Reference baseline: unavailable"
      },
      { kind: "geomagnetism-context", line: geomagnetismSummaryLine ? `Geomagnetism: ${geomagnetismSummaryLine}` : "Geomagnetism: unavailable" },
      { kind: "space-events", line: spaceEvents != null ? `Space events: ${spaceContextSummaryLine ?? "unavailable"}` : "Space events: unavailable" },
      {
        kind: "space-weather-archive",
        line: spaceWeatherArchiveSummaryLine
          ? `Space-weather archive: ${spaceWeatherArchiveSummaryLine}`
          : "Space-weather archive: unavailable"
      },
      {
        kind: "volcanic-ash-advisories",
        line: vaacSummaryLine ? `Volcanic ash advisories: ${vaacSummaryLine}` : "Volcanic ash advisories: unavailable"
      },
      {
        kind: "space-weather",
        line: spaceWeather != null
          ? `Space weather: ${spaceWeather.topAlert?.headline ?? spaceWeather.topSummary?.headline ?? "available"}`
          : "Space weather: unavailable"
      },
      { kind: "data-health", line: `Selected target data: ${healthSummary}` },
    ],
    preset.emphasizedContextTypes
  );

  const displayLines = orderedDisplayLines;

  const exportLines = [
    `Operational preset: ${preset.label}`,
    `Operational context: ${contexts.length} sources | ${contexts.filter((item) => item.healthy).length} healthy`,
    airportContextSummary ? `Airport context: ${airportContextSummary}` : null,
    weatherSummaryLine ? `Weather context: ${weatherSummaryLine}` : null,
    referenceSummaryLine ? `Reference baseline: ${referenceSummaryLine}` : null,
    geomagnetismSummaryLine ? `Geomagnetism context: ${geomagnetismSummaryLine}` : null,
    spaceContextSummaryLine ? `Space context: ${spaceContextSummaryLine}` : null,
    spaceWeatherArchiveSummaryLine ? `Space-weather archive: ${spaceWeatherArchiveSummaryLine}` : null,
    vaacSummaryLine ? `VAAC context: ${vaacSummaryLine}` : null
  ].filter((value): value is string => Boolean(value)).slice(0, 4);

  return {
    presetId: preset.id,
    presetLabel: preset.label,
    emphasizedContextTypes: preset.emphasizedContextTypes,
    isCustomPreset: false,
    presetCaveat: preset.caveat,
    sourceCount: contexts.length,
    healthySourceCount: contexts.filter((item) => item.healthy).length,
    sourceModes: Array.from(new Set(contexts.map((item) => item.mode))),
    availableContextTypes: contexts.map((item) => item.kind),
    aviationWeatherAvailable: weather != null,
    airportStatusAvailable: airportStatus != null,
    geomagnetismAvailable: geomagnetism != null,
    referenceContextAvailable: reference != null,
    spaceEventsAvailable: spaceEvents != null,
    spaceWeatherAvailable: spaceWeather != null,
    spaceWeatherArchiveAvailable: spaceWeatherArchive != null,
    vaacAvailable: vaac != null,
    airportContextSummary,
    weatherSummary: weatherSummaryLine,
    referenceContextSummary: referenceSummaryLine,
    spaceContextSummary: spaceContextSummaryLine,
    spaceWeatherArchiveSummary: spaceWeatherArchiveSummaryLine,
    geomagnetismSummary: geomagnetismSummaryLine,
    vaacSummary: vaacSummaryLine,
    healthSummary,
    caveats,
    displayLines,
    exportLines,
    metadata: {
      presetId: preset.id,
      presetLabel: preset.label,
      emphasizedContextTypes: preset.emphasizedContextTypes,
      presetCaveat: preset.caveat,
      sourceCount: contexts.length,
      healthySourceCount: contexts.filter((item) => item.healthy).length,
      sourceModes: Array.from(new Set(contexts.map((item) => item.mode))),
      availableContextTypes: contexts.map((item) => item.kind),
      healthSummary,
      topSummaries: {
        aviationWeather: weatherSummaryLine,
        airportStatus: airportStatus ? `${airportStatus.statusType} | ${airportStatus.summary}` : null,
        referenceContext: referenceSummaryLine,
        geomagnetism: geomagnetismSummaryLine,
        spaceEvents: spaceEvents
          ? (spaceEvents.topCloseApproach
              ? `${spaceEvents.topCloseApproach.objectDesignation} | ${spaceEvents.topCloseApproach.closeApproachAt}`
              : spaceEvents.latestFireball
                ? `fireball | ${spaceEvents.latestFireball.eventTime}`
                : null)
          : null,
        spaceWeather: spaceWeather
          ? (spaceWeather.topAlert?.headline ?? spaceWeather.topSummary?.headline ?? null)
          : null,
        spaceWeatherArchive: spaceWeatherArchiveSummaryLine,
        vaac: topVaacAdvisory
          ? `${topVaacAdvisory.volcanoName} | ${topVaacAdvisory.issueTime ?? "issue time unavailable"}`
          : null,
      },
      caveats: caveats.slice(0, 4),
    },
  };
}

function formatGeomagnetismInterval(value: number | null) {
  if (value == null) {
    return "unknown interval";
  }
  if (value % 60 === 0) {
    return `${value / 60} min`;
  }
  return `${value} sec`;
}

function orderContextLines(
  lines: Array<{ kind: string; line: string }>,
  emphasizedKinds: string[]
) {
  return [...lines]
    .sort((left, right) => scoreKind(right.kind, emphasizedKinds) - scoreKind(left.kind, emphasizedKinds))
    .map((item) => item.line);
}

function scoreKind(kind: string, emphasizedKinds: string[]) {
  const index = emphasizedKinds.indexOf(kind);
  return index >= 0 ? emphasizedKinds.length - index : 0;
}

function displayAirport(code: string, name: string | null) {
  return name ? `${name} (${code})` : code;
}

function formatSourceKind(kind: AerospaceSourceHealthSummary["sourceKind"]) {
  switch (kind) {
    case "observed-live":
      return "observed live";
    case "observed-session":
      return "observed session";
    case "derived-propagated":
      return "derived propagated";
    case "contextual-reference":
      return "contextual reference";
    default:
      return "unavailable";
  }
}

function buildDataHealthCaveat(summary: AerospaceSourceHealthSummary) {
  if (summary.freshness === "stale" || summary.freshness === "unknown") {
    return `Selected-target data is ${summary.freshness}; interpret the combined context accordingly.`;
  }
  if (summary.evidenceBasis === "derived") {
    return "Selected-target satellite state remains derived/propagated, not observed live telemetry.";
  }
  if (summary.health === "partial" || summary.health === "degraded") {
    return "Selected-target data health is partial or degraded.";
  }
  return `Selected-target data is ${summary.evidenceBasis}.`;
}
