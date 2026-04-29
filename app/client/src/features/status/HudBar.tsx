import { formatRelativeAge, getReplaySnapshot } from "../../lib/history";
import { buildActiveImageryContextFromHud } from "../../lib/imageryContext";
import { useSourceStatusQuery } from "../../lib/queries";
import { useAppStore } from "../../lib/store";
import { ImageryContextBadge } from "../imagery/ImageryContextBadge";

export function HudBar() {
  const hud = useAppStore((state) => state.hud);
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const entityHistoryTracks = useAppStore((state) => state.entityHistoryTracks);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const sourceStatusQuery = useSourceStatusQuery();
  const degradedCount =
    sourceStatusQuery.data?.sources.filter((source) =>
      ["stale", "rate-limited", "degraded"].includes(source.state)
    ).length ?? 0;
  const replaySnapshot =
    selectedEntity && (selectedEntity.type === "aircraft" || selectedEntity.type === "satellite")
      ? getReplaySnapshot(entityHistoryTracks[selectedEntity.id] ?? null, selectedReplayIndex)
      : null;
  const imageryContext = buildActiveImageryContextFromHud(hud);
  const isReplayContext = selectedReplayIndex != null;

  return (
    <footer className="hud">
      <span>Lat {hud.latitude.toFixed(4)}</span>
      <span>Lon {hud.longitude.toFixed(4)}</span>
      <span>Alt {hud.altitudeMeters.toLocaleString()} m</span>
      <span>Heading {hud.headingDegrees.toFixed(1)} deg</span>
      <span>Pitch {hud.pitchDegrees.toFixed(1)} deg</span>
      <ImageryContextBadge context={imageryContext} isReplayContext={isReplayContext} />
      <span>3D Tiles {hud.tilesProvider}</span>
      <span>Selected {selectedEntity?.label ?? "None"}</span>
      {replaySnapshot ? (
        <span>
          Track {replaySnapshot.isLive ? "Live" : `Replay ${formatRelativeAge(replaySnapshot.ageSeconds)}`}
        </span>
      ) : null}
      <span>{new Date(hud.timestamp).toLocaleTimeString()}</span>
      <span>Imagery Status {hud.imageryStatus}</span>
      <span>Degraded Sources {degradedCount}</span>
    </footer>
  );
}
