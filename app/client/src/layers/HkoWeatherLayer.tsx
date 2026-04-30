import { useEffect } from "react";
import type { Viewer } from "cesium";

import { useHkoWeatherQuery } from "../lib/queries";
import { useAppStore } from "../lib/store";
import type { HkoTropicalCycloneContext, HkoWeatherWarningEvent } from "../types/api";
import type { HkoWeatherEntity } from "../types/entities";

interface HkoWeatherLayerProps {
  viewer: Viewer | null;
}

export function HkoWeatherLayer(props: HkoWeatherLayerProps) {
  void props.viewer;
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "hkoWeather")?.enabled ?? false;
  const setHkoWeatherEntities = useAppStore((state) => state.setHkoWeatherEntities);
  const hkoQuery = useHkoWeatherQuery(filters, enabled);

  useEffect(() => {
    if (!enabled) {
      setHkoWeatherEntities([]);
      return;
    }
    const metadataCaveat = hkoQuery.data?.metadata.caveat ?? null;
    const warnings = (hkoQuery.data?.warnings ?? []).map((item) => toWarningEntity(item, metadataCaveat ?? item.caveat));
    const cyclone = hkoQuery.data?.tropicalCyclone
      ? [toTropicalCycloneEntity(hkoQuery.data.tropicalCyclone, metadataCaveat ?? hkoQuery.data.tropicalCyclone.caveat)]
      : [];
    setHkoWeatherEntities([...warnings, ...cyclone]);
  }, [enabled, hkoQuery.data, setHkoWeatherEntities]);

  return null;
}

function toWarningEntity(event: HkoWeatherWarningEvent, caveat: string): HkoWeatherEntity {
  return {
    id: `hko:warning:${event.eventId}`,
    type: "environmental-event",
    eventSource: "hong-kong-observatory",
    entityKind: "warning",
    eventId: event.eventId,
    source: "hong-kong-observatory-open-weather",
    label: event.title,
    latitude: 0,
    longitude: 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.updatedAt ?? event.issuedAt ?? new Date().toISOString(),
    observedAt: event.issuedAt ?? null,
    fetchedAt: event.updatedAt ?? event.issuedAt ?? null,
    status: event.warningType,
    sourceDetail: "HKO weather warning",
    externalUrl: event.sourceUrl,
    confidence: null,
    historyAvailable: false,
    canonicalIds: { event_id: event.eventId },
    rawIdentifiers: {},
    quality: null,
    derivedFields: [],
    historySummary: null,
    linkTargets: [],
    metadata: {
      warningType: event.warningType,
      warningLevel: event.warningLevel,
      evidenceBasis: event.evidenceBasis,
      caveat,
    },
    warningType: event.warningType,
    warningLevel: event.warningLevel,
    summary: event.summary,
    issuedAt: event.issuedAt,
    updatedAt: event.updatedAt,
    expiresAt: event.expiresAt,
    affectedArea: event.affectedArea,
    signal: null,
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat,
  };
}

function toTropicalCycloneEntity(event: HkoTropicalCycloneContext, caveat: string): HkoWeatherEntity {
  return {
    id: `hko:tc:${event.eventId}`,
    type: "environmental-event",
    eventSource: "hong-kong-observatory",
    entityKind: "tropical-cyclone-context",
    eventId: event.eventId,
    source: "hong-kong-observatory-open-weather",
    label: event.title,
    latitude: 0,
    longitude: 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.updatedAt ?? event.issuedAt ?? new Date().toISOString(),
    observedAt: event.issuedAt ?? null,
    fetchedAt: event.updatedAt ?? event.issuedAt ?? null,
    status: event.signal ?? "tc-context",
    sourceDetail: "HKO tropical cyclone context",
    externalUrl: event.sourceUrl,
    confidence: null,
    historyAvailable: false,
    canonicalIds: { event_id: event.eventId },
    rawIdentifiers: {},
    quality: null,
    derivedFields: [],
    historySummary: null,
    linkTargets: [],
    metadata: {
      signal: event.signal,
      evidenceBasis: event.evidenceBasis,
      caveat,
    },
    warningType: "WTCSGNL",
    warningLevel: event.signal,
    summary: event.summary,
    issuedAt: event.issuedAt,
    updatedAt: event.updatedAt,
    expiresAt: null,
    affectedArea: "Hong Kong",
    signal: event.signal,
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat,
  };
}
