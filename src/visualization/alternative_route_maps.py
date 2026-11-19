"""Exact keyed alternative maps using the existing route renderer."""

from src.visualization.route_maps import route_map


def alternative_route_maps(graph, routes) -> tuple:
    """Create selectable maps without repeating routing calculations."""
    colors = ("#22d3ee", "#fbbf24", "#c084fc", "#fb7185", "#4ade80")
    return tuple(
        route_map(graph, route, color=colors[i % len(colors)]) for i, route in enumerate(routes)
    )
