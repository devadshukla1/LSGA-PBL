"""Highlight the selected keyed road geometry on a bounded context map."""

import folium
from pyproj import Transformer

from src.visualization.maps import road_map


def route_map(graph, route, context_limit: int = 500, color: str = "#facc15") -> folium.Map:
    """Draw exact selected edge geometry and fit the view around the route."""
    view = road_map(graph, context_limit)
    transform = Transformer.from_crs(graph.graph["crs"], 4326, always_xy=True)

    def point(node):
        attrs = graph.nodes[node]
        lon, lat = transform.transform(attrs["x"], attrs["y"])
        return lat, lon

    coords = []
    for u, v, key in route.edge_path:
        geometry = graph.edges[u, v, key].get("geometry")
        if geometry is not None:
            segment = [
                (lat, lon) for lon, lat in (transform.transform(x, y) for x, y in geometry.coords)
            ]
        else:
            segment = [point(u), point(v)]
        folium.PolyLine(segment, color=color, weight=6).add_to(view)
        coords.extend(segment)
    for node, label, color in [
        (route.source, "Source", "#22c55e"),
        (route.target, "Destination", "#ef4444"),
    ]:
        folium.CircleMarker(point(node), radius=8, color=color, tooltip=label).add_to(view)
    coords.extend([point(route.source), point(route.target)])
    lat, lon = zip(*coords, strict=True)
    view.fit_bounds([[min(lat), min(lon)], [max(lat), max(lon)]])
    return view
