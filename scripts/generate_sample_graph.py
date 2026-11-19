"""Generate the bundled synthetic New Delhi road example."""

import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph.dataset_service import SAMPLE, metadata_for, register
from src.graph.weights import apply_weights


def build_sample() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph(crs="EPSG:4326")
    for n in range(16):
        graph.add_node(n, x=77.21 + (n % 4) * 0.001, y=28.63 + (n // 4) * 0.001)
    for n in range(14):
        for target in (n + 1, n + 4):
            if target >= 14 or (target == n + 1 and target % 4 == 0):
                continue
            attrs = dict(length=100 + n * 3, highway="residential", oneway=n % 3 == 0)
            graph.add_edge(n, target, **attrs)
            if not attrs["oneway"]:
                graph.add_edge(target, n, **attrs)
    graph.add_edge(0, 1, key=7, length=140, highway="primary", oneway=True)
    graph.add_edge(14, 15, length=90, highway="service", oneway=True)
    apply_weights(graph)
    return graph


if __name__ == "__main__":
    graph = build_sample()
    register(graph, metadata_for(graph, SAMPLE))
    print(
        f"Generated SYNTHETIC sample: {len(graph)} nodes, {graph.number_of_edges()} directed edges"
    )
