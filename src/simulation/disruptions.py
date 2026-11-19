"""Exact keyed road and node exclusions on an independent graph."""


def apply_disruptions(graph, scenario) -> None:
    """Apply already-validated disruptions to the caller's scenario copy."""
    graph.remove_edges_from(scenario.closed_edges)
    graph.remove_nodes_from(scenario.blocked_nodes)
