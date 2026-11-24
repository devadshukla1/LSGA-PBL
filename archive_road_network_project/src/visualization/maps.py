"""Bounded road map for a full geographic road graph."""

from itertools import islice

import folium
import networkx as nx
from branca.element import Element
from pyproj import Transformer


def road_map(graph: nx.MultiDiGraph, limit: int = 500) -> folium.Map:
    transform = Transformer.from_crs(graph.graph["crs"], 4326, always_xy=True)

    def point(x: float, y: float) -> tuple:
        lon, lat = transform.transform(x, y)
        return lat, lon

    positions = {n: point(d["x"], d["y"]) for n, d in graph.nodes(data=True)}
    result = folium.Map(tiles=None)
    folium.TileLayer("OpenStreetMap").add_to(result)
    result.get_root().header.add_child(
        Element(
            "<style>.leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.76)}"
            ".leaflet-container{background:#111827}</style>"
        )
    )
    for u, v, d in islice(graph.edges(data=True), limit):
        geom = d.get("geometry")
        coords = (
            [point(x, y) for x, y in geom.coords]
            if geom is not None
            else [positions[u], positions[v]]
        )
        folium.PolyLine(coords, color="#38BDF8", weight=3).add_to(result)
    for n in islice(graph, limit):
        folium.CircleMarker(positions[n], radius=2, color="#FB923C").add_to(result)
    lat, lon = zip(*positions.values(), strict=True)
    result.fit_bounds([[min(lat), min(lon)], [max(lat), max(lon)]])
    return result
