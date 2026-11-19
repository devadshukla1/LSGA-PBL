"""Tests for BFS, DFS, Dijkstra, A*, Bidirectional Dijkstra, and Yen's K-Shortest."""

import networkx as nx
import pytest

from scripts.generate_sample_graph import build_sample
from src.algorithms.bfs import bfs
from src.algorithms.dfs import dfs
from src.algorithms.traversal_models import prepare
from src.routing.route_alternatives import find_alternative_routes
from src.routing.routing_service import find_route


def test_bfs_hop_minimality_against_networkx() -> None:
    """Verify BFS finds exact unweighted directed hop-minimal distances."""
    graph = build_sample()
    roads = prepare(graph)
    tree = bfs(roads, 0)

    # Compare with NetworkX single source shortest path lengths (unweighted)
    nx_lengths = nx.single_source_shortest_path_length(graph, 0)

    for target_node, expected_hops in nx_lengths.items():
        assert target_node in tree.depth
        assert tree.depth[target_node] == expected_hops


def test_dfs_cycle_and_discovery() -> None:
    """Verify iterative DFS handles cycles and visits all reachable nodes."""
    graph = build_sample()
    roads = prepare(graph)
    tree = dfs(roads, 0)

    # All nodes visited must be in NetworkX reachable nodes
    nx_reachable = set(nx.descendants(graph, 0)) | {0}
    assert set(tree.visit_order) == nx_reachable
    assert len(tree.finish_order) == len(tree.visit_order)


def test_dijkstra_source_equals_target() -> None:
    """Verify Dijkstra when source equals target."""
    graph = build_sample()
    route = find_route(graph, 0, 0, "dijkstra", "distance")
    assert route.is_reachable
    assert route.optimized_cost == 0.0
    assert route.node_path == (0,)
    assert route.edge_path == ()


def test_dijkstra_unreachable_node() -> None:
    """Verify Dijkstra handling of unreachable destination."""
    graph = build_sample()
    # Node 15 is in a separate disconnected component
    route = find_route(graph, 0, 15, "dijkstra", "distance")
    assert not route.is_reachable
    assert route.node_path == ()
    assert route.edge_path == ()
    assert route.status == "unreachable"


def test_all_three_algorithms_agree_on_optimal_cost() -> None:
    """Verify Dijkstra, A*, and Bidirectional Dijkstra yield identical optimal costs."""
    graph = build_sample()

    for obj in ("distance", "travel_time"):
        r_dijkstra = find_route(graph, 0, 10, "dijkstra", obj)
        r_astar = find_route(graph, 0, 10, "astar", obj)
        r_bidir = find_route(graph, 0, 10, "bidirectional_dijkstra", obj)

        assert r_dijkstra.is_reachable
        assert r_astar.is_reachable
        assert r_bidir.is_reachable

        assert pytest.approx(r_dijkstra.optimized_cost) == r_astar.optimized_cost
        assert pytest.approx(r_dijkstra.optimized_cost) == r_bidir.optimized_cost


def test_yen_k_shortest_invariants() -> None:
    """Verify Yen's K-shortest paths are loopless and ordered by nondecreasing cost."""
    graph = build_sample()
    alt_result = find_alternative_routes(graph, 0, 10, k=3, objective="distance")

    assert len(alt_result.routes) >= 2
    costs = [r.optimized_cost for r in alt_result.routes]

    # Ordered nondecreasing
    assert costs == sorted(costs)

    # First route is globally optimal (matches Dijkstra)
    best = find_route(graph, 0, 10, "dijkstra", "distance")
    assert pytest.approx(alt_result.routes[0].optimized_cost) == best.optimized_cost

    # Loopless invariant
    for route in alt_result.routes:
        assert len(route.node_path) == len(set(route.node_path)), "Route must be loopless"
