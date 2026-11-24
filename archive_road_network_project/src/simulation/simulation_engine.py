"""Scenario routing coordinated through the existing routing service."""

from src.routing.routing_service import find_route
from src.simulation.scenario_builder import build_scenario_graph
from src.simulation.scenario_models import SimulationResult
from src.simulation.simulation_comparison import compare_simulation


def simulate(graph, scenario, request, dataset_id=None) -> SimulationResult:
    effective = build_scenario_graph(graph, scenario, dataset_id)
    baseline = find_route(
        graph, request.source, request.target, request.algorithm, request.objective
    )
    blocked = request.source in scenario.blocked_nodes or request.target in scenario.blocked_nodes
    route = (
        None
        if blocked
        else find_route(
            effective, request.source, request.target, request.algorithm, request.objective
        )
    )
    return SimulationResult(
        baseline,
        route,
        "blocked_endpoint" if blocked else route.status,
        compare_simulation(baseline, route, effective),
    )
