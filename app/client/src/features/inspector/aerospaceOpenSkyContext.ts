import type { AircraftEntity } from "../../types/entities";
import type { OpenSkyAircraftState, OpenSkyStatesResponse, SourceStatus } from "../../types/api";

export type OpenSkySelectedTargetMatchStatus =
  | "exact-icao"
  | "exact-callsign"
  | "possible-callsign"
  | "no-match"
  | "unavailable"
  | "ambiguous";

export interface OpenSkySelectedTargetComparison {
  matchStatus: OpenSkySelectedTargetMatchStatus;
  selectedTargetId: string | null;
  selectedCallsign: string | null;
  selectedIcao24: string | null;
  matchedOpenSkyIcao24: string | null;
  matchedOpenSkyCallsign: string | null;
  timeDifferenceSeconds: number | null;
  positionDifferenceKm: number | null;
  caveats: string[];
  evidenceBasis: "source-reported" | "contextual";
}

export interface AerospaceOpenSkyContextSummary {
  source: string;
  sourceMode: OpenSkyStatesResponse["sourceHealth"]["sourceMode"];
  sourceHealth: OpenSkyStatesResponse["sourceHealth"]["health"];
  sourceState: SourceStatus["state"] | "unavailable";
  aircraftCount: number;
  matchedState: OpenSkyAircraftState | null;
  selectedTargetComparison: OpenSkySelectedTargetComparison;
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceOpenSkyContextSummary(input: {
  response: OpenSkyStatesResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
  selectedAircraft: AircraftEntity | null;
}): AerospaceOpenSkyContextSummary | null {
  if (!input.response || !input.selectedAircraft) {
    return null;
  }

  const comparison = buildOpenSkySelectedTargetComparison({
    response: input.response,
    sourceHealth: input.sourceHealth,
    selectedAircraft: input.selectedAircraft
  });
  const matchedState =
    comparison.matchedOpenSkyIcao24 != null
      ? input.response.states.find((state) => state.icao24 === comparison.matchedOpenSkyIcao24) ?? null
      : null;

  return {
    source: input.response.source,
    sourceMode: input.response.sourceHealth.sourceMode,
    sourceHealth: input.response.sourceHealth.health,
    sourceState: input.sourceHealth?.state ?? "unavailable",
    aircraftCount: input.response.count,
    matchedState,
    selectedTargetComparison: comparison,
    displayLines: [
      `Source mode: ${input.response.sourceHealth.sourceMode}`,
      `Source health: ${input.sourceHealth?.state ?? input.response.sourceHealth.health}`,
      `Returned state vectors: ${input.response.count}`,
      `Comparison: ${displayMatchStatus(comparison.matchStatus)}`,
      matchedState
        ? `Matched selected aircraft: ${displayStateLabel(matchedState)}`
        : "Matched selected aircraft: no exact OpenSky state-vector match in this optional source window",
      matchedState?.lastContact ? `Last contact: ${matchedState.lastContact}` : null,
      comparison.timeDifferenceSeconds != null
        ? `Observation difference: ${comparison.timeDifferenceSeconds} seconds`
        : null,
      comparison.positionDifferenceKm != null
        ? `Position difference: ${comparison.positionDifferenceKm.toFixed(1)} km`
        : null,
      matchedState?.latitude != null && matchedState.longitude != null
        ? `Position: ${matchedState.latitude.toFixed(4)}, ${matchedState.longitude.toFixed(4)}`
        : matchedState
          ? "Position: unavailable in this source-reported state vector"
          : null
    ].filter((line): line is string => Boolean(line)),
    caveats: Array.from(
      new Set([
        "OpenSky anonymous state vectors are optional, rate-limited, and source-reported only.",
        "Coverage is not guaranteed to be complete or authoritative.",
        "This context does not replace the primary aircraft workflow.",
        ...comparison.caveats,
        ...input.response.caveats,
        ...(matchedState?.caveats ?? []),
      ])
    )
  };
}

export function buildAerospaceOpenSkyExportLines(
  summary: AerospaceOpenSkyContextSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }
  return [
    `OpenSky anonymous: ${summary.aircraftCount} state vectors | mode=${summary.sourceMode} | health=${summary.sourceState}`,
    `OpenSky comparison: ${displayMatchStatus(summary.selectedTargetComparison.matchStatus)}`,
    summary.matchedState
      ? `OpenSky match: ${displayStateLabel(summary.matchedState)} | last contact ${summary.matchedState.lastContact ?? "unknown"}`
      : "OpenSky match: no exact matching state vector for the selected aircraft in this optional source window",
  ];
}

