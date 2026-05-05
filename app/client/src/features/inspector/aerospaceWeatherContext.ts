import type { AviationWeatherContextResponse, SourceStatus } from "../../types/api";

export interface AerospaceWeatherContextSummary {
  airportCode: string;
  airportName: string | null;
  source: string;
  sourceDetail: string;
  sourceHealthState: SourceStatus["state"] | "unavailable";
  metarAvailable: boolean;
  tafAvailable: boolean;
  metarReportedAt: string | null;
  tafIssuedAt: string | null;
  displayLines: string[];
  caveats: string[];
}

export function buildAerospaceWeatherContextSummary(input: {
  weather: AviationWeatherContextResponse | null | undefined;
  sourceHealth?: SourceStatus | null;
}): AerospaceWeatherContextSummary | null {
  if (!input.weather) {
    return null;
  }

  const metar = input.weather.metar;
  const taf = input.weather.taf;
  const metarCloudSummary = metar?.cloudLayers
    .slice(0, 2)
    .map((layer) => `${layer.cover}${layer.baseFtAgl != null ? ` ${layer.baseFtAgl} ft` : ""}`)
    .join(", ");
  const nextTafPeriod = taf?.forecastPeriods[0] ?? null;

  return {
    airportCode: input.weather.airportCode,
    airportName: input.weather.airportName ?? null,
    source: input.weather.source,
    sourceDetail: input.weather.sourceDetail,
    sourceHealthState: input.sourceHealth?.state ?? "unavailable",
    metarAvailable: metar != null,
    tafAvailable: taf != null,
    metarReportedAt: metar?.reportAt ?? metar?.observedAt ?? null,
    tafIssuedAt: taf?.issueTime ?? null,
    displayLines: [
      `Airport context: ${displayAirport(input.weather)}`,
      `Provider: ${input.weather.sourceDetail}`,
      metar
        ? `METAR: ${metar.flightCategory ?? "category unknown"} | vis ${metar.visibility ?? "unknown"} | wind ${displayWind(metar.windDirection, metar.windSpeedKt)}`
        : "METAR: unavailable for this airport context",
      metarCloudSummary ? `METAR clouds: ${metarCloudSummary}` : null,
      metar?.reportAt ? `METAR report: ${metar.reportAt}` : null,
      taf
        ? `TAF: ${taf.issueTime ? `issued ${taf.issueTime}` : "issue time unavailable"} | ${taf.forecastPeriods.length} forecast periods`
        : "TAF: unavailable for this airport context",
      nextTafPeriod
        ? `Next TAF period: ${displayTafPeriod(nextTafPeriod)}`
        : null,
      `Source health: ${input.sourceHealth?.state ?? "unavailable"}`
    ].filter((line): line is string => Boolean(line)),
    caveats: Array.from(
      new Set([
        "Airport-area weather context is read-only situational evidence and may not match conditions at the target's exact position or altitude.",
        "Do not infer flight intent from METAR or TAF alone.",
        ...(input.weather.caveats ?? []),
        ...(input.sourceHealth?.degradedReason ? [input.sourceHealth.degradedReason] : []),
      ])
    )
  };
}

export function buildAerospaceWeatherExportLines(
  summary: AerospaceWeatherContextSummary | null | undefined
): string[] {
  if (!summary) {
    return [];
  }
  return [
    `Aviation weather: ${displayAirport(summary)} | source=${summary.source}`,
    `Weather products: METAR ${summary.metarAvailable ? "available" : "unavailable"} | TAF ${summary.tafAvailable ? "available" : "unavailable"} | source health ${summary.sourceHealthState}`,
  ];
}

function displayAirport(
  summary: Pick<AerospaceWeatherContextSummary, "airportCode" | "airportName"> | AviationWeatherContextResponse
) {
  return summary.airportName ? `${summary.airportName} (${summary.airportCode})` : summary.airportCode;
}

function displayWind(direction: string | null | undefined, speedKt: number | null | undefined) {
  if (!direction && speedKt == null) {
    return "unknown";
  }
  if (!direction) {
    return `${speedKt ?? "unknown"} kt`;
  }
  if (speedKt == null) {
    return `${direction}`;
  }
  return `${direction} at ${speedKt} kt`;
}

function displayTafPeriod(
  period: NonNullable<AviationWeatherContextResponse["taf"]>["forecastPeriods"][number]
) {
  const pieces = [
    period.changeIndicator ?? "initial",
    period.validFrom ? `from ${period.validFrom}` : null,
    period.windDirection || period.windSpeedKt != null
      ? `wind ${displayWind(period.windDirection, period.windSpeedKt)}`
      : null,
    period.visibility ? `vis ${period.visibility}` : null,
    period.weather ? `wx ${period.weather}` : null
  ].filter((value): value is string => Boolean(value));
  return pieces.join(" | ");
}
