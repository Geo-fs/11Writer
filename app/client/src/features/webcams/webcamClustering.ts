import type { CameraEntity } from "../../types/entities";

export interface WebcamClusterBounds {
  minLatitude: number;
  maxLatitude: number;
  minLongitude: number;
  maxLongitude: number;
}

export interface WebcamCluster {
  clusterId: string;
  cameraCount: number;
  cameras: CameraEntity[];
  sourceIds: string[];
  primarySourceId: string;
  directImageCount: number;
  viewerOnlyCount: number;
  needsReviewCount: number;
  usableCount: number;
  missingCoordinateCount: number;
  uncertainOrientationCount: number;
  centerLatitude: number;
  centerLongitude: number;
  bounds: WebcamClusterBounds;
  representativeCameraIds: string[];
  facilityCodeHints: string[];
  referenceHintTexts: string[];
  referenceSummary: WebcamClusterReferenceSummary;
  dominantCapability: "direct-image" | "viewer-only" | "mixed" | "review-heavy";
  caveats: string[];
}

export interface WebcamClusterReferenceSummary {
  referenceHintCount: number;
  facilityHintCount: number;
  topReferenceHints: string[];
  topFacilityHints: string[];
  reviewedLinkCount: number;
  machineSuggestionCount: number;
  unlinkedHintCount: number;
  referenceReadyCount: number;
  needsReferenceReviewCount: number;
  referenceCaveats: string[];
  readinessLabel: "Reviewed links available" | "Machine suggestions only" | "Hints need review" | "No reference hints";
}

export interface WebcamClusterResult {
  clusters: WebcamCluster[];
  unclusteredCameras: CameraEntity[];
  missingCoordinateCameras: CameraEntity[];
  cellSizeDegrees: number;
}

export interface WebcamCoverageSummary {
  loadedCameraCount: number;
  clusterCount: number;
  directImageCount: number;
  viewerOnlyCount: number;
  reviewNeededCount: number;
  usableCount: number;
  sourceCount: number;
  largestCluster?: WebcamCluster | null;
  mostReviewHeavyCluster?: WebcamCluster | null;
  strongestDirectImageCluster?: WebcamCluster | null;
  referenceSummary: WebcamClusterReferenceSummary;
}

export function clusterWebcams(
  cameras: CameraEntity[],
  cameraHeightMeters?: number | null
): WebcamClusterResult {
  const cellSizeDegrees = deriveClusterCellSize(cameraHeightMeters);
  const positioned: CameraEntity[] = [];
  const missingCoordinateCameras: CameraEntity[] = [];

  for (const camera of cameras) {
    if (camera.position.kind === "unknown") {
      missingCoordinateCameras.push(camera);
      continue;
    }
    positioned.push(camera);
  }

  const grouped = new Map<string, CameraEntity[]>();
  for (const camera of positioned) {
    const key = gridKey(camera.latitude, camera.longitude, cellSizeDegrees);
    const list = grouped.get(key);
    if (list) {
      list.push(camera);
    } else {
      grouped.set(key, [camera]);
    }
  }

  const clusters: WebcamCluster[] = [];
  const unclusteredCameras: CameraEntity[] = [];

  for (const [key, group] of grouped) {
    if (group.length <= 1) {
      unclusteredCameras.push(group[0]);
      continue;
    }
    clusters.push(buildCluster(key, group));
  }

  clusters.sort((left, right) => right.cameraCount - left.cameraCount || left.clusterId.localeCompare(right.clusterId));
  unclusteredCameras.sort((left, right) => left.label.localeCompare(right.label));

  return {
    clusters,
    unclusteredCameras,
    missingCoordinateCameras,
    cellSizeDegrees
  };
}

