"""Build isolated effective-weight graph snapshots."""

import copy
import math
from dataclasses import replace
from datetime import UTC, datetime

from src.simulation.congestion import generate_congestion
from src.simulation.disruptions import apply_disruptions
from src.simulation.scenario_models import TrafficScenario
from src.simulation.scenario_validation import RANGES, fingerprint, identity, validate_scenario


def create_scenario(
    graph,
    dataset_id,
    level="normal",
    seed=42,
    coverage=0.5,
    closed_edges=(),
    blocked_nodes=(),
    name="Traffic scenario",
    parameters=None,
):
    scenario = TrafficScenario(
        "",
        name,
        dataset_id,
        fingerprint(graph),
        level,
        seed,
        coverage,
        tuple(sorted(closed_edges)),
        tuple(sorted(blocked_nodes)),
        tuple(parameters) if parameters is not None else RANGES.get(level, ()),
        datetime.now(UTC).isoformat(),
    )
    scenario = replace(scenario, scenario_id=identity(scenario))
    validate_scenario(graph, scenario, dataset_id)
    return scenario


def build_scenario_graph(base_graph, scenario, dataset_id=None):
    validate_scenario(base_graph, scenario, dataset_id or scenario.dataset_id)
    effective = copy.deepcopy(base_graph)
    factors = generate_congestion(base_graph, scenario)
    for edge, multiplier in factors.items():
        data = effective.edges[edge]
        original = data["travel_time_s"]
        adjusted = original * multiplier
        if not math.isfinite(adjusted) or adjusted < 0:
            raise ValueError("Nonfinite or negative effective travel time")
        data.update(
            base_travel_time_s=original,
            effective_travel_time_s=adjusted,
            congestion_multiplier=multiplier,
            travel_time_s=adjusted,
        )
    apply_disruptions(effective, scenario)
    return effective
