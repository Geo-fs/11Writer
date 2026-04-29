import {
  useCameraReviewQueueQuery,
  useCameraSourceInventoryQuery,
  useCameraSourcesQuery,
  useSourceStatusQuery
} from "../../lib/queries";
import { useAppStore } from "../../lib/store";
import { CaveatBlock, MetricRow, StatusBadge } from "../../components/ui";
import {
  getCameraReferenceState,
  hasDirectImage,
  isUsableCamera,
  isViewerOnly,
  summarizeWebcamCoverage,
  type WebcamCluster
} from "../webcams/webcamClustering";
import type {
  CameraSourceInventoryEntry,
  CameraSourceRegistryEntry,
  ReviewQueueItem,
  SourceStatus
} from "../../types/api";
import type { CameraEntity } from "../../types/entities";

export function WebcamOperationsPanel() {
  const layers = useAppStore((state) => state.layers);
  const cameraEntities = useAppStore((state) => state.cameraEntities);
  const webcamClusters = useAppStore((state) => state.webcamClusters);
  const webcamFilters = useAppStore((state) => state.webcamFilters);
  const selectedWebcamClusterId = useAppStore((state) => state.selectedWebcamClusterId);
  const selectedEntityId = useAppStore((state) => state.selectedEntityId);
  const setWebcamFilters = useAppStore((state) => state.setWebcamFilters);
  const resetWebcamFilters = useAppStore((state) => state.resetWebcamFilters);
  const setSelectedWebcamClusterId = useAppStore((state) => state.setSelectedWebcamClusterId);
  const setSelectedEntityId = useAppStore((state) => state.setSelectedEntityId);
  const camerasEnabled = layers.find((layer) => layer.key === "cameras")?.enabled ?? false;
  const inventoryQuery = useCameraSourceInventoryQuery();
  const cameraSourcesQuery = useCameraSourcesQuery();
  const sourceStatusQuery = useSourceStatusQuery();
  const reviewQueueQuery = useCameraReviewQueueQuery(20);

  const sourceMap = new Map(
    (cameraSourcesQuery.data?.sources ?? []).map((source) => [source.key, source] as const)
  );
  const statusMap = new Map(
    (sourceStatusQuery.data?.sources ?? []).map((source) => [source.name, source] as const)
  );
  const visibleSummary = summarizeVisibleCameras(cameraEntities);
  const coverageSummary = summarizeWebcamCoverage(cameraEntities, webcamClusters);
  const inventorySources = [...(inventoryQuery.data?.sources ?? [])].sort(compareInventorySources);
  const reviewItems = reviewQueueQuery.data?.items ?? [];
  const selectedCluster =
    webcamClusters.find((cluster) => toEntityClusterId(cluster) === selectedWebcamClusterId) ??
    (webcamClusters.length === 1 ? webcamClusters[0] : null);

  return (
    <div className="panel__section" data-testid="webcam-operations-panel">
      <p className="panel__eyebrow">Webcam Operations</p>
      {!camerasEnabled ? (
        <div className="empty-state compact" data-testid="webcam-panel-disabled">
          <p>Camera layer disabled.</p>
          <span>Enable Cameras in Layer Controls to inspect live webcam source yield and camera subsets.</span>
        </div>
      ) : null}

      <div className="data-card data-card--compact webcam-summary-card" data-testid="webcam-visible-summary">
        <strong>Visible Webcam Subset</strong>
        <span>{visibleSummary.total} cameras in current viewport/query result</span>
        <span>{coverageSummary.clusterCount} clusters</span>
        <span>{visibleSummary.usable} usable</span>
        <span>{visibleSummary.directImage} direct-image</span>
        <span>{visibleSummary.viewerOnly} viewer-only</span>
        <span>{visibleSummary.needsReview} needs review</span>
        <span>{coverageSummary.sourceCount} sources represented</span>
        {coverageSummary.largestCluster ? (
          <span data-testid="webcam-largest-cluster">
            Largest cluster {coverageSummary.largestCluster.cameraCount} cameras
          </span>
        ) : null}
        {coverageSummary.mostReviewHeavyCluster ? (
          <span>Most review-heavy cluster {coverageSummary.mostReviewHeavyCluster.needsReviewCount} review-needed</span>
        ) : null}
        {coverageSummary.strongestDirectImageCluster ? (
          <span>Strongest direct-image group {coverageSummary.strongestDirectImageCluster.directImageCount} direct-image</span>
        ) : null}
      </div>

      <div className="data-card" data-testid="webcam-filter-panel">
        <strong>Camera Filters</strong>
        <div className="field-grid webcam-filter-grid">
          <label className="field-row">
            <span>Webcam Source</span>
            <select
              className="panel__select"
              value={webcamFilters.sourceId}
              onChange={(event) => setWebcamFilters({ sourceId: event.currentTarget.value })}
            >
              <option value="">All webcam sources</option>
              {inventorySources.map((source) => (
                <option key={source.key} value={source.key}>
                  {source.key}
                </option>
              ))}
            </select>
          </label>
          <label className="toggle-row">
            <span>Direct-image only</span>
            <input
              data-testid="webcam-filter-direct-image"
              type="checkbox"
              checked={webcamFilters.directImageOnly}
              onChange={(event) => setWebcamFilters({ directImageOnly: event.currentTarget.checked })}
            />
          </label>
          <label className="toggle-row">
            <span>Viewer-only</span>
            <input
              data-testid="webcam-filter-viewer-only"
              type="checkbox"
              checked={webcamFilters.viewerOnly}
              onChange={(event) => setWebcamFilters({ viewerOnly: event.currentTarget.checked })}
            />
          </label>
          <label className="toggle-row">
            <span>Needs review</span>
            <input
              data-testid="webcam-filter-needs-review"
              type="checkbox"
              checked={webcamFilters.needsReview}
              onChange={(event) => setWebcamFilters({ needsReview: event.currentTarget.checked })}
            />
          </label>
          <label className="toggle-row">
            <span>Usable only</span>
            <input
              data-testid="webcam-filter-usable-only"
              type="checkbox"
              checked={webcamFilters.usableOnly}
              onChange={(event) => setWebcamFilters({ usableOnly: event.currentTarget.checked })}
            />
          </label>
          <label className="toggle-row">
            <span>Exact coordinates only</span>
            <input
              data-testid="webcam-filter-exact-coordinates"
              type="checkbox"
              checked={webcamFilters.exactCoordinatesOnly}
              onChange={(event) => setWebcamFilters({ exactCoordinatesOnly: event.currentTarget.checked })}
            />
          </label>
          <label className="toggle-row">
            <span>Uncertain orientation</span>
            <input
              data-testid="webcam-filter-uncertain-orientation"
              type="checkbox"
              checked={webcamFilters.uncertainOrientation}
              onChange={(event) => setWebcamFilters({ uncertainOrientation: event.currentTarget.checked })}
            />
          </label>
          <label className="toggle-row">
            <span>Missing coordinates</span>
            <input
              data-testid="webcam-filter-missing-coordinates"
              type="checkbox"
              checked={webcamFilters.missingCoordinates}
              onChange={(event) => setWebcamFilters({ missingCoordinates: event.currentTarget.checked })}
            />
          </label>
        </div>
        <button type="button" className="ghost-button" onClick={() => resetWebcamFilters()}>
          Reset Webcam Filters
        </button>
      </div>

      <div className="stack" data-testid="webcam-source-operations-list">
        {inventorySources.map((source) => (
          <SourceOperationsCard
            key={source.key}
            source={source}
            runtime={sourceMap.get(source.key)}
            status={statusMap.get(source.key)}
          />
        ))}
      </div>

      <div className="data-card" data-testid="webcam-cluster-list-panel">
        <strong>Webcam Clusters</strong>
        <span>
          {webcamClusters.length} grouped camera areas from the currently loaded and filtered webcam set
        </span>
        {webcamClusters.length > 0 ? (
          <div className="stack" data-testid="webcam-cluster-list">
            {webcamClusters.slice(0, 8).map((cluster) => (
              <button
                key={cluster.clusterId}
                type="button"
                className="ghost-button webcam-cluster-button"
                data-testid="webcam-cluster-item"
                onClick={() => setSelectedWebcamClusterId(toEntityClusterId(cluster))}
              >
                {cluster.primarySourceId} | {cluster.cameraCount} cameras | {cluster.directImageCount} direct-image | {cluster.viewerOnlyCount} viewer-only
              </button>
            ))}
          </div>
        ) : (
          <div className="empty-state compact">
            <p>No multi-camera clusters in the current filtered set.</p>
            <span>Single cameras still render individually and remain selectable on the globe.</span>
          </div>
        )}
      </div>

      {selectedCluster ? (
        <ClusterDetailPanel
          cluster={selectedCluster}
          selectedEntityId={selectedEntityId}
          onSelectCamera={(cameraId) => {
            setSelectedEntityId(cameraId);
          }}
          onShowViewerOnly={() =>
            setWebcamFilters({
              sourceId: selectedCluster.primarySourceId,
              viewerOnly: true,
              directImageOnly: false,
              needsReview: false
            })
          }
          onShowNeedsReview={() =>
            setWebcamFilters({
              sourceId: selectedCluster.primarySourceId,
              needsReview: true,
              viewerOnly: false,
              directImageOnly: false
            })
          }
          onSelectFirstDirectImage={() => {
            const firstDirectImage = selectedCluster.cameras.find((camera) => hasDirectImage(camera));
            if (firstDirectImage) {
              setSelectedEntityId(firstDirectImage.id);
            }
          }}
        />
      ) : null}

      <div className="data-card" data-testid="webcam-review-queue-panel">
        <strong>Webcam Review Queue</strong>
        <span>
          {reviewQueueQuery.data?.count ?? 0} items surfaced from the current persisted webcam review queue
        </span>
        {reviewItems.length > 0 ? (
          <div className="stack" data-testid="webcam-review-queue-list">
            {reviewItems.slice(0, 8).map((item) => (
              <ReviewQueueCard key={item.queueId} item={item} />
            ))}
          </div>
        ) : (
          <div className="empty-state compact">
            <p>No webcam review items.</p>
            <span>Viewer-only and uncertain metadata items will appear here when sources require follow-up.</span>
          </div>
        )}
      </div>
    </div>
  );
}