export function summarizeWebcamCoverage(
  cameras: CameraEntity[],
  clusters: WebcamCluster[]
): WebcamCoverageSummary {
  const directImageCount = cameras.filter(hasDirectImage).length;
  const viewerOnlyCount = cameras.filter(isViewerOnly).length;
  const reviewNeededCount = cameras.filter((camera) => camera.review.status === "needs-review").length;
  const usableCount = cameras.filter(isUsableCamera).length;
  const sourceCount = new Set(cameras.map((camera) => camera.source)).size;
  const largestCluster = clusters[0] ?? null;
  const mostReviewHeavyCluster =
    [...clusters].sort((left, right) => reviewRatio(right) - reviewRatio(left) || right.needsReviewCount - left.needsReviewCount)[0] ?? null;
  const strongestDirectImageCluster =
    [...clusters].sort((left, right) => directRatio(right) - directRatio(left) || right.directImageCount - left.directImageCount)[0] ?? null;

  return {
    loadedCameraCount: cameras.length,
    clusterCount: clusters.length,
    directImageCount,
    viewerOnlyCount,
    reviewNeededCount,
    usableCount,
    sourceCount,
    largestCluster,
    mostReviewHeavyCluster,
    strongestDirectImageCluster,
    referenceSummary: summarizeReferenceContext(cameras)
  };
}

export function deriveClusterCellSize(cameraHeightMeters?: number | null) {
  if (cameraHeightMeters == null) {
    return 0.35;
  }
  if (cameraHeightMeters >= 20_000_000) {
    return 8;
  }
  if (cameraHeightMeters >= 5_000_000) {
    return 3;
  }
  if (cameraHeightMeters >= 1_500_000) {
    return 1;
  }
  if (cameraHeightMeters >= 500_000) {
    return 0.35;
  }
  return 0.12;
}

function buildCluster(key: string, cameras: CameraEntity[]): WebcamCluster {
  const sourceCounts = new Map<string, number>();
  let directImageCount = 0;
  let viewerOnlyCount = 0;
  let needsReviewCount = 0;
  let usableCount = 0;
  let uncertainOrientationCount = 0;
  let latitudeSum = 0;
  let longitudeSum = 0;
  const bounds: WebcamClusterBounds = {
    minLatitude: Number.POSITIVE_INFINITY,
    maxLatitude: Number.NEGATIVE_INFINITY,
    minLongitude: Number.POSITIVE_INFINITY,
    maxLongitude: Number.NEGATIVE_INFINITY
  };

  for (const camera of cameras) {
    sourceCounts.set(camera.source, (sourceCounts.get(camera.source) ?? 0) + 1);
    if (hasDirectImage(camera)) {
      directImageCount += 1;
    }
    if (isViewerOnly(camera)) {
      viewerOnlyCount += 1;
    }
    if (camera.review.status === "needs-review") {
      needsReviewCount += 1;
    }
    if (isUsableCamera(camera)) {
      usableCount += 1;
    }
    if (camera.orientation.kind !== "exact") {
      uncertainOrientationCount += 1;
    }
    latitudeSum += camera.latitude;
    longitudeSum += camera.longitude;
    bounds.minLatitude = Math.min(bounds.minLatitude, camera.latitude);
    bounds.maxLatitude = Math.max(bounds.maxLatitude, camera.latitude);
    bounds.minLongitude = Math.min(bounds.minLongitude, camera.longitude);
    bounds.maxLongitude = Math.max(bounds.maxLongitude, camera.longitude);
  }

  const sourceIds = [...sourceCounts.keys()].sort();
  const primarySourceId =
    [...sourceCounts.entries()].sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))[0]?.[0] ??
    cameras[0].source;
  const facilityCodeHints = uniqueStrings(cameras.map((camera) => camera.facilityCodeHint).filter(Boolean)).slice(0, 5);
  const referenceHintTexts = uniqueStrings(cameras.map((camera) => camera.referenceHintText).filter(Boolean)).slice(0, 5);
  const referenceSummary = summarizeReferenceContext(cameras);
  const caveats = buildClusterCaveats({
    cameraCount: cameras.length,
    directImageCount,
    viewerOnlyCount,
    needsReviewCount,
    uncertainOrientationCount
  });

  return {
    clusterId: `cluster:${key}:${sourceIds.join(",")}`,
    cameraCount: cameras.length,
    cameras: [...cameras].sort(compareClusterCameras),
    sourceIds,
    primarySourceId,
    directImageCount,
    viewerOnlyCount,
    needsReviewCount,
    usableCount,
    missingCoordinateCount: 0,
    uncertainOrientationCount,
    centerLatitude: latitudeSum / cameras.length,
    centerLongitude: longitudeSum / cameras.length,
    bounds,
    representativeCameraIds: [...cameras].sort(compareClusterCameras).slice(0, 5).map((camera) => camera.id),
    facilityCodeHints,
    referenceHintTexts,
    referenceSummary,
    dominantCapability: dominantCapability(directImageCount, viewerOnlyCount, needsReviewCount, cameras.length),
    caveats
  };
}

