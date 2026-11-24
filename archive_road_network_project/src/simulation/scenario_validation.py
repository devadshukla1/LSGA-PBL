"""Validate scenario data against its exact dataset snapshot."""

import hashlib
import json
import math
import re
from dataclasses import asdict

from src.algorithms.routing_tiebreak import signature
from src.graph.storage import encoded

RANGES = {"normal": (1.0, 1.0), "light": (1.15, 1.35), "moderate": (1.4, 1.8), "heavy": (1.9, 2.8)}


def fingerprint(graph) -> str:
    """Digest baseline topology, weights, geometry, and metadata."""
    nodes = sorted((n, encoded(d)) for n, d in graph.nodes(data=True))
    edges = sorted(
        ((u, v, k, encoded(d)) for u, v, k, d in graph.edges(keys=True, data=True)),
        key=lambda e: signature((e[:3],)),
    )
    return hashlib.sha256(
        json.dumps([encoded(graph.graph), nodes, edges], sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


def identity(scenario) -> str:
    data = asdict(scenario)
    for field in ("scenario_id", "created_at", "scenario_name"):
        data.pop(field)
    return hashlib.sha256(json.dumps(data, sort_keys=True, allow_nan=False).encode()).hexdigest()[
        :24
    ]


def validate_scenario(graph, scenario, dataset_id: str) -> None:
    if scenario.schema_version != 1 or type(scenario.schema_version) is not int:
        raise ValueError("Unsupported scenario schema")
    if scenario.dataset_id != dataset_id or scenario.dataset_fingerprint != fingerprint(graph):
        raise ValueError("Scenario dataset identity or fingerprint mismatch")
    if scenario.congestion_level not in RANGES or type(scenario.random_seed) is not int:
        raise ValueError("Invalid congestion level or seed")
    coverage = scenario.congestion_coverage
    if type(coverage) not in (int, float) or not math.isfinite(coverage) or not 0 <= coverage <= 1:
        raise ValueError("Coverage must be finite and between zero and one")
    if len(scenario.parameters) != 2 or any(
        type(x) not in (int, float) or not math.isfinite(x) or x < 1 for x in scenario.parameters
    ):
        raise ValueError("Invalid multiplier range")
    if scenario.parameters[0] > scenario.parameters[1]:
        raise ValueError("Reversed multiplier range")
    if scenario.congestion_level == "normal" and scenario.parameters != (1.0, 1.0):
        raise ValueError("Normal traffic requires multiplier one")
    if len(set(scenario.closed_edges)) != len(scenario.closed_edges):
        raise ValueError("Duplicate closures")
    if len(set(scenario.blocked_nodes)) != len(scenario.blocked_nodes):
        raise ValueError("Duplicate blocked nodes")
    for edge in scenario.closed_edges:
        if len(edge) != 3 or any(type(n) is not int for n in edge) or not graph.has_edge(*edge):
            raise ValueError("Unknown directed edge closure")
    if any(type(n) is not int or n not in graph for n in scenario.blocked_nodes):
        raise ValueError("Unknown blocked junction")
    if (
        not re.fullmatch(r"[a-f0-9]{24}", scenario.scenario_id)
        or identity(scenario) != scenario.scenario_id
    ):
        raise ValueError("Invalid scenario identity")