function ClusterDetailPanel({
  cluster,
  selectedEntityId,
  onSelectCamera,
  onShowViewerOnly,
  onShowNeedsReview,
  onSelectFirstDirectImage
}: {
  cluster: WebcamCluster;
  selectedEntityId: string | null;
  onSelectCamera: (cameraId: string) => void;
  onShowViewerOnly: () => void;
  onShowNeedsReview: () => void;
  onSelectFirstDirectImage: () => void;
}) {
  const sourceBreakdown = cluster.sourceIds.map((sourceId) => {
    const count = cluster.cameras.filter((camera) => camera.source === sourceId).length;
    return `${sourceId} (${count})`;
  });

  return (
    <div className="data-card webcam-cluster-detail" data-testid="webcam-cluster-detail">
      <strong>Selected Cluster</strong>
      <span>{cluster.cameraCount} cameras</span>
      <span>Primary source {cluster.primarySourceId}</span>
      <span>{cluster.directImageCount} direct-image | {cluster.viewerOnlyCount} viewer-only</span>
      <span>{cluster.usableCount} usable | {cluster.needsReviewCount} needs review</span>
      <span>
        {cluster.missingCoordinateCount} missing coordinates | {cluster.uncertainOrientationCount} uncertain orientation
      </span>
      <span>Sources {sourceBreakdown.join(" | ")}</span>
      <span>
        Approximate center {cluster.centerLatitude.toFixed(3)}, {cluster.centerLongitude.toFixed(3)}
      </span>
      {cluster.facilityCodeHints.length > 0 ? (
        <span>Facility hints {cluster.facilityCodeHints.join(", ")}</span>
      ) : null}
      {cluster.referenceHintTexts.length > 0 ? (
        <span>Reference hints {cluster.referenceHintTexts.join(" | ")}</span>
      ) : null}
      <div className="data-card data-card--compact" data-testid="webcam-cluster-reference-context">
        <strong>Reference Context</strong>
        <div className="stack">
          <StatusBadge tone={referenceTone(cluster.referenceSummary.readinessLabel)}>
            {cluster.referenceSummary.readinessLabel}
          </StatusBadge>
          <MetricRow
            label="Reviewed"
            value={cluster.referenceSummary.reviewedLinkCount.toLocaleString()}
          />
          <MetricRow
            label="Machine suggestions"
            value={cluster.referenceSummary.machineSuggestionCount.toLocaleString()}
          />
          <MetricRow
            label="Hint-only"
            value={cluster.referenceSummary.unlinkedHintCount.toLocaleString()}
          />
          <MetricRow
            label="Reference-ready"
            value={cluster.referenceSummary.referenceReadyCount.toLocaleString()}
          />
          <MetricRow
            label="Needs reference review"
            value={cluster.referenceSummary.needsReferenceReviewCount.toLocaleString()}
          />
          <MetricRow
            label="Top reference hints"
            value={cluster.referenceSummary.topReferenceHints.join(" | ") || "None"}
          />
          <MetricRow
            label="Top facility hints"
            value={cluster.referenceSummary.topFacilityHints.join(" | ") || "None"}
          />
        </div>
        <CaveatBlock heading="Reference caveat" tone="evidence" compact>
          {cluster.referenceSummary.referenceCaveats.join(" ")}
        </CaveatBlock>
      </div>
      <div className="stack stack--actions webcam-cluster-actions">
        <button type="button" className="ghost-button" onClick={onSelectFirstDirectImage}>
          Select First Direct-Image Camera
        </button>
        <button type="button" className="ghost-button" onClick={onShowViewerOnly}>
          Show Viewer-Only Cameras
        </button>
        <button type="button" className="ghost-button" onClick={onShowNeedsReview}>
          Show Review-Needed Cameras
        </button>
      </div>
      <div className="stack" data-testid="webcam-cluster-camera-list">
        {cluster.cameras.slice(0, 10).map((camera) => (
          <button
            key={camera.id}
            type="button"
            className="ghost-button webcam-cluster-camera-row"
            data-testid="webcam-cluster-camera-row"
            onClick={() => onSelectCamera(camera.id)}
          >
            {camera.label} | {camera.source} | {hasDirectImage(camera) ? "Direct-image" : isViewerOnly(camera) ? "Viewer-only" : "No frame"} | {isUsableCamera(camera) ? "Usable" : camera.review.status}
            {` | ${getCameraReferenceState(camera).label}`}
            {camera.referenceHintText ? ` | hint=${camera.referenceHintText}` : ""}
            {camera.facilityCodeHint ? ` | facility=${camera.facilityCodeHint}` : ""}
            {selectedEntityId === camera.id ? " | selected" : ""}
          </button>
        ))}
      </div>
      <div className="stack">
        {cluster.caveats.map((caveat) => (
          <span key={caveat}>{caveat}</span>
        ))}
      </div>
    </div>
  );
}

