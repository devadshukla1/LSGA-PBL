"""Deterministic route ranking using scalar and tuple identifiers."""

from src.algorithms.traversal_models import canonical


def signature(edges: tuple) -> tuple:
    return tuple(tuple(canonical(value) for value in edge) for edge in edges)


def rank(route) -> tuple:
    """Exact primary cost, distance, hop count, then canonical edge identity."""
    return (
        route.optimized_cost,
        route.total_distance_m,
        len(route.edge_path),
        signature(route.edge_path),
    )
