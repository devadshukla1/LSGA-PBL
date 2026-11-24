"""Acquire simplified directed road topology from OpenStreetMap."""

import math

import networkx as nx
import osmnx as ox

DEFAULT_BBOX = (77.19, 28.62, 77.24, 28.65)


def parameters(bbox: tuple = DEFAULT_BBOX) -> dict:
    west, south, east, north = map(float, bbox)
    if not all(map(math.isfinite, (west, south, east, north))) or not (
        -180 <= west < east <= 180 and -90 <= south < north <= 90
    ):
        raise ValueError("Expected west, south, east, north geographic bounds")
    return dict(
        bbox=[west, south, east, north],
        network_type="drive",
        simplify=True,
        retain_all=True,
        truncate_by_edge=False,
    )


def download(bbox: tuple = DEFAULT_BBOX) -> nx.MultiDiGraph:
    """Keep all components and preserve OSMnx one-way and parallel edges."""
    return ox.graph_from_bbox(**parameters(bbox))
