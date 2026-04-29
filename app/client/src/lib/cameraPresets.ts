import { Cartesian3, Math as CesiumMath } from "cesium";
import type { Viewer } from "cesium";

export type CameraPresetKey = "global" | "austin" | "nyc" | "london";

export interface CameraPreset {
  key: CameraPresetKey;
  label: string;
  destination: Cartesian3;
  heading: number;
  pitch: number;
  roll: number;
}

const presets: Record<CameraPresetKey, CameraPreset> = {
  global: {
    key: "global",
    label: "Global Reset",
    destination: Cartesian3.fromDegrees(-97.7431, 30.2672, 4_500_000),
    heading: 0,
    pitch: -CesiumMath.PI_OVER_TWO,
    roll: 0
  },
  austin: {
    key: "austin",
    label: "Austin Demo",
    destination: Cartesian3.fromDegrees(-97.7431, 30.2672, 1600),
    heading: CesiumMath.toRadians(18),
    pitch: CesiumMath.toRadians(-22),
    roll: 0
  },
  nyc: {
    key: "nyc",
    label: "NYC Demo",
    destination: Cartesian3.fromDegrees(-74.006, 40.7128, 1800),
    heading: CesiumMath.toRadians(32),
    pitch: CesiumMath.toRadians(-28),
    roll: 0
  },
  london: {
    key: "london",
    label: "London",
    destination: Cartesian3.fromDegrees(-0.1276, 51.5072, 2200),
    heading: CesiumMath.toRadians(24),
    pitch: CesiumMath.toRadians(-27),
    roll: 0
  }
};

export function getCameraPresets(): CameraPreset[] {
  return Object.values(presets);
}

export function flyToPreset(viewer: Viewer, key: CameraPresetKey) {
  const preset = presets[key];
  viewer.camera.flyTo({
    destination: preset.destination,
    orientation: {
      heading: preset.heading,
      pitch: preset.pitch,
      roll: preset.roll
    },
    duration: 1.8
  });
}
