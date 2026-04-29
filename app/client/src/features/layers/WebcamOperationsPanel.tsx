import {
  useCameraReviewQueueQuery,
  useCameraSourceInventoryQuery,
  useCameraSourcesQuery,
  useSourceStatusQuery
} from "../../lib/queries";
import { useAppStore } from "../../lib/store";
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
  const webcamFilters = useAppStore((state) => state.webcamFilters);
  const setWebcamFilters = useAppStore((state) => state.setWebcamFilters);
  const resetWebcamFilters = useAppStore((state) => state.resetWebcamFilters);
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
  const inventorySources = [...(inventoryQuery.data?.sources ?? [])].sort(compareInventorySources);
  const reviewItems = reviewQueueQuery.data?.items ?? [];

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
        <span>{visibleSummary.usable} usable</span>
        <span>{visibleSummary.directImage} direct-image</span>
        <span>{visibleSummary.viewerOnly} viewer-only</span>
        <span>{visibleSummary.needsReview} needs review</span>
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

function hasDirectImage(camera: CameraEntity) {
  return Boolean(camera.frame.imageUrl && camera.frame.status !== "viewer-page-only");
}

function isViewerOnly(camera: CameraEntity) {
  return camera.frame.status === "viewer-page-only" || (!camera.frame.imageUrl && Boolean(camera.frame.viewerUrl));
}

function isUsableCamera(camera: CameraEntity) {
  if (camera.review.status === "blocked" || camera.healthState === "blocked") {
    return false;
  }
  return camera.frame.status === "live" || camera.frame.status === "viewer-page-only";
}
