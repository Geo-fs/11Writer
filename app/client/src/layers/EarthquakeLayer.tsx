import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useEarthquakeEventsQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { EarthquakeEvent } from "../types/api";
import type { EarthquakeEntity } from "../types/entities";

interface EarthquakeLayerProps {
  viewer: Viewer | null;
}

export function EarthquakeLayer({ viewer }: EarthquakeLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "earthquakes")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setEarthquakeEntities = useAppStore((state) => state.setEarthquakeEntities);
  const earthquakeQuery = useEarthquakeEventsQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) {
      return;
    }
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("earthquakes");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) {
      return;
    }

    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setEarthquakeEntities([]);
      return;
    }
    const events = earthquakeQuery.data?.events ?? [];
    const caveat = earthquakeQuery.data?.metadata.caveat ?? "USGS magnitude alone does not imply impact.";
    const mappedEntities: EarthquakeEntity[] = events.map((event) => toEarthquakeEntity(event, caveat));

    for (const event of events) {
      collection.add(buildEarthquakeMarker(event, labelsEnabled));
    }
    setEarthquakeEntities(mappedEntities);
  }, [earthquakeQuery.data, enabled, labelsEnabled, setEarthquakeEntities, viewer]);

  useEffect(() => {
    if (!viewer) {
      return;
    }
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) {
          setSelectedEntity(null);
        }
        return;
      }
      if (!selected.id.startsWith("earthquake:")) {
        return;
      }
      const eventId = selected.id.replace("earthquake:", "");
      const event = earthquakeQuery.data?.events.find((item) => item.eventId === eventId);
      if (!event) {
        return;
      }
      const caveat = earthquakeQuery.data?.metadata.caveat ?? "USGS magnitude alone does not imply impact.";
      setSelectedEntity(toEarthquakeEntity(event, caveat));
    };

    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [earthquakeQuery.data, setSelectedEntity, viewer]);

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

function buildEarthquakeMarker(event: EarthquakeEvent, labelsEnabled: boolean) {
  const magnitude = event.magnitude ?? 0;
  const pixelSize = Math.max(6, Math.min(20, 6 + magnitude * 2.2));
  const color = magnitude >= 6 ? Color.ORANGE : magnitude >= 4 ? Color.GOLD : Color.YELLOW;
  const labelText = event.magnitude != null ? `M${event.magnitude.toFixed(1)} ${event.place ?? event.title}` : event.title;

  return new Entity({
    id: `earthquake:${event.eventId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude, event.latitude, Math.max(0, (event.depthKm ?? 0) * 10)),
    properties: {
      source: event.source,
      magnitude: event.magnitude,
      magnitudeType: event.magnitudeType,
      depthKm: event.depthKm,
      eventType: event.eventType,
      tsunami: event.tsunami,
      significance: event.significance,
      status: event.status
    },
    point: {
      pixelSize,
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

function toEarthquakeEntity(event: EarthquakeEvent, caveat: string): EarthquakeEntity {
  return {
    id: `earthquake:${event.eventId}`,
    type: "environmental-event",
    eventId: event.eventId,
    source: event.source,
    label: event.title,
    latitude: event.latitude,
    longitude: event.longitude,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.time,
    observedAt: event.time,
    fetchedAt: event.updated ?? event.time,
    status: event.status ?? "reported",
    sourceDetail: "USGS Earthquake Hazards Program",
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
      alert: event.alert,
      significance: event.significance,
      felt: event.felt,
      cdi: event.cdi,
      mmi: event.mmi,
      tsunami: event.tsunami,
      caveat
    },
    eventType: event.eventType,
    magnitude: event.magnitude,
    magnitudeType: event.magnitudeType,
    depthKm: event.depthKm,
    place: event.place,
    updated: event.updated,
    tsunami: event.tsunami,
    significance: event.significance,
    alert: event.alert,
    felt: event.felt,
    cdi: event.cdi,
    mmi: event.mmi,
    caveat
  };
}
