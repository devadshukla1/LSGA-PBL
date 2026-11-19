import copy
from dataclasses import replace

import networkx as nx
import pytest

from src.graph.dataset_service import load
from src.simulation.scenario_builder import build_scenario_graph, create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.scenario_storage import (
    delete_scenario,
    list_scenarios,
    load_scenario,
    save_scenario,
)
from src.simulation.simulation_engine import simulate


@pytest.mark.parametrize("level", ["normal", "light", "moderate", "heavy"])
@pytest.mark.parametrize("algorithm", ["dijkstra", "astar", "bidirectional_dijkstra"])
def test_effective_oracle_and_immutability(level, algorithm):
    info = load()
    graph = info.graph
    snapshot = copy.deepcopy(graph)
    scenario = create_scenario(graph, "offline_sample", level, coverage=1)
    effective = build_scenario_graph(graph, scenario)
    assert nx.utils.graphs_equal(effective, build_scenario_graph(graph, scenario))
    for objective, field in (("travel_time", "travel_time_s"), ("distance", "length_m")):
        result = simulate(graph, scenario, SimulationRequest(0, 1, algorithm, objective))
        assert result.scenario_route.optimized_cost == pytest.approx(
            nx.shortest_path_length(effective, 0, 1, weight=field)
        )
    assert nx.utils.graphs_equal(graph, snapshot)


def test_closures_blocked_and_persistence(tmp_path):
    graph = load().graph
    scenario = create_scenario(graph, "offline_sample", closed_edges=((0, 1, 7),))
    result = simulate(graph, scenario, SimulationRequest(0, 1))
    assert result.scenario_route.edge_path == ((0, 1, 0),)
    assert result.comparison["baseline_route_scenario_time"] is None
    assert result.comparison["travel_time_difference_s"] == pytest.approx(4.32)
    effective = build_scenario_graph(graph, scenario)
    assert effective.has_edge(0, 1, 0) and not effective.has_edge(0, 1, 7)
    save_scenario(scenario, graph, "offline_sample", tmp_path)
    assert load_scenario(scenario.scenario_id, graph, "offline_sample", tmp_path) == scenario
    assert list_scenarios(tmp_path) == [scenario.scenario_id]
    delete_scenario(scenario.scenario_id, tmp_path)
    assert list_scenarios(tmp_path) == []
    blocked = create_scenario(graph, "offline_sample", blocked_nodes=(0,))
    assert simulate(graph, blocked, SimulationRequest(0, 1)).status == "blocked_endpoint"
    with pytest.raises(ValueError):
        build_scenario_graph(graph, scenario, "wrong")
    for kwargs in (
        {"coverage": float("nan")},
        {"coverage": -1},
        {"seed": True},
        {"closed_edges": ((0, 1, 999),)},
        {"blocked_nodes": (999,)},
        {"closed_edges": ((0, 1, 0), (0, 1, 0))},
        {"parameters": (0, 2)},
    ):
        with pytest.raises(ValueError):
            create_scenario(graph, "offline_sample", **kwargs)
    with pytest.raises(ValueError):
        build_scenario_graph(graph, replace(scenario, schema_version=2))


def test_normal_zero_unreachable_and_identity():
    graph = load().graph
    a = create_scenario(graph, "offline_sample", "normal")
    b = create_scenario(graph, "offline_sample", "normal")
    assert a.scenario_id == b.scenario_id
    result = simulate(graph, a, SimulationRequest(0, 1))
    assert result.comparison["travel_time_difference_s"] == 0
    assert result.comparison["rerouting_time_saved"] == 0
    assert simulate(graph, a, SimulationRequest(0, 15)).comparison["scenario_travel_time_s"] is None
    assert (
        simulate(graph, a, SimulationRequest(0, 0)).comparison["travel_time_change_percent"] is None
    )
