"""Graph-aware partitioning using balanced multi-source region growing and boundary refinement."""

import collections
import math
import time
from collections import defaultdict
from collections.abc import Hashable

import networkx as nx

from src.indexing.spatial_index import extract_node_coordinates, haversine_m
from src.partitioning.partition_models import PartitionResult


def _build_undirected_adjacency(graph: nx.MultiDiGraph) -> dict[Hashable, set[Hashable]]:
    """Construct an undirected neighbor view collapsing parallel and opposite edges."""
    neighbors: dict[Hashable, set[Hashable]] = {n: set() for n in graph.nodes}
    for u, v in graph.edges():
        if u != v:
            neighbors[u].add(v)
            neighbors[v].add(u)
    return neighbors


def _select_seeds(
    neighbors: dict[Hashable, set[Hashable]],
    coords: dict[Hashable, tuple[float, float]],
    k: int,
) -> list[Hashable]:
    """Select K dispersed seed nodes deterministically using farthest-point selection."""
    nodes_sorted = sorted(neighbors.keys(), key=lambda n: (-len(neighbors[n]), str(n)))
    seeds: list[Hashable] = [nodes_sorted[0]]

    # For subsequent seeds, maximize minimum distance to already chosen seeds
    while len(seeds) < k:
        best_candidate = None
        best_min_dist = -1.0

        for candidate in nodes_sorted:
            if candidate in seeds:
                continue

            # Compute min distance to existing seeds using BFS hop count, falling back to geographic
            min_dist_to_seeds = math.inf
            for s in seeds:
                # Calculate hop distance or fallback to geographic
                cand_lat, cand_lon = coords[candidate]
                seed_lat, seed_lon = coords[s]
                geo_dist = haversine_m(cand_lat, cand_lon, seed_lat, seed_lon)
                min_dist_to_seeds = min(min_dist_to_seeds, geo_dist)

            if min_dist_to_seeds > best_min_dist:
                best_min_dist = min_dist_to_seeds
                best_candidate = candidate

        seeds.append(best_candidate if best_candidate is not None else nodes_sorted[len(seeds)])

    return seeds


