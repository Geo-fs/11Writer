import type { AircraftEntity } from "../../types/entities";
import type {
  OurAirportsAirportReferenceRecord,
  OurAirportsReferenceResponse,
  OurAirportsRunwayReferenceRecord,
  ReferenceNearbyItem,
  ReferenceObjectSummary,
  SourceStatus
} from "../../types/api";

export type AerospaceReferenceAirportMatchStatus =
  | "exact-airport-code"
  | "airport-name-match"
  | "no-match"
  | "not-applicable"
  | "unavailable";

export type AerospaceReferenceRunwayMatchStatus =
  | "runway-ident-match"
  | "no-runway-context"
  | "no-match"
  | "not-applicable"
  | "unavailable";

export interface AerospaceReferenceContextSummary {
  source: string;
  sourceMode: OurAirportsReferenceResponse["sourceHealth"]["sourceMode"];
  sourceHealth: OurAirportsReferenceResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  airportCount: number;
  runwayCount: number;
  selectedAirportCode: string | null;
  selectedAirportName: string | null;
  selectedRegionCode: string | null;
  selectedRunwayCode: string | null;
  airportMatchStatus: AerospaceReferenceAirportMatchStatus;
  runwayMatchStatus: AerospaceReferenceRunwayMatchStatus;
  matchedAirport: OurAirportsAirportReferenceRecord | null;
  matchedRunway: OurAirportsRunwayReferenceRecord | null;
  comparisonLine: string;
  displayLines: string[];
  exportLines: string[];
  caveats: string[];
  doesNotProve: string[];
}

