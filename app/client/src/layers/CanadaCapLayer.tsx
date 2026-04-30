import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useCanadaCapAlertsQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { CanadaCapAlertEvent } from "../types/api";
import type { CanadaCapAlertEntity } from "../types/entities";

interface CanadaCapLayerProps {
  viewer: Viewer | null;
}

export function CanadaCapLayer({ viewer }: CanadaCapLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "canadaCap")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setCanadaCapEntities = useAppStore((state) => state.setCanadaCapEntities);
  const canadaCapQuery = useCanadaCapAlertsQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("canada-cap-alerts");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setCanadaCapEntities([]);
      return;
    }
    const alerts = canadaCapQuery.data?.alerts ?? [];
    const mapped = alerts.map((item) => toCanadaCapEntity(item, canadaCapQuery.data?.metadata.caveat ?? item.caveat));
    for (const item of alerts) {
      if (Number.isFinite(item.longitude) && Number.isFinite(item.latitude)) {
        collection.add(buildAlertMarker(item, labelsEnabled));
      }
    }
    setCanadaCapEntities(mapped);
  }, [enabled, canadaCapQuery.data, labelsEnabled, setCanadaCapEntities, viewer]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("canadacap:")) return;
      const eventId = selected.id.replace("canadacap:", "");
      const alert = canadaCapQuery.data?.alerts.find((item) => item.eventId === eventId);
      if (!alert) return;
      setSelectedEntity(toCanadaCapEntity(alert, canadaCapQuery.data?.metadata.caveat ?? alert.caveat));
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [canadaCapQuery.data, setSelectedEntity, viewer]);

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

function buildAlertMarker(event: CanadaCapAlertEvent, labelsEnabled: boolean) {
  const color =
    event.severity === "extreme"
      ? Color.RED
      : event.severity === "severe"
        ? Color.ORANGE
        : event.severity === "moderate"
          ? Color.GOLD
          : Color.CYAN;
  return new Entity({
    id: `canadacap:${event.eventId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude ?? 0, event.latitude ?? 0, 0),
    point: {
      pixelSize: 8,
      color,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5,
    },
    label: labelsEnabled
      ? {
          text: `${event.alertType.toUpperCase()} | ${event.severity}`,
          font: "11px sans-serif",
          fillColor: Color.WHITE,
          outlineColor: Color.BLACK,
          outlineWidth: 2,
          style: LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: VerticalOrigin.BOTTOM,
          pixelOffset: new Cartesian2(0, -14),
        }
      : undefined,
  });
}

function toCanadaCapEntity(event: CanadaCapAlertEvent, caveat: string): CanadaCapAlertEntity {
  return {
    id: `canadacap:${event.eventId}`,
    type: "environmental-event",
    eventSource: "environment-canada-cap",
    eventId: event.eventId,
    source: "environment-canada-cap-alerts",
    label: event.title,
    latitude: event.latitude ?? Number.NaN,
    longitude: event.longitude ?? Number.NaN,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.sentAt,
    observedAt: event.effectiveAt ?? null,
    fetchedAt: event.updatedAt ?? event.sentAt,
    status: event.alertType,
    sourceDetail: "Environment Canada CAP alert",
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
      severity: event.severity,
      urgency: event.urgency,
      certainty: event.certainty,
      evidenceBasis: event.evidenceBasis,
      caveat,
    },
    alertType: event.alertType,
    severity: event.severity,
    urgency: event.urgency,
    certainty: event.certainty,
    areaDescription: event.areaDescription,
    provinceOrRegion: event.provinceOrRegion,
    effectiveAt: event.effectiveAt,
    onsetAt: event.onsetAt,
    expiresAt: event.expiresAt,
    geometrySummary: event.geometrySummary,
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat,
  };
}
