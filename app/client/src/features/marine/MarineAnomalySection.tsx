import { useMemo, useState } from "react";
import {
  useMarineChokepointSummaryQuery,
  useMarineVesselSummaryQuery,
  useMarineVesselsQuery,
  useMarineViewportSummaryQuery
} from "../../lib/queries";
import { useAppStore } from "../../lib/store";
import type { MarineChokepointSliceSummary } from "../../types/api";
import { buildActiveImageryContextFromHud } from "../../lib/imageryContext";
import { ImageryContextBadge } from "../imagery/ImageryContextBadge";
import { MarineAnomalyPanel } from "./MarineAnomalyComponents";

type SliceFilter = "all" | "medium+" | "high";
type SliceSort = "priority" | "score";

export function MarineAnomalySection() {
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const hud = useAppStore((state) => state.hud);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const [sliceFilter, setSliceFilter] = useState<SliceFilter>("all");
  const [sliceSort, setSliceSort] = useState<SliceSort>("priority");
  const vesselsQuery = useMarineVesselsQuery();
  const selectedMarineVesselId =
    selectedEntity?.type === "marine-vessel"
      ? selectedEntity.id
      : vesselsQuery.data?.vessels?.[0]?.id ?? null;
  const vesselSummaryQuery = useMarineVesselSummaryQuery(selectedMarineVesselId);
  const center = Number.isFinite(hud.latitude) && Number.isFinite(hud.longitude)
    ? { lat: hud.latitude, lon: hud.longitude }
    : null;
  const viewportSummaryQuery = useMarineViewportSummaryQuery(center);
  const chokepointSummaryQuery = useMarineChokepointSummaryQuery(center);

  const sortedSlices = useMemo(() => {
    const slices = [...(chokepointSummaryQuery.data?.slices ?? [])];
    const filtered = slices.filter((slice) => {
      if (sliceFilter === "high") return slice.anomaly.level === "high";
      if (sliceFilter === "medium+") return slice.anomaly.level !== "low";
      return true;
    });
    filtered.sort((a, b) => {
      if (sliceSort === "priority") {
        const aRank = a.anomaly.priorityRank ?? Number.MAX_SAFE_INTEGER;
        const bRank = b.anomaly.priorityRank ?? Number.MAX_SAFE_INTEGER;
        if (aRank !== bRank) return aRank - bRank;
      }
      return b.anomaly.score - a.anomaly.score;
    });
    return filtered;
  }, [chokepointSummaryQuery.data?.slices, sliceFilter, sliceSort]);

  const attentionItems = useMemo(() => {
    const items: Array<{ type: string; label: string; level: string; score: number; reason: string; caveat: string }> = [];
    if (vesselSummaryQuery.data) {
      items.push({
        type: "vessel",
        label: vesselSummaryQuery.data.anomaly.displayLabel,
        level: vesselSummaryQuery.data.anomaly.level,
        score: vesselSummaryQuery.data.anomaly.score,
        reason: vesselSummaryQuery.data.anomaly.reasons[0] ?? "No reason stated.",
        caveat: vesselSummaryQuery.data.anomaly.caveats[0] ?? ""
      });
    }
    if (viewportSummaryQuery.data) {
      items.push({
        type: "viewport",
        label: viewportSummaryQuery.data.anomaly.displayLabel,
        level: viewportSummaryQuery.data.anomaly.level,
        score: viewportSummaryQuery.data.anomaly.score,
        reason: viewportSummaryQuery.data.anomaly.reasons[0] ?? "No reason stated.",
        caveat: viewportSummaryQuery.data.anomaly.caveats[0] ?? ""
      });
    }
    const topSlice = sortedSlices[0];
    if (topSlice) {
      items.push({
        type: "chokepoint",
        label: topSlice.anomaly.displayLabel,
        level: topSlice.anomaly.level,
        score: topSlice.anomaly.score,
        reason: topSlice.anomaly.reasons[0] ?? "No reason stated.",
        caveat: topSlice.anomaly.caveats[0] ?? ""
      });
    }
    return items.sort((a, b) => b.score - a.score);
  }, [sortedSlices, vesselSummaryQuery.data, viewportSummaryQuery.data]);

  const anyLoading =
    vesselsQuery.isLoading ||
    vesselSummaryQuery.isLoading ||
    viewportSummaryQuery.isLoading ||
    chokepointSummaryQuery.isLoading;
  const imageryContext = buildActiveImageryContextFromHud(hud);

  return (
    <div className="panel__section" data-testid="marine-anomaly-section">
      <p className="panel__eyebrow">Marine Attention Priority</p>
      <div className="empty-state compact">
        <p>Attention priority is a review signal, not proof of intent.</p>
      </div>
      <ImageryContextBadge context={imageryContext} isReplayContext={selectedReplayIndex != null} />
      {anyLoading ? <span className="marine-anomaly-muted">Loading marine anomaly summaries.</span> : null}
      {vesselsQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-vessels-error">
          <p>Marine vessel list unavailable.</p>
          <span>Attention ranking is limited until marine vessel data is available.</span>
        </div>
      ) : null}

      {selectedMarineVesselId == null && !vesselsQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-no-selected-vessel">
          <p>No selected vessel.</p>
          <span>Select a marine vessel to inspect attention priority.</span>
        </div>
      ) : null}

      {vesselSummaryQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-vessel-loading">
          <p>Loading selected vessel summary.</p>
        </div>
      ) : null}

      {vesselSummaryQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-vessel-error">
          <p>Selected vessel summary unavailable.</p>
          <span>No notable anomaly in this window can be evaluated right now.</span>
        </div>
      ) : null}

      {vesselSummaryQuery.data ? (
        <MarineAnomalyPanel
          title={`Selected Vessel: ${vesselSummaryQuery.data.latestObserved?.label ?? vesselSummaryQuery.data.vesselId}`}
          anomaly={vesselSummaryQuery.data.anomaly}
          note="Notable activity from vessel summary window."
        />
      ) : (
        <div className="empty-state compact" data-testid="marine-vessel-low-state">
          <p>No selected vessel anomaly summary.</p>
          <span>Low or unavailable marine vessel priority for this context.</span>
        </div>
      )}

      {viewportSummaryQuery.data ? (
        <MarineAnomalyPanel
          title="Viewport Notable Activity"
          anomaly={viewportSummaryQuery.data.anomaly}
          note="Does this time/area window deserve attention?"
        />
      ) : viewportSummaryQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-viewport-loading">
          <p>Loading viewport summary.</p>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-viewport-error">
          <p>Viewport summary unavailable.</p>
          <span>No notable anomaly in this window can be evaluated from current data.</span>
        </div>
      )}

      {chokepointSummaryQuery.data ? (
        <div className="data-card marine-anomaly-panel" data-testid="marine-chokepoint-priority">
          <strong>Chokepoint Slice Prioritization</strong>
          <div className="marine-anomaly-controls">
            <label data-testid="marine-chokepoint-filter">
              <span>Filter</span>
              <select value={sliceFilter} onChange={(e) => setSliceFilter(e.currentTarget.value as SliceFilter)}>
                <option value="all">all</option>
                <option value="medium+">medium+</option>
                <option value="high">high only</option>
              </select>
            </label>
            <label data-testid="marine-chokepoint-sort">
              <span>Sort</span>
              <select value={sliceSort} onChange={(e) => setSliceSort(e.currentTarget.value as SliceSort)}>
                <option value="priority">priority rank</option>
                <option value="score">score</option>
              </select>
            </label>
          </div>
          <div className="stack" data-testid="marine-chokepoint-slice-list">
            {sortedSlices.map((slice) => (
              <SliceCard key={`${slice.sliceStartAt}-${slice.sliceEndAt}`} slice={slice} />
            ))}
            {sortedSlices.length === 0 ? (
              <div className="empty-state compact" data-testid="marine-chokepoint-empty">
                <p>No chokepoint slices match this filter.</p>
              </div>
            ) : null}
          </div>
        </div>
      ) : chokepointSummaryQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-chokepoint-loading">
          <p>Loading chokepoint summary.</p>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-chokepoint-error">
          <p>Chokepoint summary unavailable.</p>
        </div>
      )}

      {attentionItems.length > 0 ? (
        <div className="data-card marine-anomaly-panel" data-testid="marine-attention-queue">
          <strong>Marine Attention Queue</strong>
          <div className="stack">
            {attentionItems.map((item, index) => (
              <div key={`${item.type}-${index}`} className="data-card data-card--compact">
                <span>{item.type}</span>
                <strong>{item.label}</strong>
                <span>{item.level.toUpperCase()} | {item.score.toFixed(1)}</span>
                <span>{item.reason}</span>
                <span className="marine-anomaly-muted">{item.caveat ? `Caveat: ${item.caveat}` : "Caveats: 0"}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-attention-queue-empty">
          <p>Attention queue unavailable for current data.</p>
        </div>
      )}
    </div>
  );
}

function SliceCard({ slice }: { slice: MarineChokepointSliceSummary }) {
  return (
    <div className="data-card data-card--compact marine-slice-card" data-testid="marine-chokepoint-slice-item">
      <strong>Rank #{slice.anomaly.priorityRank ?? "-"}</strong>
      <span>{slice.anomaly.displayLabel}</span>
      <span>{slice.anomaly.level.toUpperCase()} | {slice.anomaly.score.toFixed(1)}</span>
      <span>{slice.anomaly.reasons[0] ?? "No reason stated."}</span>
      {slice.anomaly.caveats[0] ? <span className="marine-anomaly-muted">{slice.anomaly.caveats[0]}</span> : null}
    </div>
  );
}