export function buildAerospaceReferenceContextSummary(input: {
  response: OurAirportsReferenceResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
  selectedAircraft: AircraftEntity | null;
  primaryReference?: { summary: ReferenceObjectSummary } | null;
  nearestAirport?: ReferenceNearbyItem | null;
  nearestRunway?: ReferenceNearbyItem | null;
}): AerospaceReferenceContextSummary | null {
  if (!input.selectedAircraft) {
    return null;
  }

  const selectedAirportSummary = selectAirportSummary(input.primaryReference?.summary ?? null, input.nearestAirport ?? null);
  const selectedAirportCode = normalizeCode(selectedAirportSummary?.primaryCode ?? null);
  const selectedAirportName = normalizeName(selectedAirportSummary?.canonicalName ?? null);
  const selectedRegionCode = buildRegionCode(selectedAirportSummary ?? null);
  const selectedRunwayCode = normalizeCode(input.nearestRunway?.summary.primaryCode ?? null);
  const sourceState = input.sourceHealth?.state ?? "unavailable";
  const response = input.response ?? null;

  const unavailableCaveat =
    "OurAirports reference context is baseline facility metadata only and does not replace live selected-target evidence.";
  const noInferenceLines = [
    "Reference matches do not validate aircraft identity, route, flight intent, or operational state.",
    "Reference runways are baseline geometry only and do not prove runway availability or airport access."
  ];

  if (!selectedAirportCode && !selectedAirportName) {
    return {
      source: response?.source ?? "ourairports-reference",
      sourceMode: response?.sourceHealth.sourceMode ?? normalizeSourceMode(input.sourceHealth?.lastRunMode),
      sourceHealth: response?.sourceHealth.health ?? "unknown",
      sourceState,
      airportCount: response?.airportCount ?? 0,
      runwayCount: response?.runwayCount ?? 0,
      selectedAirportCode: null,
      selectedAirportName: null,
      selectedRegionCode,
      selectedRunwayCode,
      airportMatchStatus: "not-applicable",
      runwayMatchStatus: selectedRunwayCode ? "unavailable" : "not-applicable",
      matchedAirport: null,
      matchedRunway: null,
      comparisonLine: "Reference comparison: not applicable because no bounded airport reference input is available for the selected aircraft",
      displayLines: [
        "Reference basis: no bounded selected-airport code or name is currently available",
        `Source state: ${sourceState}`,
        "Comparison: not applicable"
      ],
      exportLines: [
        "OurAirports reference: not applicable for the selected aircraft",
        "Reference comparison: no bounded airport code or name was available from existing selected-target context"
      ],
      caveats: [unavailableCaveat, ...noInferenceLines],
      doesNotProve: noInferenceLines
    };
  }

  if (!response) {
    return {
      source: "ourairports-reference",
      sourceMode: normalizeSourceMode(input.sourceHealth?.lastRunMode),
      sourceHealth: "unknown",
      sourceState,
      airportCount: 0,
      runwayCount: 0,
      selectedAirportCode,
      selectedAirportName,
      selectedRegionCode,
      selectedRunwayCode,
      airportMatchStatus: "unavailable",
      runwayMatchStatus: selectedRunwayCode ? "unavailable" : "not-applicable",
      matchedAirport: null,
      matchedRunway: null,
      comparisonLine: "Reference comparison: unavailable because no OurAirports response is currently loaded",
      displayLines: [
        `Reference basis: ${displaySelectedAirport(selectedAirportCode, selectedAirportName)}`,
        `Source state: ${sourceState}`,
        "Comparison: unavailable"
      ],
      exportLines: [
        `OurAirports reference: unavailable | source state ${sourceState}`,
        `Reference basis: ${displaySelectedAirport(selectedAirportCode, selectedAirportName)}`
      ],
      caveats: [unavailableCaveat, ...noInferenceLines],
      doesNotProve: noInferenceLines
    };
  }

  const matchedAirport =
    findMatchedAirport(response.airports, selectedAirportCode, selectedAirportName, selectedRegionCode) ??
    response.airports[0] ??
    null;
  const airportMatchStatus = determineAirportMatchStatus(
    matchedAirport,
    selectedAirportCode,
    selectedAirportName,
    selectedRegionCode
  );
  const matchedRunway =
    matchedAirport && selectedRunwayCode
      ? findMatchedRunway(response.runways, matchedAirport.referenceId, selectedRunwayCode)
      : null;
  const runwayMatchStatus = determineRunwayMatchStatus(
    selectedRunwayCode,
    airportMatchStatus,
    matchedRunway,
    response.runwayCount
  );
  const comparisonLine = buildComparisonLine(airportMatchStatus, runwayMatchStatus);
  const displayLines = [
    `Reference basis: ${displaySelectedAirport(selectedAirportCode, selectedAirportName)}`,
    selectedRegionCode ? `Reference region filter: ${selectedRegionCode}` : null,
    `Source mode: ${response.sourceHealth.sourceMode}`,
    `Source health: ${input.sourceHealth?.state ?? response.sourceHealth.health}`,
    `Returned reference rows: ${response.airportCount} airports | ${response.runwayCount} runways`,
    comparisonLine,
    matchedAirport ? `Matched airport: ${displayAirportRecord(matchedAirport)}` : "Matched airport: none in current baseline window",
    matchedRunway ? `Matched runway: ${displayRunwayRecord(matchedRunway)}` : buildRunwayLine(runwayMatchStatus, selectedRunwayCode)
  ].filter((line): line is string => Boolean(line));
  const caveats = Array.from(
    new Set([
      unavailableCaveat,
      ...noInferenceLines,
      ...response.caveats,
      ...response.sourceHealth.caveats,
      ...(matchedAirport?.caveats ?? []),
      ...(matchedRunway?.caveats ?? [])
    ])
  ).slice(0, 6);

  return {
    source: response.source,
    sourceMode: response.sourceHealth.sourceMode,
    sourceHealth: response.sourceHealth.health,
    sourceState,
    airportCount: response.airportCount,
    runwayCount: response.runwayCount,
    selectedAirportCode,
    selectedAirportName,
    selectedRegionCode,
    selectedRunwayCode,
    airportMatchStatus,
    runwayMatchStatus,
    matchedAirport,
    matchedRunway,
    comparisonLine,
    displayLines,
    exportLines: [
      `OurAirports reference: ${response.airportCount} airports | ${response.runwayCount} runways | mode=${response.sourceHealth.sourceMode} | health=${input.sourceHealth?.state ?? response.sourceHealth.health}`,
      comparisonLine,
      matchedAirport ? `Reference airport: ${displayAirportRecord(matchedAirport)}` : "Reference airport: no baseline airport row matched the current selected-airport context"
    ],
    caveats,
    doesNotProve: noInferenceLines
  };
}

