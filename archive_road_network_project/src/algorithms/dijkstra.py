"""Manual Dijkstra search over keyed, directed road edges."""

from src.algorithms.routing_search import search


def dijkstra(graph_or_adjacency, source, target, objective="distance"):
    """Find an optimal route using a zero heuristic."""
    return search(graph_or_adjacency, source, target, objective, "dijkstra")
