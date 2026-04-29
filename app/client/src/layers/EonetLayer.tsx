import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useEonetEventsQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { EonetEvent } from "../types/api";
import type { EonetEntity } from "../types/entities";

interface EonetLayerProps {
  viewer: Viewer | null;
}

export function EonetLayer({ viewer }: EonetLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "eonet")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setEonetEntities = useAppStore((state) => state.setEonetEntities);
  const eonetQuery = useEonetEventsQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("eonet-events");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setEonetEntities([]);
      return;
    }
    const events = eonetQuery.data?.events ?? [];
    const mapped: EonetEntity[] = events.map((event) => toEonetEntity(event, eonetQuery.data?.metadata.caveat ?? event.caveat));
    for (const event of events) {
      collection.add(buildEonetMarker(event, labelsEnabled));
    }
    setEonetEntities(mapped);
  }, [enabled, eonetQuery.data, labelsEnabled, setEonetEntities, viewer]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("eonet:")) return;
      const eventId = selected.id.replace("eonet:", "");
      const event = eonetQuery.data?.events.find((item) => item.eventId === eventId);
      if (!event) return;
      setSelectedEntity(toEonetEntity(event, eonetQuery.data?.metadata.caveat ?? event.caveat));
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [eonetQuery.data, setSelectedEntity, viewer]);

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

function buildEonetMarker(event: EonetEvent, labelsEnabled: boolean) {
  const category = (event.categoryTitles[0] ?? "").toLowerCase();
  const color = category.includes("wildfire")
    ? Color.ORANGE
    : category.includes("volcano")
      ? Color.RED
      : category.includes("storm")
        ? Color.CYAN
        : Color.LIGHTGREEN;
  const labelText = `${event.categoryTitles[0] ?? "Event"} | ${event.title}`;
  return new Entity({
    id: `eonet:${event.eventId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude, event.latitude, 0),
    point: {
      pixelSize: 9,
      color,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5
    },
    label: labelsEnabled
      ? {
          text: labelText,
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

function toEonetEntity(event: EonetEvent, caveat: string): EonetEntity {
  return {
    id: `eonet:${event.eventId}`,
    type: "environmental-event",
    eventSource: "nasa-eonet",
    eventId: event.eventId,
    source: event.source,
    label: event.title,
    latitude: event.latitude,
    longitude: event.longitude,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.eventDate,
    observedAt: event.eventDate,
    fetchedAt: event.updated ?? event.eventDate,
    status: event.status,
    sourceDetail: "NASA EONET",
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
      categories: event.categories,
      categoryIds: event.categoryIds,
      categoryTitles: event.categoryTitles,
      geometryType: event.geometryType,
      geometryCount: event.rawGeometryCount
    },
    eventDate: event.eventDate,
    categories: event.categoryTitles.length > 0 ? event.categoryTitles : event.categories,
    statusDetail: event.status,
    geometryType: event.geometryType,
    geometryCount: event.rawGeometryCount,
    coordinatesSummary: event.coordinatesSummary,
    description: event.description,
    closedAt: event.closed,
    caveat
  };
}
