"""Conservative geographic lower bounds for road costs."""

import math
from collections.abc import Callable

import networkx as nx
from pyproj import CRS, Transformer
from pyproj.exceptions import CRSError

EARTH_RADIUS_M = 6_371_008.8


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance in metres between (longitude, latitude) pairs."""
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    term = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(min(1, math.sqrt(term)))


def safe_heuristic(graph: nx.MultiDiGraph, target, objective: str) -> tuple[Callable, str, bool]:
    """Scale straight-line distance by the smallest verified edge cost ratio.

    Triangle inequality makes this globally consistent, including multiedges.
    Unknown CRS, bad coordinates, or uncertain precision use zero.
    """

    def zero(node):
        return 0.0

    try:
        crs = CRS.from_user_input(graph.graph["crs"])
        transformer = Transformer.from_crs(crs, 4326, always_xy=True)
        coordinates = {}
        for node, attrs in graph.nodes(data=True):
            lon, lat = transformer.transform(float(attrs["x"]), float(attrs["y"]))
            if not all(map(math.isfinite, (lon, lat))) or not (
                -180 <= lon <= 180 and -90 <= lat <= 90
            ):
                raise ValueError("Invalid geographic coordinate")
            coordinates[node] = (lon, lat)
        if target not in coordinates:
            raise ValueError("Missing target")
        field = {"distance": "length_m", "travel_time": "travel_time_s"}[objective]
        scale = 1.0 if objective == "distance" else math.inf
        for u, v, attrs in graph.edges(data=True):
            span = haversine(coordinates[u], coordinates[v])
            if span > 0:
                scale = min(scale, float(attrs[field]) / span)
        if not math.isfinite(scale) or scale <= 0:
            return zero, "zero", True
        scale = max(0.0, scale * (1 - 1e-10))
        return (
            lambda node: scale * haversine(coordinates[node], coordinates[target]),
            ("scaled_haversine_distance" if objective == "distance" else "scaled_haversine_time"),
            False,
        )
    except (KeyError, ValueError, TypeError, OverflowError, CRSError):
        return zero, "zero", True