function SourceOperationsCard({
  source,
  runtime,
  status
}: {
  source: CameraSourceInventoryEntry;
  runtime?: CameraSourceRegistryEntry;
  status?: SourceStatus;
}) {
  const readiness = describeReadiness(source, runtime, status);
  const stateDetail = status?.blockedReason ?? status?.degradedReason ?? source.blockedReason ?? source.lastCatalogImportDetail;

  return (
    <div
      className="data-card data-card--compact webcam-source-card"
      data-testid={`webcam-source-card-${source.key}`}
    >
      <strong>{source.sourceName}</strong>
      <span>Source ID {source.key}</span>
      <span className={`webcam-readiness webcam-readiness--${readiness.tone}`}>{readiness.label}</span>
      <span>{describeSourceType(source)}</span>
      <span>
        {source.authentication === "none"
          ? "No credentials required"
          : source.credentialsConfigured
            ? "Credentials configured"
            : "Credentials missing"}
      </span>
      <span>
        {source.lastImportOutcome
          ? `Last import outcome ${source.lastImportOutcome}`
          : source.lastCatalogImportStatus
            ? `Last catalog import ${source.lastCatalogImportStatus}`
            : "No measured import yet"}
      </span>
      {source.importReadiness !== "inventory-only" ? (
        <>
          <span>Discovered {formatCount(source.discoveredCameraCount)}</span>
          <span>Usable {formatCount(source.usableCameraCount)}</span>
          <span>Direct-image {formatCount(source.directImageCameraCount)}</span>
          <span>Viewer-only {formatCount(source.viewerOnlyCameraCount)}</span>
          <span>Missing coordinates {formatCount(source.missingCoordinateCameraCount)}</span>
          <span>Uncertain orientation {formatCount(source.uncertainOrientationCameraCount)}</span>
          <span>Review queue {formatCount(source.reviewQueueCount)}</span>
        </>
      ) : (
        <>
          <span>Page structure {source.pageStructure ?? "unknown"}</span>
          <span>Likely camera count {formatCount(source.likelyCameraCount)}</span>
          <span>Compliance risk {source.complianceRisk ?? "unknown"}</span>
          <span>Extraction feasibility {source.extractionFeasibility ?? "unknown"}</span>
          <span>Viewer posture {source.providesDirectImage ? "mixed/direct possible" : "viewer-only / candidate"}</span>
        </>
      )}
      {runtime?.cadenceSeconds != null ? (
        <span>
          Cadence {runtime.cadenceSeconds}s{runtime.cadenceReason ? ` (${runtime.cadenceReason})` : ""}
        </span>
      ) : null}
      {status?.backoffUntil ? <span>Backoff until {formatTimestamp(status.backoffUntil)}</span> : null}
      {status?.lastCompletedAt ? <span>Last completed {formatTimestamp(status.lastCompletedAt)}</span> : null}
      {stateDetail ? <span>{stateDetail}</span> : null}
    </div>
  );
}

