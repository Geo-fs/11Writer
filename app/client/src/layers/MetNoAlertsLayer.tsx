import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useMetNoMetAlertsQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { MetNoMetAlertEvent } from "../types/api";
import type { MetNoAlertEntity } from "../types/entities";

interface MetNoAlertsLayerProps {
  viewer: Viewer | null;
}

export function MetNoAlertsLayer({ viewer }: MetNoAlertsLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "metnoAlerts")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setMetNoAlertEntities = useAppStore((state) => state.setMetNoAlertEntities);
  const metnoQuery = useMetNoMetAlertsQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("metno-alerts");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setMetNoAlertEntities([]);
      return;
    }
    const metadataCaveat = metnoQuery.data?.metadata.caveat ?? null;
    const mapped = (metnoQuery.data?.alerts ?? [])
      .map((event) => toMetNoAlertEntity(event, metadataCaveat ?? event.caveat))
      .filter((item): item is MetNoAlertEntity => item != null);
    for (const entity of mapped) {
      collection.add(buildAlertMarker(entity, labelsEnabled));
    }
    setMetNoAlertEntities(mapped);
  }, [enabled, labelsEnabled, metnoQuery.data, setMetNoAlertEntities, viewer]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("metno:")) return;
      const eventId = selected.id.replace("metno:", "");
      const match = metnoQuery.data?.alerts.find((item) => item.eventId === eventId);
      if (match) {
        const entity = toMetNoAlertEntity(match, metnoQuery.data?.metadata.caveat ?? match.caveat);
        if (entity) setSelectedEntity(entity);
      }
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [metnoQuery.data, setSelectedEntity, viewer]);

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

function buildAlertMarker(entity: MetNoAlertEntity, labelsEnabled: boolean) {
  return new Entity({
    id: entity.id,
    name: entity.label,
    position: Cartesian3.fromDegrees(entity.longitude, entity.latitude, 0),
    point: {
      pixelSize: 8,
      color: severityColor(entity.severity),
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5
    },
    label: labelsEnabled
      ? {
          text: entity.severity.toUpperCase(),
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

function toMetNoAlertEntity(event: MetNoMetAlertEvent, caveat: string): MetNoAlertEntity | null {
  const bbox = [
    event.bboxMinLon ?? null,
    event.bboxMinLat ?? null,
    event.bboxMaxLon ?? null,
    event.bboxMaxLat ?? null
  ] as const;
  if (bbox.some((value) => value == null)) {
    return null;
  }
  const [minLon, minLat, maxLon, maxLat] = bbox as [number, number, number, number];
  const longitude = (minLon + maxLon) / 2;
  const latitude = (minLat + maxLat) / 2;
  const bboxSummary = `${minLat.toFixed(2)},${minLon.toFixed(2)} to ${maxLat.toFixed(2)},${maxLon.toFixed(2)}`;
  return {
    id: `metno:${event.eventId}`,
    type: "environmental-event",
    eventSource: "met-norway-metalerts",
    entityKind: "weather-alert",
    eventId: event.eventId,
    source: "met-norway-metalerts",
    label: event.title,
    latitude,
    longitude,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.updatedAt ?? event.effectiveAt ?? event.sentAt ?? new Date().toISOString(),
    observedAt: null,
    fetchedAt: event.updatedAt ?? event.sentAt ?? null,
    status: event.severity,
    sourceDetail: "MET Norway weather alert",
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
      bboxSummary,
      coordinateProvenance: "bbox-centroid",
      evidenceBasis: event.evidenceBasis,
      caveat
    },
    alertType: event.alertType,
    severity: event.severity,
    certainty: event.certainty,
    urgency: event.urgency,
    areaDescription: event.areaDescription,
    effectiveAt: event.effectiveAt,
    onsetAt: event.onsetAt,
    expiresAt: event.expiresAt,
    sentAt: event.sentAt,
    updatedAt: event.updatedAt,
    msgType: event.msgType,
    statusDetail: event.status,
    geometrySummary: event.geometrySummary,
    bboxSummary,
    coordinateProvenance: "bbox-centroid",
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat
  };
}

function severityColor(severity: MetNoAlertEntity["severity"]) {
  switch (severity) {
    case "red":
      return Color.RED;
    case "orange":
      return Color.ORANGE;
    case "yellow":
      return Color.GOLD;
    case "green":
      return Color.LIGHTGREEN;
    case "unknown":
    default:
      return Color.LIGHTGRAY;
  }
}
