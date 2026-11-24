"""Full-graph statistics counting each directed edge separately."""

import networkx as nx

from src.graph.models import GraphStatistics


def statistics(g: nx.MultiDiGraph) -> GraphStatistics:
    n, m = len(g), g.number_of_edges()
    lengths = [d["length_m"] for _, _, d in g.edges(data=True)]
    degrees = [degree for _, degree in g.degree()]
    weak = list(map(len, nx.weakly_connected_components(g)))
    strong = list(map(len, nx.strongly_connected_components(g)))
    return GraphStatistics(
        n,
        m,
        nx.density(g),
        m / n,
        m / n,
        max(degrees),
        min(degrees),
        len(weak),
        len(strong),
        max(weak),
        max(strong),
        sum(len(keys) > 1 for u in g for keys in g[u].values()),
        nx.number_of_selfloops(g),
        sum(lengths),
        min(lengths),
        max(lengths),
        sum(lengths) / m,
    )
