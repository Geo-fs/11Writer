import { useEffect, useRef } from "react";
import { Cartesian2, Cartesian3, Color, CustomDataSource, Entity, LabelStyle, VerticalOrigin } from "cesium";
import type { Viewer } from "cesium";

import { useGeoNetHazardsQuery } from "../lib/queries";
import { consumeManualSelectionClear } from "../lib/selectionInteraction";
import { useAppStore } from "../lib/store";
import type { GeoNetHazardEntity } from "../types/entities";
import type { GeoNetQuakeEvent, GeoNetVolcanoAlert } from "../types/api";

interface GeoNetLayerProps {
  viewer: Viewer | null;
}

export function GeoNetLayer({ viewer }: GeoNetLayerProps) {
  const dataSourceRef = useRef<CustomDataSource | null>(null);
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.environmentalFilters);
  const enabled = layers.find((layer) => layer.key === "geonet")?.enabled ?? false;
  const labelsEnabled = layers.find((layer) => layer.key === "labels")?.enabled ?? true;
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const setGeoNetEntities = useAppStore((state) => state.setGeoNetEntities);
  const geonetQuery = useGeoNetHazardsQuery(filters, Boolean(viewer && enabled));

  useEffect(() => {
    if (!viewer) return;
    if (!dataSourceRef.current) {
      const dataSource = new CustomDataSource("geonet-hazards");
      dataSourceRef.current = dataSource;
      void viewer.dataSources.add(dataSource);
    }
  }, [viewer]);

  useEffect(() => {
    if (!viewer || !dataSourceRef.current) return;
    const collection = dataSourceRef.current.entities;
    collection.removeAll();
    if (!enabled) {
      setGeoNetEntities([]);
      return;
    }
    const quakes = geonetQuery.data?.quakes ?? [];
    const volcanoAlerts = geonetQuery.data?.volcanoAlerts ?? [];
    const metadataCaveat = geonetQuery.data?.metadata.caveat ?? null;
    const mapped = [
      ...quakes.map((event) => toGeoNetQuakeEntity(event, metadataCaveat ?? event.caveat)),
      ...volcanoAlerts.map((event) => toGeoNetVolcanoEntity(event, metadataCaveat ?? event.caveat)),
    ];
    for (const quake of quakes) {
      if (quake.longitude != null && quake.latitude != null) {
        collection.add(buildQuakeMarker(quake, labelsEnabled));
      }
    }
    for (const alert of volcanoAlerts) {
      if (alert.longitude != null && alert.latitude != null) {
        collection.add(buildVolcanoMarker(alert, labelsEnabled));
      }
    }
    setGeoNetEntities(mapped);
  }, [enabled, geonetQuery.data, labelsEnabled, setGeoNetEntities, viewer]);

  useEffect(() => {
    if (!viewer) return;
    const handleSelection = (selected: Entity | undefined) => {
      if (!selected) {
        if (consumeManualSelectionClear()) setSelectedEntity(null);
        return;
      }
      if (!selected.id.startsWith("geonet:")) return;
      const [kind, itemId] = selected.id.replace("geonet:", "").split(":", 2);
      if (kind === "quake") {
        const quake = geonetQuery.data?.quakes.find((item) => item.eventId === itemId);
        if (quake) {
          setSelectedEntity(toGeoNetQuakeEntity(quake, geonetQuery.data?.metadata.caveat ?? quake.caveat));
        }
      } else if (kind === "volcano") {
        const alert = geonetQuery.data?.volcanoAlerts.find((item) => item.volcanoId === itemId);
        if (alert) {
          setSelectedEntity(toGeoNetVolcanoEntity(alert, geonetQuery.data?.metadata.caveat ?? alert.caveat));
        }
      }
    };
    viewer.selectedEntityChanged.addEventListener(handleSelection);
    return () => {
      viewer.selectedEntityChanged.removeEventListener(handleSelection);
    };
  }, [geonetQuery.data, setSelectedEntity, viewer]);

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

