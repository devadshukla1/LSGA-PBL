"""Manual A* search with a globally consistent geographic heuristic."""

from src.algorithms.routing_search import search


def astar(graph_or_adjacency, source, target, objective="distance"):
    """Find an optimal route with safe heuristic fallback."""
    return search(graph_or_adjacency, source, target, objective, "astar")