function gridKey(latitude: number, longitude: number, cellSizeDegrees: number) {
  const latIndex = Math.floor((latitude + 90) / cellSizeDegrees);
  const lonIndex = Math.floor((longitude + 180) / cellSizeDegrees);
  return `${cellSizeDegrees}:${latIndex}:${lonIndex}`;
}

function uniqueStrings(values: (string | null | undefined)[]) {
  return [...new Set(values.filter((value): value is string => Boolean(value)))];
}

function dominantCapability(
  directImageCount: number,
  viewerOnlyCount: number,
  needsReviewCount: number,
  cameraCount: number
): WebcamCluster["dominantCapability"] {
  if (needsReviewCount / cameraCount >= 0.5) {
    return "review-heavy";
  }
  if (directImageCount > 0 && viewerOnlyCount > 0) {
    return "mixed";
  }
  if (directImageCount > 0) {
    return "direct-image";
  }
  return "viewer-only";
}

function buildClusterCaveats(input: {
  cameraCount: number;
  directImageCount: number;
  viewerOnlyCount: number;
  needsReviewCount: number;
  uncertainOrientationCount: number;
}) {
  const caveats = ["Cluster center is approximate and for display only."];
  if (input.viewerOnlyCount > 0 && input.directImageCount > 0) {
    caveats.push("Mixed direct-image and viewer-only cameras.");
  } else if (input.viewerOnlyCount > 0) {
    caveats.push("Contains viewer-only cameras that do not provide direct frames.");
  }
  if (input.needsReviewCount > 0) {
    caveats.push("Contains review-needed cameras.");
  }
  if (input.uncertainOrientationCount > 0) {
    caveats.push("Contains cameras with uncertain orientation.");
  }
  return caveats;
}

function compareClusterCameras(left: CameraEntity, right: CameraEntity) {
  return (
    Number(hasDirectImage(right)) - Number(hasDirectImage(left)) ||
    Number(isUsableCamera(right)) - Number(isUsableCamera(left)) ||
    left.label.localeCompare(right.label)
  );
}

function reviewRatio(cluster: WebcamCluster) {
  return cluster.cameraCount === 0 ? 0 : cluster.needsReviewCount / cluster.cameraCount;
}

function directRatio(cluster: WebcamCluster) {
  return cluster.cameraCount === 0 ? 0 : cluster.directImageCount / cluster.cameraCount;
}

export function hasDirectImage(camera: CameraEntity) {
  return Boolean(camera.frame.imageUrl && camera.frame.status !== "viewer-page-only");
}

export function isViewerOnly(camera: CameraEntity) {
  return camera.frame.status === "viewer-page-only" || (!camera.frame.imageUrl && Boolean(camera.frame.viewerUrl));
}

export function isUsableCamera(camera: CameraEntity) {
  if (camera.review.status === "blocked" || camera.healthState === "blocked") {
    return false;
  }
  return camera.frame.status === "live" || camera.frame.status === "viewer-page-only";
}