export function buildAerospaceReferenceExportLines(
  summary: AerospaceReferenceContextSummary | null | undefined
): string[] {
  return summary?.exportLines ?? [];
}

export function buildReferenceRegionCode(
  summary: ReferenceObjectSummary | null | undefined
): string | null {
  return buildRegionCode(summary ?? null);
}

function selectAirportSummary(
  primaryReference: ReferenceObjectSummary | null,
  nearestAirport: ReferenceNearbyItem | null
) {
  if (nearestAirport?.summary.objectType === "airport") {
    return nearestAirport.summary;
  }
  if (primaryReference?.objectType === "airport") {
    return primaryReference;
  }
  return null;
}

function findMatchedAirport(
  airports: OurAirportsAirportReferenceRecord[],
  selectedAirportCode: string | null,
  selectedAirportName: string | null,
  selectedRegionCode: string | null
) {
  if (selectedAirportCode) {
    const exact = airports.find((airport) => airportMatchesCode(airport, selectedAirportCode));
    if (exact) {
      return exact;
    }
  }
  if (selectedAirportName) {
    const byName = airports.find((airport) => {
      const sameName = normalizeName(airport.name) === selectedAirportName;
      if (!sameName) {
        return false;
      }
      return selectedRegionCode == null || normalizeCode(airport.regionCode) === selectedRegionCode;
    });
    if (byName) {
      return byName;
    }
  }
  return null;
}

function determineAirportMatchStatus(
  matchedAirport: OurAirportsAirportReferenceRecord | null,
  selectedAirportCode: string | null,
  selectedAirportName: string | null,
  selectedRegionCode: string | null
): AerospaceReferenceAirportMatchStatus {
  if (!selectedAirportCode && !selectedAirportName) {
    return "not-applicable";
  }
  if (!matchedAirport) {
    return "no-match";
  }
  if (selectedAirportCode && airportMatchesCode(matchedAirport, selectedAirportCode)) {
    return "exact-airport-code";
  }
  if (
    selectedAirportName &&
    normalizeName(matchedAirport.name) === selectedAirportName &&
    (selectedRegionCode == null || normalizeCode(matchedAirport.regionCode) === selectedRegionCode)
  ) {
    return "airport-name-match";
  }
  return "no-match";
}

function findMatchedRunway(
  runways: OurAirportsRunwayReferenceRecord[],
  airportReferenceId: string,
  selectedRunwayCode: string
) {
  return (
    runways.find(
      (runway) =>
        runway.airportRefId === airportReferenceId &&
        [normalizeCode(runway.leIdent), normalizeCode(runway.heIdent)].includes(selectedRunwayCode)
    ) ?? null
  );
}

function determineRunwayMatchStatus(
  selectedRunwayCode: string | null,
  airportMatchStatus: AerospaceReferenceAirportMatchStatus,
  matchedRunway: OurAirportsRunwayReferenceRecord | null,
  runwayCount: number
): AerospaceReferenceRunwayMatchStatus {
  if (!selectedRunwayCode) {
    return "no-runway-context";
  }
  if (airportMatchStatus === "not-applicable") {
    return "not-applicable";
  }
  if (airportMatchStatus === "unavailable") {
    return "unavailable";
  }
  if (matchedRunway) {
    return "runway-ident-match";
  }
  return runwayCount > 0 ? "no-match" : "unavailable";
}

