import {
  Credit,
  ImageryLayer,
  SingleTileImageryProvider,
  UrlTemplateImageryProvider,
  WebMapTileServiceImageryProvider
} from "cesium";
import type {
  PlanetConfigResponse,
  PlanetImageryCategory,
  PlanetImageryMode
} from "../types/api";

export interface GroupedImageryModes {
  category: PlanetImageryCategory;
  modes: PlanetImageryMode[];
}

export interface AppliedPlanetImageryMode {
  mode: PlanetImageryMode;
  layer: ImageryLayer;
  warning?: string;
  requestedModeId: string;
  usedFallback: boolean;
}

export interface PlanetImageryFailureSubscription {
  dispose: () => void;
}

export interface InitialImageryModeResolution {
  modeId: string;
  source: "permalink" | "local-storage" | "default" | "first-available";
  warning?: string;
}

export interface ActiveImageryContext {
  modeId: string;
  title: string;
  source: string;
  modeRole: PlanetImageryMode["modeRole"];
  sensorFamily: PlanetImageryMode["sensorFamily"];
  shortCaveat: string;
  temporalNature: PlanetImageryMode["temporalNature"];
  cloudBehavior: PlanetImageryMode["cloudBehavior"];
}

export function resolveInitialImageryModeId(options: {
  availableModes: PlanetImageryMode[];
  defaultModeId: string;
  viewStateModeId?: string | null;
  storedModeId?: string | null;
}): InitialImageryModeResolution {
  const validIds = new Set(options.availableModes.map((mode) => mode.id));
  if (options.viewStateModeId && validIds.has(options.viewStateModeId)) {
    return { modeId: options.viewStateModeId, source: "permalink" };
  }
  if (options.storedModeId && validIds.has(options.storedModeId)) {
    return { modeId: options.storedModeId, source: "local-storage" };
  }
  const invalidSelections = [options.viewStateModeId, options.storedModeId].filter(
    (value) => value && !validIds.has(value)
  ) as string[];
  if (validIds.has(options.defaultModeId)) {
    return {
      modeId: options.defaultModeId,
      source: "default",
      warning:
        invalidSelections.length > 0
          ? `Unavailable imagery mode(s): ${invalidSelections.join(", ")}. Restored default mode.`
          : undefined
    };
  }
  const firstAvailable = options.availableModes[0]?.id ?? options.defaultModeId;
  return {
    modeId: firstAvailable,
    source: "first-available",
    warning:
      invalidSelections.length > 0
        ? `Unavailable imagery mode(s): ${invalidSelections.join(", ")}. Restored first available mode.`
        : "Configured default imagery mode is missing; restored first available mode."
  };
}

export function buildActiveImageryContext(mode: PlanetImageryMode): ActiveImageryContext {
  return {
    modeId: mode.id,
    title: mode.title,
    source: mode.source,
    modeRole: mode.modeRole,
    sensorFamily: mode.sensorFamily,
    shortCaveat: mode.shortCaveat,
    temporalNature: mode.temporalNature,
    cloudBehavior: mode.cloudBehavior
  };
}

export function groupPlanetImageryModes(
  categories: PlanetImageryCategory[],
  imageryModes: PlanetImageryMode[]
): GroupedImageryModes[] {
  return [...categories]
    .sort((left, right) => left.order - right.order)
    .map((category) => ({
      category,
      modes: sortImageryModesForPicker(imageryModes.filter((mode) => mode.category === category.id))
    }))
    .filter((group) => group.modes.length > 0);
}

function sortImageryModesForPicker(modes: PlanetImageryMode[]) {
  return [...modes].sort((left, right) => {
    const roleScore = roleOrder(left.modeRole) - roleOrder(right.modeRole);
    if (roleScore !== 0) {
      return roleScore;
    }
    if (left.defaultReady !== right.defaultReady) {
      return left.defaultReady ? -1 : 1;
    }
    return left.title.localeCompare(right.title);
  });
}

function roleOrder(role: PlanetImageryMode["modeRole"]) {
  switch (role) {
    case "default-basemap":
      return 0;
    case "optional-basemap":
      return 1;
    case "analysis-layer":
      return 2;
    default:
      return 3;
  }
}

export function resolvePlanetImageryMode(
  planetConfig: PlanetConfigResponse,
  modeId: string | null | undefined
): { mode: PlanetImageryMode; requestedModeId: string; warning?: string } {
  const requestedModeId = modeId ?? planetConfig.defaultImageryModeId;
  const exactMode = planetConfig.imageryModes.find((mode) => mode.id === requestedModeId);
  if (exactMode) {
    return { mode: exactMode, requestedModeId };
  }
  const fallbackMode =
    planetConfig.imageryModes.find((mode) => mode.id === planetConfig.defaultImageryModeId) ??
    planetConfig.imageryModes[0];
  if (!fallbackMode) {
    throw new Error("No imagery modes are configured.");
  }
  return {
    mode: fallbackMode,
    requestedModeId,
    warning: `Imagery mode "${requestedModeId}" was unavailable. Falling back to ${fallbackMode.title}.`
  };
}