function buildQuakeMarker(event: GeoNetQuakeEvent, labelsEnabled: boolean) {
  const color =
    (event.magnitude ?? 0) >= 5 ? Color.ORANGE : (event.magnitude ?? 0) >= 4 ? Color.GOLD : Color.CYAN;
  return new Entity({
    id: `geonet:quake:${event.eventId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude ?? 0, event.latitude ?? 0, 0),
    point: {
      pixelSize: 8,
      color,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5
    },
    label: labelsEnabled
      ? {
          text: event.magnitude != null ? `M${event.magnitude.toFixed(1)}` : "quake",
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

function buildVolcanoMarker(event: GeoNetVolcanoAlert, labelsEnabled: boolean) {
  const color = (event.alertLevel ?? 0) >= 3 ? Color.RED : (event.alertLevel ?? 0) >= 1 ? Color.ORANGE : Color.LIGHTGRAY;
  return new Entity({
    id: `geonet:volcano:${event.volcanoId}`,
    name: event.title,
    position: Cartesian3.fromDegrees(event.longitude ?? 0, event.latitude ?? 0, 0),
    point: {
      pixelSize: 8,
      color,
      outlineColor: Color.BLACK.withAlpha(0.75),
      outlineWidth: 1.5
    },
    label: labelsEnabled
      ? {
          text: `VAL ${event.alertLevel ?? "?"}`,
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

function toGeoNetQuakeEntity(event: GeoNetQuakeEvent, caveat: string): GeoNetHazardEntity {
  return {
    id: `geonet:quake:${event.eventId}`,
    type: "environmental-event",
    eventSource: "geonet-nz",
    entityKind: "quake",
    eventId: event.eventId,
    publicId: event.publicId,
    source: "geonet-new-zealand",
    label: event.locality ?? event.title,
    latitude: event.latitude ?? 0,
    longitude: event.longitude ?? 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.eventTime,
    observedAt: event.eventTime,
    fetchedAt: event.updatedAt ?? event.eventTime,
    status: event.quality ?? event.status ?? "quake",
    sourceDetail: "GeoNet earthquake record",
    externalUrl: event.sourceUrl,
    confidence: null,
    historyAvailable: false,
    canonicalIds: { event_id: event.eventId, public_id: event.publicId },
    rawIdentifiers: {},
    quality: event.quality
      ? {
          label: event.quality,
          notes: ["GeoNet quality string preserved from source event."]
        }
      : null,
    derivedFields: [],
    historySummary: null,
    linkTargets: [],
    metadata: { caveat, evidenceBasis: event.evidenceBasis },
    magnitude: event.magnitude,
    depthKm: event.depthKm,
    locality: event.locality,
    region: event.region,
    geonetQuality: event.quality,
    statusDetail: event.status,
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat
  };
}

function toGeoNetVolcanoEntity(event: GeoNetVolcanoAlert, caveat: string): GeoNetHazardEntity {
  return {
    id: `geonet:volcano:${event.volcanoId}`,
    type: "environmental-event",
    eventSource: "geonet-nz",
    entityKind: "volcano-alert",
    eventId: event.volcanoId,
    source: "geonet-new-zealand",
    label: event.title,
    latitude: event.latitude ?? 0,
    longitude: event.longitude ?? 0,
    altitude: 0,
    heading: null,
    speed: null,
    timestamp: event.updatedAt ?? event.issuedAt ?? new Date().toISOString(),
    observedAt: null,
    fetchedAt: event.updatedAt ?? event.issuedAt ?? null,
    status: event.alertLevel != null ? `VAL ${event.alertLevel}` : "volcano-alert",
    sourceDetail: "GeoNet volcanic alert level",
    externalUrl: event.sourceUrl,
    confidence: null,
    historyAvailable: false,
    canonicalIds: { volcano_id: event.volcanoId },
    rawIdentifiers: {},
    quality: null,
    derivedFields: [],
    historySummary: null,
    linkTargets: [],
    metadata: { caveat, evidenceBasis: event.evidenceBasis },
    volcanoId: event.volcanoId,
    volcanoName: event.volcanoName,
    alertLevel: event.alertLevel,
    aviationColorCode: event.aviationColorCode,
    geonetQuality: null,
    activity: event.activity,
    hazards: event.hazards,
    evidenceBasis: event.evidenceBasis,
    sourceMode: event.sourceMode,
    caveat
  };
}
