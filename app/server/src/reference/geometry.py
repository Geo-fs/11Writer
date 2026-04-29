from __future__ import annotations

import json
import math
from typing import Iterable


EARTH_RADIUS_M = 6_371_000.0


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def initial_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    x = math.sin(d_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    return normalize_heading_deg(math.degrees(math.atan2(x, y)))


def normalize_heading_deg(value: float) -> float:
    return value % 360.0


def reciprocal_runway_heading(heading_deg: float | None) -> float | None:
    if heading_deg is None:
        return None
    return normalize_heading_deg(heading_deg + 180.0)


def heading_delta_deg(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    delta = abs(normalize_heading_deg(a) - normalize_heading_deg(b))
    return min(delta, 360.0 - delta)


def runway_centerpoint(
    le_lat: float | None,
    le_lon: float | None,
    he_lat: float | None,
    he_lon: float | None,
) -> tuple[float | None, float | None]:
    latitudes = [value for value in [le_lat, he_lat] if value is not None]
    longitudes = [value for value in [le_lon, he_lon] if value is not None]
    if not latitudes or not longitudes:
        return None, None
    return sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)


def runway_thresholds(record_detail: dict[str, object]) -> dict[str, tuple[float | None, float | None, float | None]]:
    return {
        "le": (
            _as_float(record_detail.get("le_latitude_deg")),
            _as_float(record_detail.get("le_longitude_deg")),
            _as_float(record_detail.get("le_heading_deg")),
        ),
        "he": (
            _as_float(record_detail.get("he_latitude_deg")),
            _as_float(record_detail.get("he_longitude_deg")),
            _as_float(record_detail.get("he_heading_deg")),
        ),
    }


def runway_bearing_from_thresholds(record_detail: dict[str, object]) -> float | None:
    le_lat, le_lon, _ = runway_thresholds(record_detail)["le"]
    he_lat, he_lon, _ = runway_thresholds(record_detail)["he"]
    if None in (le_lat, le_lon, he_lat, he_lon):
        return None
    return initial_bearing_deg(le_lat, le_lon, he_lat, he_lon)


def bbox_intersects(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> bool:
    left_min_lat, left_min_lon, left_max_lat, left_max_lon = left
    right_min_lat, right_min_lon, right_max_lat, right_max_lon = right
    return not (
        left_max_lat < right_min_lat
        or left_min_lat > right_max_lat
        or left_max_lon < right_min_lon
        or left_min_lon > right_max_lon
    )


def point_to_segment_distance_m(
    lat: float,
    lon: float,
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
) -> float:
    scale = 111_320.0
    avg_lat = math.radians((start_lat + end_lat + lat) / 3)
    x = lon * scale * math.cos(avg_lat)
    y = lat * scale
    x1 = start_lon * scale * math.cos(avg_lat)
    y1 = start_lat * scale
    x2 = end_lon * scale * math.cos(avg_lat)
    y2 = end_lat * scale
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    px = x1 + t * dx
    py = y1 + t * dy
    return math.hypot(x - px, y - py)


def point_to_reference_object_distance_m(
    lat: float,
    lon: float,
    *,
    object_type: str,
    centroid_lat: float | None,
    centroid_lon: float | None,
    detail: dict[str, object],
) -> tuple[float | None, str]:
    if object_type == "runway":
        le_lat, le_lon, _ = runway_thresholds(detail)["le"]
        he_lat, he_lon, _ = runway_thresholds(detail)["he"]
        if None not in (le_lat, le_lon, he_lat, he_lon):
            return point_to_segment_distance_m(lat, lon, le_lat, le_lon, he_lat, he_lon), "segment"
    if centroid_lat is None or centroid_lon is None:
        return None, "unknown"
    return haversine_distance_m(lat, lon, centroid_lat, centroid_lon), "centroid"


def bearing_to_reference_object_deg(
    lat: float,
    lon: float,
    *,
    centroid_lat: float | None,
    centroid_lon: float | None,
) -> float | None:
    if centroid_lat is None or centroid_lon is None:
        return None
    return initial_bearing_deg(lat, lon, centroid_lat, centroid_lon)


def airport_influence_radius_m(airport_type: str | None, longest_runway_ft: float | None = None) -> float:
    base = {
        "large_airport": 15_000.0,
        "medium_airport": 8_000.0,
        "small_airport": 4_000.0,
        "heliport": 1_500.0,
        "seaplane_base": 2_500.0,
    }.get((airport_type or "").lower(), 3_000.0)
    if longest_runway_ft is None:
        return base
    if longest_runway_ft >= 10_000:
        return max(base, 15_000.0)
    if longest_runway_ft >= 7_000:
        return max(base, 8_000.0)
    if longest_runway_ft >= 4_000:
        return max(base, 5_000.0)
    return base


def point_in_polygon(lat: float, lon: float, geometry_json: str | None) -> bool:
    if not geometry_json:
        return False
    try:
        geometry = json.loads(geometry_json)
    except json.JSONDecodeError:
        return False
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type == "Polygon":
        return any(_point_in_ring(lat, lon, ring) for ring in coordinates[:1]) if isinstance(coordinates, list) else False
    if geometry_type == "MultiPolygon" and isinstance(coordinates, list):
        for polygon in coordinates:
            if isinstance(polygon, list) and polygon and _point_in_ring(lat, lon, polygon[0]):
                return True
    return False


def _point_in_ring(lat: float, lon: float, ring: Iterable[Iterable[float]]) -> bool:
    points = list(ring)
    if len(points) < 3:
        return False
    inside = False
    j = len(points) - 1
    for i, point in enumerate(points):
        xi, yi = point[0], point[1]
        xj, yj = points[j][0], points[j][1]
        intersects = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def _as_float(value: object | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
