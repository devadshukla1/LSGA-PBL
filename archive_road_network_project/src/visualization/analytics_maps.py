"""Bounded critical-junction, failure, and forest overlays."""

import folium
from pyproj import Transformer

from src.algorithms.connectivity import weak_components
from src.algorithms.traversal_models import canonical
from src.visualization.maps import road_map


def analytics_map(graph, scores=None, failed=(), forest_edges=(), limit=300):
    view = road_map(graph, limit)
    transform = Transformer.from_crs(graph.graph["crs"], 4326, always_xy=True)

    def point(x, y):
        lon, lat = transform.transform(x, y)
        return lat, lon

    def node(n):
        return point(graph.nodes[n]["x"], graph.nodes[n]["y"])

    scores = scores or {}
    highest = max(scores.values(), default=0)
    for n in sorted(scores, key=lambda n: (-scores[n], canonical(n)))[:limit]:
        size = 3 + 7 * scores[n] / highest if highest else 3
        folium.CircleMarker(node(n), radius=size, color="#fb923c", tooltip=str(n)).add_to(view)
    if failed:
        remaining = graph.subgraph([n for n in graph if n not in set(failed)])
        components = weak_components(remaining).components
        largest = max(components, key=len, default=())
        for n in sorted(largest, key=canonical)[:limit]:
            folium.CircleMarker(node(n), radius=3, color="#22d3ee").add_to(view)
        for n in failed[:limit]:
            folium.Marker(node(n), icon=folium.DivIcon(html='<b style="color:red">X</b>')).add_to(
                view
            )
    for u, v, key in forest_edges[:limit]:
        geom = graph.edges[u, v, key].get("geometry")
        coords = [point(x, y) for x, y in geom.coords] if geom is not None else [node(u), node(v)]
        folium.PolyLine(coords, color="#4ade80", weight=5).add_to(view)
    return view