function ReviewQueueCard({ item }: { item: ReviewQueueItem }) {
  const reviewReason = item.issues.map((issue) => issue.reason).join(" | ");
  return (
    <div className="data-card data-card--compact webcam-review-card" data-testid="webcam-review-item">
      <strong>{item.camera.label}</strong>
      <span>Source {item.sourceKey}</span>
      <span>{item.priority} priority</span>
      <span>{isViewerOnly(item.camera) ? "Viewer-only" : hasDirectImage(item.camera) ? "Direct-image" : "No frame path"}</span>
      <span>{reviewReason || item.camera.review.reason || "Needs review"}</span>
      <span>
        Position {item.camera.position.kind} | Orientation {item.camera.orientation.kind}
      </span>
      {item.camera.referenceHintText ? <span>Reference hint: {item.camera.referenceHintText}</span> : null}
      {item.camera.facilityCodeHint ? <span>Facility hint: {item.camera.facilityCodeHint}</span> : null}
    </div>
  );
}

function compareInventorySources(left: CameraSourceInventoryEntry, right: CameraSourceInventoryEntry) {
  const order = new Map([
    ["validated", 0],
    ["actively-importing", 1],
    ["approved-unvalidated", 2],
    ["low-yield", 3],
    ["poor-quality", 4],
    ["inventory-only", 5]
  ]);
  return (order.get(left.importReadiness ?? "inventory-only") ?? 9) - (order.get(right.importReadiness ?? "inventory-only") ?? 9) || left.key.localeCompare(right.key);
}

