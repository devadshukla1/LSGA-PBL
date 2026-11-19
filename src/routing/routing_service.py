"""Dataset-independent route execution and exact-path validation."""

from dataclasses import replace

import networkx as nx

from src.algorithms.astar import astar
from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.dijkstra import dijkstra
from src.routing.route_validation import validate_route


def find_route(
    graph: nx.MultiDiGraph,
    source,
    target,
    algorithm: str = "dijkstra",
    objective: str = "travel_time",
):
    """Run the selected algorithm and validate its keyed result."""
    if not isinstance(graph, nx.MultiDiGraph):
        raise ValueError("Routing requires a directed MultiDiGraph")
    try:
        solver = {
            "dijkstra": dijkstra,
            "astar": astar,
            "bidirectional_dijkstra": bidirectional_dijkstra,
        }[algorithm]
    except KeyError as error:
        raise ValueError("Unknown routing algorithm") from error
    route = solver(graph, source, target, objective)
    validate_route(graph, route)
    return replace(route, diagnostics=replace(route.diagnostics, validation_status="valid"))
