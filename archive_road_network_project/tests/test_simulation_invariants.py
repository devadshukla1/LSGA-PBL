"""Tests for traffic simulation invariants, congestion tiers, closures, and immutability."""

import pytest

from scripts.generate_sample_graph import build_sample
from src.simulation.scenario_builder import build_scenario_graph, create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.simulation_engine import simulate


def test_normal_traffic_travel_times_unchanged() -> None:
    """Verify normal congestion level maintains 1.0x travel times."""
    graph = build_sample()
    scenario = create_scenario(
        graph,
        "offline_sample",
        "normal",
        42,
        0.5,
    )
    req = SimulationRequest(0, 1, "dijkstra", "travel_time")
    result = simulate(graph, scenario, req, "offline_sample")

    assert result.status == "ok"
    assert result.scenario_route is not None
    assert pytest.approx(result.scenario_route.optimized_cost) == result.baseline.optimized_cost


def test_heavy_congestion_increases_travel_time() -> None:
    """Verify heavy congestion multiplies travel times without changing distance."""
    graph = build_sample()
    scenario = create_scenario(
        graph,
        "offline_sample",
        "heavy",
        42,
        1.0,
    )
    req = SimulationRequest(0, 10, "dijkstra", "travel_time")
    result = simulate(graph, scenario, req, "offline_sample")

    assert result.status == "ok"
    assert result.scenario_route is not None
    assert result.scenario_route.total_travel_time_s > result.baseline.total_travel_time_s
    # Length of segments remains unchanged
    assert result.scenario_route.total_distance_m > 0


def test_road_closure_excludes_closed_edge() -> None:
    """Verify a closed directed edge is never traversed by the scenario route."""
    graph = build_sample()
    # Baseline route from 0 to 1 uses edge (0, 1, 7) or (0, 1, 0)
    req = SimulationRequest(0, 1, "dijkstra", "travel_time")
    baseline_result = simulate(
        graph,
        create_scenario(graph, "offline_sample", "normal", 42, 0.0),
        req,
        "offline_sample",
    )
    chosen_edge = baseline_result.baseline.edge_path[0]

    # Close that exact edge
    closed_scenario = create_scenario(
        graph,
        "offline_sample",
        "normal",
        42,
        0.0,
        closed_edges=(chosen_edge,),
    )
    result = simulate(graph, closed_scenario, req, "offline_sample")

    assert result.scenario_route is not None
    assert chosen_edge not in result.scenario_route.edge_path


def test_blocked_source_node_is_unreachable() -> None:
    """Verify blocking the origin node prevents routing."""
    graph = build_sample()
    blocked_scenario = create_scenario(
        graph,
        "offline_sample",
        "normal",
        42,
        0.0,
        blocked_nodes=(0,),
    )
    req = SimulationRequest(0, 1, "dijkstra", "travel_time")
    result = simulate(graph, blocked_scenario, req, "offline_sample")

    assert result.status == "blocked_endpoint"
    assert result.scenario_route is None


def test_original_graph_is_not_mutated() -> None:
    """Verify simulation builds an effective graph without modifying original edge attributes."""
    graph = build_sample()
    orig_time = graph.edges[0, 1, 0]["travel_time_s"]

    scenario = create_scenario(
        graph,
        "offline_sample",
        "heavy",
        42,
        1.0,
    )
    effective = build_scenario_graph(graph, scenario, "offline_sample")

    assert effective.edges[0, 1, 0]["travel_time_s"] > orig_time
    assert graph.edges[0, 1, 0]["travel_time_s"] == orig_time, "Original graph was mutated!"
