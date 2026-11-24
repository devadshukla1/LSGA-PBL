"""Connectivity summaries reusing the manual Phase 3 components."""

import networkx as nx

from src.algorithms.connectivity import strong_components, weak_components
from src.algorithms.traversal_models import prepare
from src.analytics.analytics_models import ConnectivitySummary


def connectivity_summary(graph) -> ConnectivitySummary:
    roads = prepare(graph)
    weak, strong = weak_components(roads), strong_components(roads)
    n = len(graph)
    return ConnectivitySummary(
        n,
        graph.number_of_edges(),
        weak.component_count,
        strong.component_count,
        weak.largest_component_size,
        strong.largest_component_size,
        weak.largest_component_size / n if n else 0,
        strong.largest_component_size / n if n else 0,
        tuple(sorted(map(len, weak.components), reverse=True)),
        tuple(sorted(map(len, strong.components), reverse=True)),
        tuple(nx.isolates(graph)),
    )
