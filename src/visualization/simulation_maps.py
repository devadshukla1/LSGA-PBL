"""Bounded disruption overlays with complete baseline and scenario routes."""

import folium
from pyproj import Transformer

from src.simulation.congestion import generate_congestion
from src.visualization.maps import road_map


def simulation_map(graph, scenario, result, limit=300):
    view = road_map(graph, limit)
    transform = Transformer.from_crs(graph.graph["crs"], 4326, always_xy=True)

    def point(x, y):
        lon, lat = transform.transform(x, y)
        return lat, lon

    def node(n):
        return point(graph.nodes[n]["x"], graph.nodes[n]["y"])

    def line(edge, color, width):
        u, v, k = edge
        geometry = graph.edges[edge].get("geometry")
        coords = (
            [point(x, y) for x, y in geometry.coords]
            if geometry is not None
            else [node(u), node(v)]
        )
        folium.PolyLine(coords, color=color, weight=width).add_to(view)

    congested = [e for e, m in generate_congestion(graph, scenario).items() if m > 1]
    for edge in congested[:limit]:
        line(edge, "#fb923c", 3)
    for route, color in ((result.baseline, "#22d3ee"), (result.scenario_route, "#4ade80")):
        if route and route.is_reachable:
            for edge in route.edge_path:
                line(edge, color, 6)
    for edge in scenario.closed_edges[:limit]:
        line(edge, "#ef4444", 5)
    for n in scenario.blocked_nodes[:limit]:
        folium.CircleMarker(node(n), radius=8, color="#ef4444", tooltip="Blocked").add_to(view)
    for n, label in ((result.baseline.source, "Source"), (result.baseline.target, "Destination")):
        folium.Marker(node(n), tooltip=label).add_to(view)
    return view