def graph_aware_partition(
    graph: nx.MultiDiGraph,
    k: int,
    seed: int = 42,
    balance_tolerance: float = 0.05,
    max_refinement_passes: int = 3,
) -> PartitionResult:
    """Partition a road network using deterministic balanced region growing and boundary refinement.

    1. Constructs a temporary undirected neighbor view preserving original directed edges.
    2. Identifies K dispersed seed nodes.
    3. Concurrently expands partitions via breadth-first search while enforcing capacity limits.
    4. Handles disconnected components and isolates to assign all nodes.
    5. Executes bounded boundary refinement to reduce cut edges while respecting
       balance constraints.

    Args:
        graph: Original directed MultiDiGraph.
        k: Number of partitions (1 <= K <= len(graph)).
        seed: Random seed (retained for parameter consistency).
        balance_tolerance: Allowed fractional deviation from ideal partition size.
        max_refinement_passes: Upper bound on boundary refinement passes.

    Returns:
        PartitionResult containing node assignments and diagnostics.
    """
    total_nodes = len(graph)
    if total_nodes == 0:
        raise ValueError("Cannot partition an empty graph")
    if k < 1:
        raise ValueError(f"Partition count K must be >= 1, got {k}")
    if k > total_nodes:
        raise ValueError(f"Partition count K={k} cannot exceed node count {total_nodes}")

    start_time = time.perf_counter()
    coords = extract_node_coordinates(graph)
    neighbors = _build_undirected_adjacency(graph)

    # Determine target capacities for strict balance
    base_cap = total_nodes // k
    remainder = total_nodes % k
    target_sizes = {p: base_cap + (1 if p < remainder else 0) for p in range(k)}

    # Select seeds
    seeds = _select_seeds(neighbors, coords, k)

    # Multi-source BFS region growing
    node_to_partition: dict[Hashable, int] = {}
    partition_sizes: dict[int, int] = {p: 0 for p in range(k)}
    queues: dict[int, collections.deque[Hashable]] = {p: collections.deque() for p in range(k)}

    for p, s in enumerate(seeds):
        node_to_partition[s] = p
        partition_sizes[p] = 1
        queues[p].append(s)

    assigned_count = len(seeds)

    # Round-robin expansion
    while assigned_count < total_nodes:
        progress = False
        for p in range(k):
            if partition_sizes[p] >= target_sizes[p]:
                continue
            if not queues[p]:
                continue

            curr = queues[p].popleft()
            for nbr in sorted(neighbors[curr], key=lambda n: str(n)):
                if nbr not in node_to_partition and partition_sizes[p] < target_sizes[p]:
                    node_to_partition[nbr] = p
                    partition_sizes[p] += 1
                    queues[p].append(nbr)
                    assigned_count += 1
                    progress = True
                    if partition_sizes[p] >= target_sizes[p]:
                        break

        if not progress and assigned_count < total_nodes:
            # Handle disconnected components or empty queues:
            # Find an unassigned node adjacent to an existing partition or smallest partition
            unassigned = [n for n in graph.nodes if n not in node_to_partition]
            unassigned.sort(key=lambda n: str(n))

            best_node = None
            best_target_p = None

            # Prioritize an unassigned node with neighbors in a partition that has capacity
            for node in unassigned:
                incident_partitions = {
                    node_to_partition[nbr] for nbr in neighbors[node] if nbr in node_to_partition
                }
                candidates = [
                    p for p in incident_partitions if partition_sizes[p] < target_sizes[p]
                ]
                if candidates:
                    best_node = node
                    best_target_p = min(candidates, key=lambda p: (partition_sizes[p], p))
                    break

            if best_node is None:
                # Assign unassigned node with highest degree to current smallest partition
                best_node = min(
                    unassigned,
                    key=lambda n: (-len(neighbors[n]), str(n)),
                )
                best_target_p = min(
                    range(k),
                    key=lambda p: (partition_sizes[p], p),
                )

            node_to_partition[best_node] = best_target_p
            partition_sizes[best_target_p] += 1
            queues[best_target_p].append(best_node)
            assigned_count += 1

    # Bounded boundary refinement pass
    ideal_size = total_nodes / k
    max_imbalance = max(1, int(math.ceil(balance_tolerance * ideal_size)))

    for _pass in range(max_refinement_passes):
        moves_made = 0
        boundary_nodes = [
            n
            for n in graph.nodes
            if any(node_to_partition[nbr] != node_to_partition[n] for nbr in neighbors[n])
        ]
        boundary_nodes.sort(key=lambda n: str(n))

        for u in boundary_nodes:
            curr_p = node_to_partition[u]
            if partition_sizes[curr_p] <= 1:
                continue

            # Calculate connections to current and other partitions
            p_counts: dict[int, int] = defaultdict(int)
            for nbr in neighbors[u]:
                p_counts[node_to_partition[nbr]] += 1

            curr_connections = p_counts[curr_p]

            for other_p, other_connections in p_counts.items():
                if other_p == curr_p:
                    continue
                gain = other_connections - curr_connections
                if gain > 0:
                    # Check balance constraint
                    new_curr = partition_sizes[curr_p] - 1
                    new_other = partition_sizes[other_p] + 1
                    if (
                        abs(new_curr - ideal_size) <= max_imbalance
                        and abs(new_other - ideal_size) <= max_imbalance
                    ):
                        node_to_partition[u] = other_p
                        partition_sizes[curr_p] -= 1
                        partition_sizes[other_p] += 1
                        moves_made += 1
                        break

        if moves_made == 0:
            break

    # Compile partition_to_nodes
    partition_to_nodes: dict[int, list[Hashable]] = defaultdict(list)
    for n, p in node_to_partition.items():
        partition_to_nodes[p].append(n)

    for p in range(k):
        partition_to_nodes[p].sort(key=lambda n: str(n))

    elapsed = time.perf_counter() - start_time

    return PartitionResult(
        algorithm="graph_aware",
        requested_partition_count=k,
        actual_partition_count=k,
        node_to_partition=node_to_partition,
        partition_to_nodes=dict(partition_to_nodes),
        parameters={
            "seed": seed,
            "balance_tolerance": balance_tolerance,
            "max_refinement_passes": max_refinement_passes,
        },
        runtime_seconds=round(elapsed, 6),
    )
