import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useTsunamiAlertsQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { TsunamiAlertEvent } from "../types/api";
import type { TsunamiAlertEntity } from "../types/entities";

interface TsunamiLayerProps {
  viewer: Viewer | null;
}

export function TsunamiLayer({ viewer }: TsunamiLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "tsunami")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setTsunamiEntities = useAppStore((state) => state.setTsunamiEntities);
  const tsunamiQuery = useTsunamiAlertsQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("tsunami-alerts");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setTsunamiEntities([]);
      return;
    }
    const events = tsunamiQuery.data?.events ?? [];
    const mapped = events.map((event) => toTsunamiEntity(event, tsunamiQuery.data?.metadata.caveat ?? event.caveat));
    for (const event of events) {
      if (event.longitude != null && event.latitude != null) {
        collection.add(buildTsunamiMarker(event, labelsEnabled));
      }
    }
    setTsunamiEntities(mapped);
  }, [enabled, labelsEnabled, setTsunamiEntities, tsunamiQuery.data, viewer]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("tsunami:")) return;
      const eventId = selected.id.replace("tsunami:", "");
      const event = tsunamiQuery.data?.events.find((item) => item.eventId === eventId);
      if (!event) return;
      setSelectedEntity(toTsunamiEntity(event, tsunamiQuery.data?.metadata.caveat ?? event.caveat));
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [setSelectedEntity, tsunamiQuery.data, viewer]);

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

function buildTsunamiMarker(event: TsunamiAlertEvent, labelsEnabled: boolean) {
  const color =
    event.alertType === "warning"
      ? Color.RED
      : event.alertType === "watch"
        ? Color.ORANGE
        : event.alertType === "advisory"
          ? Color.GOLD
          : event.alertType === "information"
            ? Color.CYAN
            : Color.LIGHTGRAY;
  return new Entity({
    id: `tsunami:${event.eventId}`,
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
          text: `${event.alertType.toUpperCase()} | ${event.sourceCenter}`,
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

function toTsunamiEntity(event: TsunamiAlertEvent, caveat: string): TsunamiAlertEntity {
  return {
    id: `tsunami:${event.eventId}`,
    type: "environmental-event",
    eventSource: "noaa-tsunami-alerts",
    eventId: event.eventId,
    source: "noaa-tsunami-warning-centers",
    label: event.title,
    latitude: event.latitude ?? 0,
    longitude: event.longitude ?? 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.issuedAt,
    observedAt: event.issuedAt,
    fetchedAt: event.updatedAt ?? event.issuedAt,
    status: event.alertType,
    sourceDetail: `NOAA ${event.sourceCenter}`,
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
      affectedRegions: event.affectedRegions,
      sourceCenter: event.sourceCenter,
      evidenceBasis: event.evidenceBasis,
      caveat
    },
    alertType: event.alertType,
    sourceCenter: event.sourceCenter,
    issuedAt: event.issuedAt,
    updatedAt: event.updatedAt,
    effectiveAt: event.effectiveAt,
    expiresAt: event.expiresAt,
    affectedRegions: event.affectedRegions,
    basin: event.basin,
    region: event.region,
    summary: event.summary,
    evidenceBasis: event.evidenceBasis,
    caveat
  };
}