function buildComparisonLine(
  airportMatchStatus: AerospaceReferenceAirportMatchStatus,
  runwayMatchStatus: AerospaceReferenceRunwayMatchStatus
) {
  return `Reference comparison: ${displayAirportMatchStatus(airportMatchStatus)} | ${displayRunwayMatchStatus(runwayMatchStatus)}`;
}

function buildRunwayLine(
  runwayMatchStatus: AerospaceReferenceRunwayMatchStatus,
  selectedRunwayCode: string | null
) {
  switch (runwayMatchStatus) {
    case "runway-ident-match":
      return null;
    case "no-runway-context":
      return "Matched runway: no bounded runway-threshold reference is currently available";
    case "unavailable":
      return selectedRunwayCode
        ? `Matched runway: unavailable for selected runway ${selectedRunwayCode}`
        : "Matched runway: unavailable";
    case "no-match":
      return selectedRunwayCode
        ? `Matched runway: no baseline runway ident match for ${selectedRunwayCode}`
        : "Matched runway: no baseline runway ident match";
    case "not-applicable":
    default:
      return "Matched runway: not applicable";
  }
}

function airportMatchesCode(
  airport: OurAirportsAirportReferenceRecord,
  selectedAirportCode: string
) {
  return [airport.airportCode, airport.iataCode, airport.localCode]
    .map((value) => normalizeCode(value))
    .includes(selectedAirportCode);
}

function displayAirportMatchStatus(status: AerospaceReferenceAirportMatchStatus) {
  switch (status) {
    case "exact-airport-code":
      return "exact airport-code match";
    case "airport-name-match":
      return "airport-name match";
    case "no-match":
      return "no baseline airport match";
    case "not-applicable":
      return "not applicable";
    case "unavailable":
    default:
      return "unavailable";
  }
}

function displayRunwayMatchStatus(status: AerospaceReferenceRunwayMatchStatus) {
  switch (status) {
    case "runway-ident-match":
      return "runway ident match";
    case "no-runway-context":
      return "no runway reference input";
    case "no-match":
      return "no runway ident match";
    case "not-applicable":
      return "not applicable";
    case "unavailable":
    default:
      return "unavailable";
  }
}

function displaySelectedAirport(code: string | null, name: string | null) {
  if (code && name) {
    return `${name} (${code})`;
  }
  return name ?? code ?? "unknown airport";
}

function displayAirportRecord(airport: OurAirportsAirportReferenceRecord) {
  const code = normalizeCode(airport.airportCode) ?? normalizeCode(airport.iataCode) ?? normalizeCode(airport.localCode);
  return code ? `${airport.name} (${code})` : airport.name;
}

function displayRunwayRecord(runway: OurAirportsRunwayReferenceRecord) {
  const idents = [runway.leIdent, runway.heIdent].filter((value): value is string => Boolean(value)).join("/");
  const length = runway.lengthFt != null ? ` | ${Math.round(runway.lengthFt).toLocaleString()} ft` : "";
  return `${idents || runway.referenceId}${length}`;
}

function buildRegionCode(summary: ReferenceObjectSummary | null) {
  if (!summary) {
    return null;
  }
  const admin1 = normalizeCode(summary.admin1Code);
  if (!admin1) {
    return null;
  }
  if (admin1.includes("-")) {
    return admin1;
  }
  const country = normalizeCode(summary.countryCode);
  return country ? `${country}-${admin1}` : admin1;
}

function normalizeCode(value: string | null | undefined) {
  const normalized = value?.trim().toUpperCase() ?? null;
  return normalized && normalized.length > 0 ? normalized : null;
}

function normalizeName(value: string | null | undefined) {
  const normalized = value?.trim().toUpperCase() ?? null;
  return normalized && normalized.length > 0 ? normalized : null;
}

function normalizeSourceMode(value: string | null | undefined): "fixture" | "live" | "unknown" {
  return value === "fixture" || value === "live" ? value : "unknown";
}
