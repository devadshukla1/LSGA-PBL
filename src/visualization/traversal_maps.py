"""Bounded traversal overlays on the Phase 2 road map."""

from itertools import islice

import folium
from pyproj import Transformer

from src.visualization.maps import road_map


def traversal_map(graph, traversal, target=None, path_edges=(), limit: int = 150) -> folium.Map:
    view = road_map(graph, limit)
    convert = Transformer.from_crs(graph.graph["crs"], 4326, always_xy=True)

    def point(x, y):
        lon, lat = convert.transform(x, y)
        return lat, lon

    def position(n):
        data = graph.nodes[n]
        return point(data["x"], data["y"])

    for n in traversal.visit_order[:limit]:
        folium.CircleMarker(position(n), radius=3, color="#a78bfa").add_to(view)
    for edges, color, width in [(traversal.tree_edges, "#c084fc", 3), (path_edges, "#fde047", 6)]:
        for u, v, k in islice(edges, limit):
            geometry = graph.edges[u, v, k].get("geometry")
            coords = (
                [point(x, y) for x, y in geometry.coords]
                if geometry
                else [position(u), position(v)]
            )
            folium.PolyLine(coords, color=color, weight=width).add_to(view)
    for n, label, color, radius in [
        (traversal.start_node, "Source", "#22c55e", 9),
        (target, "Target", "#ef4444", 6),
    ]:
        if n is not None:
            folium.CircleMarker(position(n), radius=radius, color=color, tooltip=label).add_to(view)
    return view
