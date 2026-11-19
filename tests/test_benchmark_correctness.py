"""Tests for route validation and NetworkX optimality verification."""

from src.algorithms.astar import astar
from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.dijkstra import dijkstra
from src.benchmarks.correctness import verify_route_correctness_and_optimality
from src.graph.dataset_service import load


def test_dijkstra_optimality_against_networkx():
    info = load()
    graph = info.graph
    source, target = 0, 1

    route = dijkstra(graph, source, target, objective="distance")
    valid, optimal, ref_cost, abs_err, rel_err, issues = verify_route_correctness_and_optimality(
        graph, route, source, target, objective="distance"
    )

    assert valid is True
    assert optimal is True
    assert ref_cost is not None
    assert abs_err == 0.0
    assert len(issues) == 0


def test_astar_optimality_against_networkx():
    info = load()
    graph = info.graph
    source, target = 0, 1

    route = astar(graph, source, target, objective="travel_time")
    valid, optimal, ref_cost, abs_err, rel_err, issues = verify_route_correctness_and_optimality(
        graph, route, source, target, objective="travel_time"
    )

    assert valid is True
    assert optimal is True
    assert ref_cost is not None
    assert abs_err == 0.0
    assert len(issues) == 0


def test_bidirectional_dijkstra_optimality_against_networkx():
    info = load()
    graph = info.graph
    source, target = 0, 5

    route = bidirectional_dijkstra(graph, source, target, objective="distance")
    valid, optimal, ref_cost, abs_err, rel_err, issues = verify_route_correctness_and_optimality(
        graph, route, source, target, objective="distance"
    )

    assert valid is True
    assert optimal is True
    assert ref_cost is not None
    assert abs_err == 0.0
    assert len(issues) == 0
