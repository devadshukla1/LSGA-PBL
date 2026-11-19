"""Compare local traversal results to NetworkX on the validated offline dataset."""

import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.algorithms.bfs import bfs
from src.algorithms.connectivity import strong_components, weak_components
from src.algorithms.dfs import dfs
from src.algorithms.reachability import find_unweighted_path
from src.algorithms.traversal_models import prepare
from src.graph.dataset_service import load
from src.graph.representation import build_adjacency
from src.graph.validation import validate


def main() -> int:
    info = load()
    g = info.graph
    roads = prepare(build_adjacency(g))
    source = next(iter(roads))
    expected = nx.single_source_shortest_path_length(g, source)
    target = max(expected, key=expected.get)
    checks = {
        "Dataset integrity": validate(g, info.metadata).valid,
        "BFS hop distances": bfs(roads, source).depth == expected,
        "DFS reachable set": dfs(roads, source).visited_nodes == set(expected),
        "Reachability path": find_unweighted_path(roads, source, target).hop_count
        == expected[target],
        "Weak membership": set(weak_components(roads).components)
        == set(map(frozenset, nx.weakly_connected_components(g))),
        "Strong membership": set(strong_components(roads).components)
        == set(map(frozenset, nx.strongly_connected_components(g))),
    }
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