export function applyPlanetImageryMode(options: {
  currentLayer: ImageryLayer | null;
  modeId: string | null | undefined;
  planetConfig: PlanetConfigResponse;
  viewer: {
    imageryLayers: {
      add: (layer: ImageryLayer, index?: number) => ImageryLayer | void;
      remove: (layer: ImageryLayer, destroy?: boolean) => boolean;
    };
  };
}): AppliedPlanetImageryMode {
  const resolved = resolvePlanetImageryMode(options.planetConfig, options.modeId);
  const nextLayer = createImageryLayerWithFallback(
    options.planetConfig,
    resolved.mode,
    options.modeId
  );
  options.viewer.imageryLayers.add(nextLayer, 0);
  if (options.currentLayer) {
    options.viewer.imageryLayers.remove(options.currentLayer, true);
  }
  return {
    mode: (nextLayer as ImageryLayer & { __mode?: PlanetImageryMode }).__mode ?? resolved.mode,
    layer: nextLayer,
    warning:
      (nextLayer as ImageryLayer & { __warning?: string }).__warning ?? resolved.warning,
    requestedModeId: resolved.requestedModeId,
    usedFallback: Boolean(
      (nextLayer as ImageryLayer & { __warning?: string }).__warning ?? resolved.warning
    )
  };
}

export function subscribeToImageryProviderFailures(
  layer: ImageryLayer,
  onFailure: (warning: string) => void
): PlanetImageryFailureSubscription {
  const provider = (
    layer as ImageryLayer & {
      imageryProvider?: {
        errorEvent?: {
          addEventListener?: (listener: (error: unknown) => void) => void | (() => void);
          removeEventListener?: (listener: (error: unknown) => void) => void;
        };
      };
    }
  ).imageryProvider;
  const errorEvent = provider?.errorEvent;
  if (!errorEvent?.addEventListener) {
    return { dispose: () => undefined };
  }

  let failureCount = 0;
  let disposed = false;
  const listener = (error: unknown) => {
    if (disposed) {
      return;
    }
    const retries =
      typeof error === "object" &&
      error !== null &&
      "timesRetried" in error &&
      typeof (error as { timesRetried?: unknown }).timesRetried === "number"
        ? (error as { timesRetried: number }).timesRetried
        : 0;
    failureCount += 1;
    if (failureCount >= 3 || retries >= 2) {
      onFailure(buildProviderFailureMessage(error));
    }
  };

  const remove = errorEvent.addEventListener(listener);
  return {
    dispose: () => {
      disposed = true;
      if (typeof remove === "function") {
        remove();
        return;
      }
      errorEvent.removeEventListener?.(listener);
    }
  };
}

function createImageryLayerWithFallback(
  planetConfig: PlanetConfigResponse,
  mode: PlanetImageryMode,
  requestedModeId: string | null | undefined
) {
  try {
    const layer = new ImageryLayer(createImageryProvider(mode)) as ImageryLayer & {
      __mode?: PlanetImageryMode;
      __warning?: string;
    };
    layer.__mode = mode;
    return layer;
  } catch (error) {
    const fallbackMode =
      planetConfig.imageryModes.find((item) => item.id === planetConfig.defaultImageryModeId) ??
      planetConfig.imageryModes[0];
    if (!fallbackMode || fallbackMode.id === mode.id) {
      throw error;
    }
    const fallbackLayer = new ImageryLayer(createImageryProvider(fallbackMode)) as ImageryLayer & {
      __mode?: PlanetImageryMode;
      __warning?: string;
    };
    fallbackLayer.__mode = fallbackMode;
    fallbackLayer.__warning = `Imagery mode "${requestedModeId ?? mode.id}" failed to initialize. Falling back to ${fallbackMode.title}.`;
    return fallbackLayer;
  }
}

function createImageryProvider(mode: PlanetImageryMode) {
  const credit = new Credit(`${mode.source} | ${mode.licenseAccessNotes}`);
  switch (mode.providerType) {
    case "wmts":
      if (!mode.providerLayer) {
        throw new Error(`Imagery mode ${mode.id} is missing providerLayer.`);
      }
      return new WebMapTileServiceImageryProvider({
        url: mode.providerUrl,
        layer: mode.providerLayer,
        style: mode.providerStyle ?? "default",
        format: mode.providerFormat ?? "image/jpeg",
        tileMatrixSetID: mode.providerTileMatrixSetId ?? "GoogleMapsCompatible_Level9",
        maximumLevel: mode.providerMaximumLevel ?? undefined,
        dimensions: buildProviderDimensions(mode),
        credit
      });
    case "template":
      return new UrlTemplateImageryProvider({
        url: mode.providerUrl,
        maximumLevel: mode.providerMaximumLevel ?? undefined,
        credit
      });
    case "single-tile":
      return new SingleTileImageryProvider({
        url: mode.providerUrl,
        credit
      });
    default:
      throw new Error(`Unsupported imagery provider type: ${String(mode.providerType)}`);
  }
}

function buildProviderDimensions(mode: PlanetImageryMode): Record<string, string> {
  const dimensions = { ...mode.providerDimensions };
  switch (mode.providerTimeStrategy) {
    case "none":
      return dimensions;
    case "fixed":
      if (mode.providerTimeValue) {
        dimensions.Time = mode.providerTimeValue;
      }
      return dimensions;
    case "daily-yesterday-utc":
      dimensions.Time = buildUtcYesterdayDate();
      return dimensions;
    default:
      return dimensions;
  }
}

function buildUtcYesterdayDate() {
  const now = new Date();
  now.setUTCDate(now.getUTCDate() - 1);
  return now.toISOString().slice(0, 10);
}

function buildProviderFailureMessage(error: unknown) {
  if (typeof error === "object" && error !== null && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message) {
      return message;
    }
  }
  return "Remote imagery tiles failed repeatedly.";
}
