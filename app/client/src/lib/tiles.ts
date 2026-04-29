import { GoogleMaps, createGooglePhotorealistic3DTileset } from "cesium";
import type { Cesium3DTileset, Viewer } from "cesium";

export interface TilesLoadResult {
  providerName: "google-photorealistic-3d" | "cesium-world-terrain";
  tileset?: Cesium3DTileset;
  warning?: string;
}

export async function loadPrimaryTiles(
  viewer: Viewer,
  googleMapsApiKey?: string | null
): Promise<TilesLoadResult> {
  if (!googleMapsApiKey) {
    return {
      providerName: "cesium-world-terrain",
      warning: "Google Maps API key missing. Running in fallback terrain mode."
    };
  }

  GoogleMaps.defaultApiKey = googleMapsApiKey;

  try {
    const tileset = await createGooglePhotorealistic3DTileset();
    viewer.scene.primitives.add(tileset);
    return {
      providerName: "google-photorealistic-3d",
      tileset
    };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown Google tiles error.";

    return {
      providerName: "cesium-world-terrain",
      warning: `Google tiles unavailable. Falling back to Cesium terrain. ${message}`
    };
  }
}
