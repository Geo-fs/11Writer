import {
  Cartesian3,
  Color,
  EllipsoidTerrainProvider,
  Ion,
  Math as CesiumMath,
  type ScreenSpaceEventHandler as ScreenSpaceEventHandlerType,
  ScreenSpaceEventHandler,
  ScreenSpaceEventType,
  defined,
  Viewer
} from "cesium";
import { markManualSelectionClear, resetManualSelectionClear } from "./selectionInteraction";

export function createViewer(container: HTMLElement) {
  Ion.defaultAccessToken = "";

  const viewer = new Viewer(container, {
    animation: false,
    baseLayer: false,
    terrainProvider: new EllipsoidTerrainProvider(),
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    infoBox: false,
    navigationHelpButton: false,
    timeline: false,
    sceneModePicker: false,
    selectionIndicator: false,
    fullscreenButton: false,
    shouldAnimate: true
  });

  viewer.scene.globe.depthTestAgainstTerrain = false;
  if (viewer.scene.skyAtmosphere) {
    viewer.scene.skyAtmosphere.hueShift = -0.02;
    viewer.scene.skyAtmosphere.saturationShift = -0.1;
    viewer.scene.skyAtmosphere.brightnessShift = -0.15;
  }
  viewer.scene.highDynamicRange = true;
  viewer.scene.backgroundColor = Color.BLACK;
  viewer.clock.shouldAnimate = true;
  viewer.camera.setView({
    destination: Cartesian3.fromDegrees(-97.7431, 30.2672, 4_500_000),
    orientation: {
      heading: 0,
      pitch: -CesiumMath.PI_OVER_TWO,
      roll: 0
    }
  });

  const handler = new ScreenSpaceEventHandler(viewer.scene.canvas);
  handler.setInputAction((movement: ScreenSpaceEventHandlerType.PositionedEvent) => {
    const picked = viewer.scene.pick(movement.position);
    if (defined(picked)) {
      resetManualSelectionClear();
      return;
    }
    if (viewer.selectedEntity) {
      markManualSelectionClear();
      viewer.selectedEntity = undefined;
    } else {
      resetManualSelectionClear();
    }
  }, ScreenSpaceEventType.LEFT_CLICK);
  handler.setInputAction(() => {
    markManualSelectionClear();
    viewer.selectedEntity = undefined;
  }, ScreenSpaceEventType.LEFT_DOUBLE_CLICK);

  return {
    viewer,
    dispose: () => {
      handler.destroy();
      viewer.destroy();
    }
  };
}

export async function applyFallbackTerrain(viewer: Viewer) {
  viewer.terrainProvider = new EllipsoidTerrainProvider();
}