export function buildOpenSkySelectedTargetComparison(input: {
  response: OpenSkyStatesResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
  selectedAircraft: AircraftEntity | null;
}): OpenSkySelectedTargetComparison {
  const selectedTargetId = input.selectedAircraft?.id ?? null;
  const selectedIcao24 = input.selectedAircraft?.canonicalIds.icao24?.trim().toLowerCase() ?? null;
  const selectedCallsign = normalizeCallsign(input.selectedAircraft?.callsign ?? null);

  if (!input.selectedAircraft) {
    return {
      matchStatus: "unavailable",
      selectedTargetId: null,
      selectedCallsign: null,
      selectedIcao24: null,
      matchedOpenSkyIcao24: null,
      matchedOpenSkyCallsign: null,
      timeDifferenceSeconds: null,
      positionDifferenceKm: null,
      caveats: ["No selected aircraft is available for OpenSky comparison."],
      evidenceBasis: "contextual"
    };
  }

  if (!input.response) {
    return {
      matchStatus: "unavailable",
      selectedTargetId,
      selectedCallsign,
      selectedIcao24,
      matchedOpenSkyIcao24: null,
      matchedOpenSkyCallsign: null,
      timeDifferenceSeconds: null,
      positionDifferenceKm: null,
      caveats: ["OpenSky anonymous comparison is unavailable because no source response is loaded."],
      evidenceBasis: "contextual"
    };
  }

  if (input.sourceHealth?.state === "degraded" || input.sourceHealth?.state === "rate-limited") {
    return {
      matchStatus: "unavailable",
      selectedTargetId,
      selectedCallsign,
      selectedIcao24,
      matchedOpenSkyIcao24: null,
      matchedOpenSkyCallsign: null,
      timeDifferenceSeconds: null,
      positionDifferenceKm: null,
      caveats: [
        "OpenSky anonymous comparison is unavailable because the optional source is degraded or rate-limited."
      ],
      evidenceBasis: "contextual"
    };
  }

  const exactIcaoMatch =
    selectedIcao24 != null
      ? input.response.states.find((state) => state.icao24 === selectedIcao24) ?? null
      : null;
  if (exactIcaoMatch) {
    return buildComparisonResult({
      matchStatus: "exact-icao",
      selectedAircraft: input.selectedAircraft,
      selectedCallsign,
      selectedIcao24,
      matchedState: exactIcaoMatch,
      caveats: [
        "OpenSky exact ICAO24 matches are still source-reported comparisons and do not replace the primary aircraft source."
      ]
    });
  }

  const callsignMatches =
    selectedCallsign != null
      ? input.response.states.filter(
          (state) => normalizeCallsign(state.callsign ?? null) === selectedCallsign
        )
      : [];
  if (callsignMatches.length > 1) {
    return {
      matchStatus: "ambiguous",
      selectedTargetId,
      selectedCallsign,
      selectedIcao24,
      matchedOpenSkyIcao24: null,
      matchedOpenSkyCallsign: selectedCallsign,
      timeDifferenceSeconds: null,
      positionDifferenceKm: null,
      caveats: [
        "Multiple OpenSky anonymous state vectors share the selected callsign, so the comparison remains ambiguous.",
        "Anonymous OpenSky callsign matches do not prove identity by themselves."
      ],
      evidenceBasis: "source-reported"
    };
  }
  if (callsignMatches.length === 1) {
    return buildComparisonResult({
      matchStatus: "exact-callsign",
      selectedAircraft: input.selectedAircraft,
      selectedCallsign,
      selectedIcao24,
      matchedState: callsignMatches[0],
      caveats: [
        "Callsign-only OpenSky matches are contextual and may not uniquely identify the selected aircraft."
      ]
    });
  }

  const possibleCallsignMatch =
    selectedCallsign != null
      ? input.response.states.find((state) => {
          const candidate = normalizeCallsign(state.callsign ?? null);
          return candidate != null && candidate.includes(selectedCallsign);
        }) ?? null
      : null;
  if (possibleCallsignMatch) {
    return buildComparisonResult({
      matchStatus: "possible-callsign",
      selectedAircraft: input.selectedAircraft,
      selectedCallsign,
      selectedIcao24,
      matchedState: possibleCallsignMatch,
      caveats: [
        "This is only a possible callsign match and does not confirm identity.",
        "No exact ICAO24 or exact callsign match was found in the optional OpenSky window."
      ]
    });
  }

  return {
    matchStatus: "no-match",
    selectedTargetId,
    selectedCallsign,
    selectedIcao24,
    matchedOpenSkyIcao24: null,
    matchedOpenSkyCallsign: null,
    timeDifferenceSeconds: null,
    positionDifferenceKm: null,
    caveats: [
      "No OpenSky anonymous match was found for the selected aircraft in the current optional source window.",
      "No match does not mean the aircraft is absent from the real world or from all traffic sources."
    ],
    evidenceBasis: "contextual"
  };
}