export function summarizeReferenceContext(cameras: CameraEntity[]): WebcamClusterReferenceSummary {
  const referenceHints = countedStrings(cameras.map((camera) => camera.referenceHintText));
  const facilityHints = countedStrings(cameras.map((camera) => camera.facilityCodeHint));
  let reviewedLinkCount = 0;
  let machineSuggestionCount = 0;
  let unlinkedHintCount = 0;
  let referenceReadyCount = 0;
  let needsReferenceReviewCount = 0;

  for (const camera of cameras) {
    const state = getCameraReferenceState(camera);
    if (state.kind !== "none") {
      referenceReadyCount += 1;
    }
    if (state.kind === "reviewed") {
      reviewedLinkCount += 1;
      continue;
    }
    if (state.kind === "machine") {
      machineSuggestionCount += 1;
      needsReferenceReviewCount += 1;
      continue;
    }
    if (state.kind === "hint") {
      unlinkedHintCount += 1;
      needsReferenceReviewCount += 1;
    }
  }

  const referenceCaveats = buildReferenceCaveats({
    cameraCount: cameras.length,
    reviewedLinkCount,
    machineSuggestionCount,
    unlinkedHintCount
  });

  return {
    referenceHintCount: referenceHints.length,
    facilityHintCount: facilityHints.length,
    topReferenceHints: topCountedStrings(referenceHints),
    topFacilityHints: topCountedStrings(facilityHints),
    reviewedLinkCount,
    machineSuggestionCount,
    unlinkedHintCount,
    referenceReadyCount,
    needsReferenceReviewCount,
    referenceCaveats,
    readinessLabel: describeReferenceReadinessLabel({
      reviewedLinkCount,
      machineSuggestionCount,
      unlinkedHintCount
    })
  };
}

export function getCameraReferenceState(camera: CameraEntity) {
  if (camera.nearestReferenceRefId) {
    return {
      kind: "reviewed",
      label: "Reviewed link",
      detail: camera.nearestReferenceRefId
    } as const;
  }
  if (camera.referenceLinkStatus && camera.referenceLinkStatus !== "hinted") {
    return {
      kind: "machine",
      label: "Machine suggestion",
      detail:
        camera.linkCandidateCount != null
          ? `${camera.referenceLinkStatus} (${camera.linkCandidateCount} candidates)`
          : camera.referenceLinkStatus
    } as const;
  }
  if (camera.referenceHintText || camera.facilityCodeHint || camera.referenceLinkStatus === "hinted") {
    return {
      kind: "hint",
      label: "Hint only",
      detail: camera.referenceHintText ?? camera.facilityCodeHint ?? "Connector hint available"
    } as const;
  }
  return {
    kind: "none",
    label: "No reference context",
    detail: "No reviewed link, machine suggestion, or connector hint."
  } as const;
}

function countedStrings(values: (string | null | undefined)[]) {
  const counts = new Map<string, number>();
  for (const value of values) {
    if (!value) {
      continue;
    }
    counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  return [...counts.entries()].sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]));
}

function topCountedStrings(entries: Array<[string, number]>) {
  return entries.slice(0, 5).map(([value, count]) => (count > 1 ? `${value} (${count})` : value));
}

function buildReferenceCaveats(input: {
  cameraCount: number;
  reviewedLinkCount: number;
  machineSuggestionCount: number;
  unlinkedHintCount: number;
}) {
  const caveats = ["Reference hints are contextual aids, not canonical matches."];
  if (input.reviewedLinkCount > 0 && input.reviewedLinkCount < input.cameraCount) {
    caveats.push("Reviewed links cover only part of this cluster.");
  }
  if (input.machineSuggestionCount > 0) {
    caveats.push("Machine suggestions are unreviewed and need confirmation.");
  }
  if (input.unlinkedHintCount > 0) {
    caveats.push("Connector-provided hints still need canonical review.");
  }
  if (
    input.reviewedLinkCount === 0 &&
    input.machineSuggestionCount === 0 &&
    input.unlinkedHintCount === 0
  ) {
    caveats.push("No reference context is available for this cluster yet.");
  }
  return caveats;
}

function describeReferenceReadinessLabel(input: {
  reviewedLinkCount: number;
  machineSuggestionCount: number;
  unlinkedHintCount: number;
}): WebcamClusterReferenceSummary["readinessLabel"] {
  if (input.reviewedLinkCount > 0) {
    return "Reviewed links available";
  }
  if (input.machineSuggestionCount > 0) {
    return "Machine suggestions only";
  }
  if (input.unlinkedHintCount > 0) {
    return "Hints need review";
  }
  return "No reference hints";
}
