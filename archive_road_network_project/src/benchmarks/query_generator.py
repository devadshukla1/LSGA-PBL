"""Reproducible origin-destination query generation with directed reachability verification."""

import random
from collections.abc import Hashable

import networkx as nx

from src.benchmarks.benchmark_models import BenchmarkQuery


def generate_benchmark_queries(
    graph: nx.MultiDiGraph,
    count: int = 30,
    seed: int = 42,
    objective: str = "distance",
) -> list[BenchmarkQuery]:
    """Generate reproducible, directed-reachable (source, target) query pairs.

    1. Uses a fixed random seed.
    2. Enforces source != destination.
    3. Verifies directed path existence using NetworkX.
    4. Computes ground-truth reference cost via NetworkX oracle.
    5. Handles small graphs where reachable pairs may be fewer than requested count.
    """
    total_nodes = len(graph)
    if total_nodes < 2:
        return []

    weight_field = "length_m" if objective == "distance" else "travel_time_s"
    rng = random.Random(seed)
    all_nodes = sorted(graph.nodes, key=lambda n: str(n))

    # Pre-filter by strongly connected components to accelerate reachable pair selection
    sccs = [scc for scc in nx.strongly_connected_components(graph) if len(scc) >= 2]
    candidate_pairs: list[tuple[Hashable, Hashable]] = []

    # First, collect candidate pairs from large strongly connected components
    for scc in sccs:
        scc_nodes = sorted(scc, key=lambda n: str(n))
        for i, u in enumerate(scc_nodes):
            for v in scc_nodes[i + 1 :]:
                candidate_pairs.append((u, v))
                candidate_pairs.append((v, u))

    # Shuffle deterministically
    rng.shuffle(candidate_pairs)

    selected_pairs: list[tuple[Hashable, Hashable]] = []
    seen: set[tuple[Hashable, Hashable]] = set()

    for u, v in candidate_pairs:
        if (u, v) not in seen and u != v and nx.has_path(graph, u, v):
            seen.add((u, v))
            selected_pairs.append((u, v))
            if len(selected_pairs) >= count:
                break

    # If still need pairs, check node combinations directly or sample
    if len(selected_pairs) < count:
        if total_nodes <= 50:
            # Deterministic scan of all pairs for small graphs
            all_pairs = [(u, v) for u in all_nodes for v in all_nodes if u != v]
            rng.shuffle(all_pairs)
            for u, v in all_pairs:
                if (u, v) not in seen and nx.has_path(graph, u, v):
                    seen.add((u, v))
                    selected_pairs.append((u, v))
                    if len(selected_pairs) >= count:
                        break
        else:
            attempts = 0
            max_attempts = max(1000, count * 50)
            while len(selected_pairs) < count and attempts < max_attempts:
                attempts += 1
                u = rng.choice(all_nodes)
                v = rng.choice(all_nodes)
                if u != v and (u, v) not in seen and nx.has_path(graph, u, v):
                    seen.add((u, v))
                    selected_pairs.append((u, v))

    # Compile BenchmarkQuery objects with ground-truth reference costs
    queries: list[BenchmarkQuery] = []
    for q_id, (source, target) in enumerate(selected_pairs):
        ref_cost = nx.shortest_path_length(graph, source, target, weight=weight_field)
        queries.append(
            BenchmarkQuery(
                query_id=q_id,
                source=source,
                target=target,
                is_reachable=True,
                reference_cost=float(ref_cost),
            )
        )

    return queries


def generate_unreachable_queries(
    graph: nx.MultiDiGraph,
    count: int = 5,
    seed: int = 42,
) -> list[BenchmarkQuery]:
    """Generate deterministic unreachable query pairs for correctness verification."""
    total_nodes = len(graph)
    if total_nodes < 2:
        return []

    rng = random.Random(seed)
    all_nodes = sorted(graph.nodes, key=lambda n: str(n))
    unreachable_pairs: list[tuple[Hashable, Hashable]] = []
    seen: set[tuple[Hashable, Hashable]] = set()

    # Search for pairs where no directed path exists
    for _ in range(min(500, total_nodes * total_nodes)):
        u = rng.choice(all_nodes)
        v = rng.choice(all_nodes)
        if u != v and (u, v) not in seen and not nx.has_path(graph, u, v):
            seen.add((u, v))
            unreachable_pairs.append((u, v))
            if len(unreachable_pairs) >= count:
                break

    queries: list[BenchmarkQuery] = []
    for q_id, (source, target) in enumerate(unreachable_pairs):
        queries.append(
            BenchmarkQuery(
                query_id=q_id,
                source=source,
                target=target,
                is_reachable=False,
                reference_cost=None,
            )
        )
    return queries
