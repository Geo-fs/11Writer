import { useEffect, useMemo, useState } from "react";
import clsx from "clsx";
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
import { buildMarineEvidenceSummary } from "./marineEvidenceSummary";
import { buildFocusedMarineReplayEvidence } from "./marineReplayEvidence";
import {
  buildMarineEvidenceInterpretation,
  getMarineEvidenceInterpretationCards,
  type MarineEvidenceInterpretationMode
} from "./marineEvidenceInterpretation";
import {
  chokepointSliceNavigationTarget,
  fromGapEvent,
  type MarineReplayNavigationTarget,
  vesselNavigationTarget,
  viewportNavigationTarget
} from "./marineReplayNavigation";

type SliceFilter = "all" | "medium+" | "high";
type SliceSort = "priority" | "score";

export function MarineAnomalySection() {
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const hud = useAppStore((state) => state.hud);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const setMarineEvidenceSummary = useAppStore((state) => state.setMarineEvidenceSummary);
  const focusedTarget = useAppStore((state) => state.activeMarineReplayTarget);
  const setFocusedTarget = useAppStore((state) => state.setActiveMarineReplayTarget);
  const [sliceFilter, setSliceFilter] = useState<SliceFilter>("all");
  const [sliceSort, setSliceSort] = useState<SliceSort>("priority");
  const [interpretationMode, setInterpretationMode] =
    useState<MarineEvidenceInterpretationMode>("compact");
  const vesselsQuery = useMarineVesselsQuery();
  const selectedMarineVesselId =
    selectedEntity?.type === "marine-vessel"
      ? selectedEntity.id
      : vesselsQuery.data?.vessels?.[0]?.id ?? null;
  const vesselSummaryQuery = useMarineVesselSummaryQuery(selectedMarineVesselId);
  const center =
    Number.isFinite(hud.latitude) && Number.isFinite(hud.longitude)
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
    const items: Array<{
      type: string;
      label: string;
      level: string;
      score: number;
      reason: string;
      caveat: string;
      target: MarineReplayNavigationTarget | null;
    }> = [];
    if (vesselSummaryQuery.data) {
      const target = vesselNavigationTarget(vesselSummaryQuery.data);
      items.push({
        type: "vessel",
        label: vesselSummaryQuery.data.anomaly.displayLabel,
        level: vesselSummaryQuery.data.anomaly.level,
        score: vesselSummaryQuery.data.anomaly.score,
        reason: vesselSummaryQuery.data.anomaly.reasons[0] ?? "No reason stated.",
        caveat: vesselSummaryQuery.data.anomaly.caveats[0] ?? "",
        target
      });
    }
    if (viewportSummaryQuery.data) {
      const target = viewportNavigationTarget(viewportSummaryQuery.data);
      items.push({
        type: "viewport",
        label: viewportSummaryQuery.data.anomaly.displayLabel,
        level: viewportSummaryQuery.data.anomaly.level,
        score: viewportSummaryQuery.data.anomaly.score,
        reason: viewportSummaryQuery.data.anomaly.reasons[0] ?? "No reason stated.",
        caveat: viewportSummaryQuery.data.anomaly.caveats[0] ?? "",
        target
      });
    }
    const topSlice = sortedSlices[0];
    if (topSlice) {
      const target = chokepointSliceNavigationTarget(topSlice);
      items.push({
        type: "chokepoint",
        label: topSlice.anomaly.displayLabel,
        level: topSlice.anomaly.level,
        score: topSlice.anomaly.score,
        reason: topSlice.anomaly.reasons[0] ?? "No reason stated.",
        caveat: topSlice.anomaly.caveats[0] ?? "",
        target
      });
    }
    return items.sort((a, b) => b.score - a.score);
  }, [sortedSlices, vesselSummaryQuery.data, viewportSummaryQuery.data]);

  const focusedEvidenceRows = useMemo(
    () =>
      buildFocusedMarineReplayEvidence({
        target: focusedTarget,
        vesselSummary: vesselSummaryQuery.data ?? null,
        viewportSummary: viewportSummaryQuery.data ?? null,
        chokepointSummary: chokepointSummaryQuery.data ?? null
      }),
    [focusedTarget, vesselSummaryQuery.data, viewportSummaryQuery.data, chokepointSummaryQuery.data]
  );

  const focusedEvidenceInterpretation = useMemo(
    () =>
      buildMarineEvidenceInterpretation({
        focusedEvidenceRows,
        activeNavigationTarget: focusedTarget,
        vesselSummary: vesselSummaryQuery.data ?? null,
        viewportSummary: viewportSummaryQuery.data ?? null,
        chokepointSummary: chokepointSummaryQuery.data ?? null
      }),
    [
      focusedEvidenceRows,
      focusedTarget,
      vesselSummaryQuery.data,
      viewportSummaryQuery.data,
      chokepointSummaryQuery.data
    ]
  );

  const visibleInterpretationCards = useMemo(
    () => getMarineEvidenceInterpretationCards(focusedEvidenceInterpretation, interpretationMode),
    [focusedEvidenceInterpretation, interpretationMode]
  );

  const exportSummary = useMemo(
    () =>
      buildMarineEvidenceSummary({
        selectedVesselSummary: vesselSummaryQuery.data ?? null,
        viewportSummary: viewportSummaryQuery.data ?? null,
        chokepointSummary: chokepointSummaryQuery.data ?? null,
        visibleSlices: sortedSlices,
        controls: { chokepointFilter: sliceFilter, chokepointSort: sliceSort },
        activeNavigationTarget: focusedTarget,
        focusedEvidenceRows,
        focusedEvidenceInterpretation,
        focusedEvidenceInterpretationMode: interpretationMode,
        visibleInterpretationCards
      }),
    [
      vesselSummaryQuery.data,
      viewportSummaryQuery.data,
      chokepointSummaryQuery.data,
      sortedSlices,
      sliceFilter,
      sliceSort,
      focusedTarget,
      focusedEvidenceRows,
      focusedEvidenceInterpretation,
      interpretationMode,
      visibleInterpretationCards
    ]
  );

  useEffect(() => {
    setMarineEvidenceSummary({
      lines: exportSummary.displayLines,
      metadata: exportSummary.metadata
    });
  }, [exportSummary, setMarineEvidenceSummary]);

  const focusedSliceVisible = useMemo(() => {
    if (!focusedTarget || focusedTarget.kind !== "chokepoint-slice") {
      return true;
    }
    return sortedSlices.some(
      (slice) =>
        slice.sliceStartAt === focusedTarget.timeWindowStart &&
        slice.sliceEndAt === focusedTarget.timeWindowEnd
    );
  }, [focusedTarget, sortedSlices]);

  const focusedStaleMessage = useMemo(() => {
    if (!focusedTarget) return null;
    if (focusedTarget.kind === "chokepoint-slice" && !focusedSliceVisible) {
      return "Focused target not visible under current filters";
    }
    if (!focusedTarget.directReplayTarget) {
      return focusedTarget.unavailableReason ?? "Summary-level signal only";
    }
    return null;
  }, [focusedTarget, focusedSliceVisible]);

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
        <>
          <MarineAnomalyPanel
            title={`Selected Vessel: ${vesselSummaryQuery.data.latestObserved?.label ?? vesselSummaryQuery.data.vesselId}`}
            anomaly={vesselSummaryQuery.data.anomaly}
            note="Notable activity from vessel summary window."
          />
          <div className="stack stack--actions">
            {vesselSummaryQuery.data.mostRecentResumedObservation ? (
              <button
                type="button"
                className="ghost-button ghost-button--small"
                data-testid="marine-focus-vessel-event"
                onClick={() => {
                  const resumed = vesselSummaryQuery.data?.mostRecentResumedObservation;
                  if (!resumed) {
                    return;
                  }
                  setFocusedTarget(
                    fromGapEvent(vesselSummaryQuery.data.vesselId, resumed, "Focus replay event")
                  );
                }}
              >
                Focus replay event
              </button>
            ) : (
              <button type="button" className="ghost-button ghost-button--small" disabled>
                Replay target unavailable for this reason
              </button>
            )}
          </div>
        </>
      ) : (
        <div className="empty-state compact" data-testid="marine-vessel-low-state">
          <p>No selected vessel anomaly summary.</p>
          <span>Low or unavailable marine vessel priority for this context.</span>
        </div>
      )}

      {viewportSummaryQuery.data ? (
        <>
          <MarineAnomalyPanel
            title="Viewport Notable Activity"
            anomaly={viewportSummaryQuery.data.anomaly}
            note="Does this time/area window deserve attention?"
          />
          <div className="stack stack--actions">
            <button
              type="button"
              className="ghost-button ghost-button--small"
              data-testid="marine-focus-viewport-window"
              onClick={() => setFocusedTarget(viewportNavigationTarget(viewportSummaryQuery.data))}
            >
              Focus viewport window
            </button>
          </div>
        </>
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
              <SliceCard
                key={`${slice.sliceStartAt}-${slice.sliceEndAt}`}
                slice={slice}
                onFocus={() => setFocusedTarget(chokepointSliceNavigationTarget(slice))}
                focused={
                  focusedTarget?.kind === "chokepoint-slice" &&
                  focusedTarget.timeWindowStart === slice.sliceStartAt &&
                  focusedTarget.timeWindowEnd === slice.sliceEndAt
                }
              />
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
              <button
                key={`${item.type}-${index}`}
                type="button"
                className={clsx(
                  "data-card data-card--compact marine-queue-item-button",
                  focusedTarget?.label === item.target?.label && "marine-target-focus"
                )}
                data-testid="marine-attention-queue-item"
                onClick={() => {
                  if (item.target) setFocusedTarget(item.target);
                }}
              >
                <span>{item.type}</span>
                <strong>{item.label}</strong>
                <span>{item.level.toUpperCase()} | {item.score.toFixed(1)}</span>
                <span>{item.reason}</span>
                <span className="marine-anomaly-muted">
                  {item.caveat ? `Caveat: ${item.caveat}` : "Caveats: 0"}
                </span>
                {!item.target?.directReplayTarget ? (
                  <span className="marine-anomaly-muted">
                    {item.target?.unavailableReason ?? "Summary-level signal only"}
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-attention-queue-empty">
          <p>Attention queue unavailable for current data.</p>
        </div>
      )}

      <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-export-preview">
        <strong>Snapshot Marine Evidence</strong>
        {exportSummary.displayLines.slice(0, 4).map((line) => (
          <span key={line}>{line}</span>
        ))}
      </div>
      {focusedTarget ? (
        <div
          className={clsx(
            "data-card data-card--compact marine-anomaly-panel",
            focusedStaleMessage && "marine-target-stale"
          )}
          data-testid="marine-focused-target"
        >
          <strong>Focused replay target</strong>
          <span>{focusedTarget.label}</span>
          <span>{focusedTarget.kind}</span>
          <span>
            {focusedTarget.timeWindowStart && focusedTarget.timeWindowEnd
              ? `${focusedTarget.timeWindowStart} to ${focusedTarget.timeWindowEnd}`
              : focusedTarget.timestamp ?? "Summary-level signal only"}
          </span>
          {focusedStaleMessage ? (
            <span className="marine-anomaly-muted" data-testid="marine-focused-target-stale">
              {focusedStaleMessage}
            </span>
          ) : null}
          {focusedTarget.caveat ? (
            <span className="marine-anomaly-muted">{focusedTarget.caveat}</span>
          ) : null}
        </div>
      ) : null}
      <div className="data-card marine-anomaly-panel" data-testid="marine-focused-evidence">
        <strong>Focused Replay Evidence</strong>
        {focusedTarget == null ? (
          <span className="marine-anomaly-muted">Focus an anomaly item to inspect replay evidence.</span>
        ) : (
          <>
            <span className="marine-anomaly-muted">
              {focusedTarget.label} ({focusedTarget.kind})
            </span>
            <div className="stack">
              {focusedEvidenceRows.map((row) => (
                <div
                  key={row.id}
                  className={clsx(
                    "data-card data-card--compact marine-evidence-row",
                    row.isFocused && "marine-target-focus",
                    row.observedOrInferred === "summary" && "marine-evidence-row--summary"
                  )}
                  data-testid="marine-evidence-row"
                >
                  <strong>{row.label}</strong>
                  <span className="marine-anomaly-muted">
                    {row.timeWindowStart && row.timeWindowEnd
                      ? `${row.timeWindowStart} to ${row.timeWindowEnd}`
                      : row.timestamp ?? "Summary-level signal only"}
                  </span>
                  <span>{row.detail}</span>
                  <span className="marine-anomaly-muted">
                    {row.observedOrInferred} · {row.kind}
                  </span>
                  {row.caveat ? (
                    <span className="marine-anomaly-muted">Caveat: {row.caveat}</span>
                  ) : null}
                </div>
              ))}
              {focusedEvidenceRows.length === 0 ? (
                <span className="marine-anomaly-muted">Replay target unavailable for this reason.</span>
              ) : null}
            </div>
            <div className="data-card data-card--compact" data-testid="marine-evidence-interpretation">
              <strong>Evidence Interpretation</strong>
              <label className="field-row" data-testid="marine-evidence-interpretation-mode">
                <span>Display mode</span>
                <select
                  className="panel__select"
                  value={interpretationMode}
                  onChange={(event) =>
                    setInterpretationMode(
                      event.currentTarget.value as MarineEvidenceInterpretationMode
                    )
                  }
                >
                  <option value="compact">Compact</option>
                  <option value="detailed">Detailed</option>
                  <option value="evidence-only">Evidence only</option>
                  <option value="caveats-first">Caveats first</option>
                </select>
              </label>
              <span>Why this was prioritized: {focusedEvidenceInterpretation.priorityExplanation}</span>
              <span className="marine-anomaly-muted">
                Trust/caveat: {focusedEvidenceInterpretation.trustLevel}
              </span>
              <div className="stack">
                {visibleInterpretationCards.map((card, index) => (
                  <div
                    key={`${card.kind}-${index}`}
                    className="data-card data-card--compact marine-evidence-row"
                    data-testid="marine-interpretation-card"
                  >
                    <strong>{card.label}</strong>
                    <span>{card.value}</span>
                    <span className="marine-anomaly-muted">{card.detail}</span>
                    <span className="marine-anomaly-muted">
                      {card.basis} · {card.severity}
                    </span>
                    {card.caveat ? (
                      <span className="marine-anomaly-muted">Caveat: {card.caveat}</span>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SliceCard({
  slice,
  onFocus,
  focused
}: {
  slice: MarineChokepointSliceSummary;
  onFocus: () => void;
  focused?: boolean;
}) {
  return (
    <div
      className={clsx("data-card data-card--compact marine-slice-card", focused && "marine-target-focus")}
      data-testid="marine-chokepoint-slice-item"
    >
      <strong>Rank #{slice.anomaly.priorityRank ?? "-"}</strong>
      <span>{slice.anomaly.displayLabel}</span>
      <span>{slice.anomaly.level.toUpperCase()} | {slice.anomaly.score.toFixed(1)}</span>
      <span>{slice.anomaly.reasons[0] ?? "No reason stated."}</span>
      {slice.anomaly.caveats[0] ? (
        <span className="marine-anomaly-muted">{slice.anomaly.caveats[0]}</span>
      ) : null}
      <button
        type="button"
        className="ghost-button ghost-button--small"
        data-testid="marine-focus-slice"
        onClick={onFocus}
      >
        Focus slice window
      </button>
    </div>
  );
}