function summarizeVisibleCameras(cameras: CameraEntity[]) {
  return {
    total: cameras.length,
    usable: cameras.filter(isUsableCamera).length,
    directImage: cameras.filter(hasDirectImage).length,
    viewerOnly: cameras.filter(isViewerOnly).length,
    needsReview: cameras.filter((camera) => camera.review.status === "needs-review").length
  };
}

function toEntityClusterId(cluster: WebcamCluster) {
  return `camera-cluster:${cluster.clusterId.replace("cluster:", "")}`;
}

function describeReadiness(
  source: CameraSourceInventoryEntry,
  runtime?: CameraSourceRegistryEntry,
  status?: SourceStatus
) {
  if (source.onboardingState === "candidate") {
    return { label: "Candidate only", tone: "candidate" } as const;
  }
  if ((status?.state === "credentials-missing") || (source.authentication !== "none" && !source.credentialsConfigured)) {
    return { label: "Credential blocked", tone: "blocked" } as const;
  }
  if (source.onboardingState === "blocked") {
    return { label: "Review gated", tone: "candidate" } as const;
  }
  if (source.importReadiness === "validated") {
    return { label: "Validated", tone: "validated" } as const;
  }
  if (source.importReadiness === "low-yield") {
    return { label: "Low yield", tone: "warning" } as const;
  }
  if (source.importReadiness === "poor-quality") {
    return { label: "Poor quality", tone: "warning" } as const;
  }
  if (source.importReadiness === "actively-importing" || runtime?.status === "healthy" && status?.lastAttemptAt && !status?.lastCompletedAt) {
    return { label: "Actively importing", tone: "active" } as const;
  }
  return { label: "Approved but unvalidated", tone: "pending" } as const;
}

function describeSourceType(source: CameraSourceInventoryEntry) {
  return `${source.sourceType} via ${source.accessMethod}`;
}

function formatCount(value?: number | null) {
  return value == null ? "Unknown" : value.toLocaleString();
}

function formatTimestamp(value?: string | null) {
  return value ? new Date(value).toLocaleString() : "Unknown";
}

function referenceTone(label: WebcamCluster["referenceSummary"]["readinessLabel"]) {
  switch (label) {
    case "Reviewed links available":
      return "success" as const;
    case "Machine suggestions only":
      return "info" as const;
    case "Hints need review":
      return "warning" as const;
    default:
      return "neutral" as const;
  }
}
