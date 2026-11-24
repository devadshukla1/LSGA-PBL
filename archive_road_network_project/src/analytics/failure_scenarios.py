"""Static baseline attack rankings and seeded sampling without replacement."""

import random

from src.algorithms.traversal_models import canonical
from src.analytics.analytics_models import FailureScenario


def failure_scenario(graph, count, strategy="random", scores=None, seed=42) -> FailureScenario:
    if type(count) is not int or not 0 <= count <= len(graph):
        raise ValueError("Failure count must be an integer within graph size")
    nodes = sorted(graph, key=canonical)
    if strategy == "random":
        if type(seed) is not int:
            raise ValueError("Seed must be an integer")
        removed = random.Random(seed).sample(nodes, count)
    else:
        if (
            strategy not in ("degree", "betweenness", "combined")
            or scores is None
            or set(scores) != set(graph)
        ):
            raise ValueError("Targeted failures require a complete static baseline ranking")
        removed = sorted(nodes, key=lambda n: (-scores[n], canonical(n)))[:count]
    return FailureScenario(strategy, tuple(removed), seed if strategy == "random" else None)
