"""Static targeted versus random failures using equal removal budgets."""

import math
import random
import statistics
from dataclasses import asdict

import networkx as nx

from src.algorithms.bfs import bfs
from src.algorithms.traversal_models import prepare
from src.analytics.connectivity import connectivity_summary
from src.analytics.failure_scenarios import failure_scenario


def failure_impact(graph, scenario, seed=42, exact_threshold=100, pair_samples=200) -> dict:
    if type(pair_samples) is not int or pair_samples < 1:
        raise ValueError("Pair sample count must be positive")
    if len(set(scenario.removed_nodes)) != len(scenario.removed_nodes) or any(
        n not in graph for n in scenario.removed_nodes
    ):
        raise ValueError("Invalid failed junctions")
    removed = set(scenario.removed_nodes)
    view = nx.subgraph_view(graph, filter_node=lambda n: n not in removed)
    summary = connectivity_summary(view)
    roads = prepare(view)
    nodes = list(roads)
    n = len(nodes)
    approximate = n > exact_threshold
    denominator = n * (n - 1)
    reachable = 0
    sample_count = denominator
    if denominator and not approximate:
        reachable = sum(bfs(roads, node).reachable_count - 1 for node in nodes)
    elif denominator:
        rng = random.Random(seed)
        pairs = [tuple(rng.sample(nodes, 2)) for _ in range(pair_samples)]
        grouped = {}
        for source, target in pairs:
            grouped.setdefault(source, []).append(target)
        for source, targets in grouped.items():
            visited = bfs(roads, source).visited_nodes
            reachable += sum(t in visited for t in targets)
        sample_count = pair_samples
    row = asdict(summary)
    row.update(
        failure_type=scenario.failure_type,
        removed_nodes=scenario.removed_nodes,
        remaining_nodes=n,
        remaining_edges=view.number_of_edges(),
        original_largest_weak_fraction=summary.largest_weak_component_size / len(graph)
        if len(graph)
        else 0,
        original_largest_strong_fraction=summary.largest_strong_component_size / len(graph)
        if len(graph)
        else 0,
        fragmentation_score=1 - summary.largest_weak_component_fraction if n else 1.0,
        reachable_pair_fraction=reachable / sample_count if sample_count else 0,
        reachability_approximate=approximate,
        sample_size=sample_count,
        seed=seed,
        denominator="ordered distinct surviving junction pairs",
    )
    return row


def resilience_experiment(
    graph,
    scores,
    strategy="degree",
    levels=(0, 0.05, 0.1, 0.15, 0.2),
    seed=42,
    repetitions=10,
    max_repetitions=30,
) -> list[dict]:
    if type(repetitions) is not int or not 2 <= repetitions <= max_repetitions:
        raise ValueError("Use 2 through 30 random repetitions")
    if len(levels) > 10 or any(not math.isfinite(x) or not 0 <= x <= 1 for x in levels):
        raise ValueError("Use at most ten failure fractions between zero and one")
    rows = []
    for level in levels:
        count = math.floor(len(graph) * level)
        targeted = failure_impact(graph, failure_scenario(graph, count, strategy, scores), seed)
        random_runs = [
            failure_impact(graph, failure_scenario(graph, count, seed=seed + i), seed + i)
            for i in range(repetitions)
        ]
        row = {
            "Failure percentage": level * 100,
            "Removed nodes": count,
            "Targeted retention": targeted["original_largest_weak_fraction"],
            "Targeted weak components": targeted["weak_component_count"],
            "Targeted reachable pairs": targeted["reachable_pair_fraction"],
            "Targeted fragmentation": targeted["fragmentation_score"],
            "Targeted survivor fraction": targeted["largest_weak_component_fraction"],
            "Reachability approximate": targeted["reachability_approximate"],
        }
        for label, key in (
            ("retention", "original_largest_weak_fraction"),
            ("weak components", "weak_component_count"),
            ("reachable pairs", "reachable_pair_fraction"),
        ):
            values = [r[key] for r in random_runs]
            row.update(
                {
                    f"Random mean {label}": statistics.mean(values),
                    f"Random std {label}": statistics.pstdev(values),
                    f"Random min {label}": min(values),
                    f"Random max {label}": max(values),
                }
            )
        rows.append(row)
    return rows