function displayStateLabel(state: OpenSkyAircraftState) {
  return state.callsign?.trim() || state.icao24.toUpperCase();
}

function displayMatchStatus(status: OpenSkySelectedTargetMatchStatus) {
  switch (status) {
    case "exact-icao":
      return "exact ICAO24 match";
    case "exact-callsign":
      return "exact callsign match";
    case "possible-callsign":
      return "possible callsign match";
    case "ambiguous":
      return "ambiguous callsign match";
    case "no-match":
      return "no match";
    case "unavailable":
      return "comparison unavailable";
  }
}

function normalizeCallsign(value: string | null | undefined) {
  const normalized = value?.trim().toUpperCase() ?? null;
  return normalized && normalized.length > 0 ? normalized : null;
}

function buildComparisonResult(input: {
  matchStatus: Exclude<OpenSkySelectedTargetMatchStatus, "ambiguous" | "no-match" | "unavailable">;
  selectedAircraft: AircraftEntity;
  selectedCallsign: string | null;
  selectedIcao24: string | null;
  matchedState: OpenSkyAircraftState;
  caveats: string[];
}): OpenSkySelectedTargetComparison {
  return {
    matchStatus: input.matchStatus,
    selectedTargetId: input.selectedAircraft.id,
    selectedCallsign: input.selectedCallsign,
    selectedIcao24: input.selectedIcao24,
    matchedOpenSkyIcao24: input.matchedState.icao24,
    matchedOpenSkyCallsign: normalizeCallsign(input.matchedState.callsign ?? null),
    timeDifferenceSeconds: computeTimeDifferenceSeconds(
      input.selectedAircraft.observedAt ?? input.selectedAircraft.timestamp,
      input.matchedState.lastContact ?? input.matchedState.timePosition ?? null
    ),
    positionDifferenceKm: computePositionDifferenceKm(input.selectedAircraft, input.matchedState),
    caveats: input.caveats,
    evidenceBasis: "source-reported"
  };
}

function computeTimeDifferenceSeconds(
  selectedTimestamp: string | null | undefined,
  openskyTimestamp: string | null
) {
  if (!selectedTimestamp || !openskyTimestamp) {
    return null;
  }
  const selectedMillis = Date.parse(selectedTimestamp);
  const openskyMillis = Date.parse(openskyTimestamp);
  if (Number.isNaN(selectedMillis) || Number.isNaN(openskyMillis)) {
    return null;
  }
  return Math.abs(Math.round((selectedMillis - openskyMillis) / 1000));
}

function computePositionDifferenceKm(
  selectedAircraft: AircraftEntity,
  matchedState: OpenSkyAircraftState
) {
  if (matchedState.latitude == null || matchedState.longitude == null) {
    return null;
  }
  return haversineKm(
    selectedAircraft.latitude,
    selectedAircraft.longitude,
    matchedState.latitude,
    matchedState.longitude
  );
}

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number) {
  const toRadians = (value: number) => (value * Math.PI) / 180;
  const earthRadiusKm = 6371;
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadiusKm * c;
}
