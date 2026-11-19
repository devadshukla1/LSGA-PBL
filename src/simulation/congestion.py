"""Reproducible synthetic edge multipliers."""

import random

from src.algorithms.routing_tiebreak import signature


def generate_congestion(graph, scenario) -> dict:
    edges = sorted(graph.edges(keys=True), key=lambda e: signature((e,)))
    rng = random.Random(scenario.random_seed)
    selected = set(rng.sample(edges, int(len(edges) * scenario.congestion_coverage)))
    return {edge: rng.uniform(*scenario.parameters) if edge in selected else 1.0 for edge in edges}
