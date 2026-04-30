import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useVolcanoStatusQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { VolcanoStatusEvent } from "../types/api";
import type { VolcanoEntity } from "../types/entities";

interface VolcanoLayerProps {
  viewer: Viewer | null;
}

export function VolcanoLayer({ viewer }: VolcanoLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "volcanoes")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setVolcanoEntities = useAppStore((state) => state.setVolcanoEntities);
  const volcanoQuery = useVolcanoStatusQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("volcano-status");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setVolcanoEntities([]);
      return;
    }
    const events = volcanoQuery.data?.events ?? [];
    const mapped = events.map((event) => toVolcanoEntity(event, volcanoQuery.data?.metadata.caveat ?? event.caveat));
    for (const event of events) {
      collection.add(buildVolcanoMarker(event, labelsEnabled));
    }
    setVolcanoEntities(mapped);
  }, [enabled, labelsEnabled, setVolcanoEntities, viewer, volcanoQuery.data]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("volcano:")) return;
      const eventId = selected.id.replace("volcano:", "");
      const event = volcanoQuery.data?.events.find((item) => item.eventId === eventId);
      if (!event) return;
      setSelectedEntity(toVolcanoEntity(event, volcanoQuery.data?.metadata.caveat ?? event.caveat));
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [setSelectedEntity, viewer, volcanoQuery.data]);

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

function buildVolcanoMarker(event: VolcanoStatusEvent, labelsEnabled: boolean) {
  const color =
    event.alertLevel === "WARNING"
      ? Color.RED
      : event.alertLevel === "WATCH"
        ? Color.ORANGE
        : event.alertLevel === "ADVISORY"
          ? Color.GOLD
          : Color.LIGHTGRAY;
  return new Entity({
    id: `volcano:${event.eventId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude, event.latitude, Math.max(0, event.elevationMeters ?? 0)),
    point: {
      pixelSize: 10,
      color,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5
    },
    label: labelsEnabled
      ? {
          text: `${event.volcanoName} | ${event.alertLevel}`,
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

function toVolcanoEntity(event: VolcanoStatusEvent, caveat: string): VolcanoEntity {
  return {
    id: `volcano:${event.eventId}`,
    type: "environmental-event",
    eventSource: "usgs-volcano-hazards",
    eventId: event.eventId,
    source: event.source,
    label: event.title,
    latitude: event.latitude,
    longitude: event.longitude,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.issuedAt,
    observedAt: event.issuedAt,
    fetchedAt: event.issuedAt,
    status: event.alertLevel,
    sourceDetail: "USGS Volcano Hazards Program",
    externalUrl: event.sourceUrl,
    confidence: null,
    historyAvailable: false,
    canonicalIds: { event_id: event.eventId, volcano_number: event.volcanoNumber },
    rawIdentifiers: {},
    quality: null,
    derivedFields: [],
    historySummary: null,
    linkTargets: [],
    metadata: {
      observatoryName: event.observatoryName,
      aviationColorCode: event.aviationColorCode,
      noticeTypeCode: event.noticeTypeCode,
      noticeIdentifier: event.noticeIdentifier,
      caveat
    },
    volcanoName: event.volcanoName,
    volcanoNumber: event.volcanoNumber,
    volcanoCode: event.volcanoCode,
    observatoryName: event.observatoryName,
    observatoryAbbr: event.observatoryAbbr,
    region: event.region,
    elevationMeters: event.elevationMeters,
    alertLevel: event.alertLevel,
    aviationColorCode: event.aviationColorCode,
    noticeTypeCode: event.noticeTypeCode,
    noticeTypeLabel: event.noticeTypeLabel,
    noticeIdentifier: event.noticeIdentifier,
    statusScope: event.statusScope,
    volcanoUrl: event.volcanoUrl,
    nvewsThreat: event.nvewsThreat,
    caveat
  };
}
