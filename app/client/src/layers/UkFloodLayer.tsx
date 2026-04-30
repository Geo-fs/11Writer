import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useUkEaFloodMonitoringQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { UkEaFloodEvent, UkEaFloodStation } from "../types/api";
import type { UkEaFloodEntity } from "../types/entities";

interface UkFloodLayerProps {
  viewer: Viewer | null;
}

export function UkFloodLayer({ viewer }: UkFloodLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "ukFloods")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setUkFloodEntities = useAppStore((state) => state.setUkFloodEntities);
  const floodQuery = useUkEaFloodMonitoringQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("uk-flood-monitoring");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setUkFloodEntities([]);
      return;
    }

    const events = floodQuery.data?.events ?? [];
    const stations = floodQuery.data?.stations ?? [];
    const metadataCaveat = floodQuery.data?.metadata.caveat ?? null;
    const mapped = [
      ...events.map((event) => toUkFloodAlertEntity(event, metadataCaveat ?? event.caveat)),
      ...stations.map((station) => toUkFloodStationEntity(station, metadataCaveat ?? station.caveat)),
    ];
    for (const event of events) {
      if (event.longitude != null && event.latitude != null) {
        collection.add(buildUkFloodAlertMarker(event, labelsEnabled));
      }
    }
    for (const station of stations) {
      if (station.longitude != null && station.latitude != null) {
        collection.add(buildUkFloodStationMarker(station, labelsEnabled));
      }
    }
    setUkFloodEntities(mapped);
  }, [enabled, floodQuery.data, labelsEnabled, setUkFloodEntities, viewer]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("ukflood:")) return;
      const [kind, itemId] = selected.id.replace("ukflood:", "").split(":", 2);
      if (kind === "alert") {
        const event = floodQuery.data?.events.find((item) => item.eventId === itemId);
        if (event) {
          setSelectedEntity(toUkFloodAlertEntity(event, floodQuery.data?.metadata.caveat ?? event.caveat));
        }
      } else if (kind === "station") {
        const station = floodQuery.data?.stations.find((item) => item.stationId === itemId);
        if (station) {
          setSelectedEntity(toUkFloodStationEntity(station, floodQuery.data?.metadata.caveat ?? station.caveat));
        }
      }
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [floodQuery.data, setSelectedEntity, viewer]);

  useEffect(() => {
    return () => {
      if (viewer && !viewer.isDestroyed() && dataSourceRef.current) {
        void viewer.dataSources.remove(dataSourceRef.current, true);
      }
      dataSourceRef.current = null;
    };
  }, [viewer]);

  return null;
}

function buildUkFloodAlertMarker(event: UkEaFloodEvent, labelsEnabled: boolean) {
  const color =
    event.severity === "severe-warning"
      ? Color.DARKRED
      : event.severity === "warning"
        ? Color.RED
        : event.severity === "alert"
          ? Color.GOLD
          : Color.LIGHTGRAY;
  return new Entity({
    id: `ukflood:alert:${event.eventId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude ?? 0, event.latitude ?? 0, 0),
    point: {
      pixelSize: 9,
      color,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5
    },
    label: labelsEnabled
      ? {
          text: `Flood ${event.severity}`,
          font: "11px sans-serif",
          fillColor: Color.WHITE,
          outlineColor: Color.BLACK,
          outlineWidth: 2,
          style: LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: VerticalOrigin.BOTTOM,
          pixelOffset: new Cartesian2(0, -14)
        }
      : undefined
  });
}

function buildUkFloodStationMarker(station: UkEaFloodStation, labelsEnabled: boolean) {
  const color =
    station.parameter === "level"
      ? Color.DEEPSKYBLUE
      : station.parameter === "flow"
        ? Color.LIMEGREEN
        : Color.CYAN;
  return new Entity({
    id: `ukflood:station:${station.stationId}`,
    name: station.stationLabel,
    position: Cartesian3.fromDegrees(station.longitude ?? 0, station.latitude ?? 0, 0),
    point: {
      pixelSize: 7,
      color,
      outlineColor: Color.BLACK.withAlpha(0.65),
      outlineWidth: 1.2
    },
    label: labelsEnabled
      ? {
          text: `${station.parameter} ${station.value ?? "n/a"}${station.unit ?? ""}`,
          font: "11px sans-serif",
          fillColor: Color.WHITE,
          outlineColor: Color.BLACK,
          outlineWidth: 2,
          style: LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: VerticalOrigin.BOTTOM,
          pixelOffset: new Cartesian2(0, -14)
        }
      : undefined
  });
}

function toUkFloodAlertEntity(event: UkEaFloodEvent, caveat: string): UkEaFloodEntity {
  return {
    id: `ukflood:alert:${event.eventId}`,
    type: "environmental-event",
    eventSource: "uk-ea-flood-monitoring",
    entityKind: "alert",
    eventId: event.eventId,
    source: "uk-environment-agency-flood-monitoring",
    label: event.title,
    latitude: event.latitude ?? 0,
    longitude: event.longitude ?? 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.issuedAt ?? event.updatedAt ?? new Date().toISOString(),
    observedAt: null,
    fetchedAt: event.updatedAt ?? event.issuedAt ?? null,
    status: event.severity,
    sourceDetail: "UK Environment Agency flood warning",
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
      areaName: event.areaName,
      severity: event.severity,
      evidenceBasis: event.evidenceBasis,
      caveat
    },
    severity: event.severity,
    severityLevel: event.severityLevel,
    areaName: event.areaName,
    floodAreaId: event.floodAreaId,
    riverOrSea: event.riverOrSea,
    county: event.county,
    region: event.region,
    message: event.message,
    description: event.description,
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat
  };
}

function toUkFloodStationEntity(station: UkEaFloodStation, caveat: string): UkEaFloodEntity {
  return {
    id: `ukflood:station:${station.stationId}`,
    type: "environmental-event",
    eventSource: "uk-ea-flood-monitoring",
    entityKind: "station-reading",
    eventId: station.stationId,
    source: "uk-environment-agency-flood-monitoring",
    label: station.stationLabel,
    latitude: station.latitude ?? 0,
    longitude: station.longitude ?? 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: station.observedAt ?? new Date().toISOString(),
    observedAt: station.observedAt ?? null,
    fetchedAt: station.observedAt ?? null,
    status: station.parameter,
    sourceDetail: "UK Environment Agency monitoring station",
    externalUrl: station.sourceUrl,
    confidence: null,
    historyAvailable: false,
    canonicalIds: { station_id: station.stationId },
    rawIdentifiers: {},
    quality: null,
    derivedFields: [],
    historySummary: null,
    linkTargets: [],
    metadata: {
      stationLabel: station.stationLabel,
      parameter: station.parameter,
      value: station.value,
      unit: station.unit,
      evidenceBasis: station.evidenceBasis,
      caveat
    },
    stationId: station.stationId,
    stationLabel: station.stationLabel,
    riverName: station.riverName,
    catchment: station.catchment,
    areaName: station.areaName,
    county: station.county,
    parameter: station.parameter,
    value: station.value,
    unit: station.unit,
    qualifier: station.qualifier,
    evidenceBasis: station.evidenceBasis,
    sourceMode: station.sourceMode,
    caveat
  };
}
