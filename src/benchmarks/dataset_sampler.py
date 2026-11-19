"""Deterministic graph-size sampling and dataset preparation for benchmarking."""

import collections
import random
from collections.abc import Hashable

import networkx as nx

from src.benchmarks.benchmark_models import BenchmarkDataset


def _sample_connected_subgraph(
    graph: nx.MultiDiGraph,
    target_size: int,
    seed: int = 42,
) -> nx.MultiDiGraph:
    """Extract an induced directed subgraph of exact target size via connected expansion.

    1. Starts at a deterministic high-degree node.
    2. Expands breadth-first across the undirected neighborhood.
    3. Handles disconnected components by selecting subsequent seeds if needed.
    4. Induces the directed MultiDiGraph preserving all original edge keys and attributes.
    """
    total_nodes = len(graph)
    if target_size > total_nodes:
        raise ValueError(
            f"Requested sample size {target_size} exceeds source graph size {total_nodes}"
        )
    if target_size <= 0:
        raise ValueError(f"Target size must be positive, got {target_size}")
    if target_size == total_nodes:
        return graph.copy()

    # Deterministic start node selection
    rng = random.Random(seed)
    candidates = sorted(graph.nodes, key=lambda n: (-graph.degree(n), str(n)))
    # Seeded pick among top candidates
    top_k = min(10, len(candidates))
    start_node = candidates[rng.randint(0, top_k - 1)]

    # Build undirected neighbor lookup
    undirected_neighbors: dict[Hashable, set[Hashable]] = {n: set() for n in graph.nodes}
    for u, v in graph.edges():
        if u != v:
            undirected_neighbors[u].add(v)
            undirected_neighbors[v].add(u)

    visited: set[Hashable] = {start_node}
    queue: collections.deque[Hashable] = collections.deque([start_node])

    while len(visited) < target_size and queue:
        curr = queue.popleft()
        # Sort neighbors deterministically
        nbrs = sorted(undirected_neighbors[curr], key=lambda n: str(n))
        for nbr in nbrs:
            if nbr not in visited:
                visited.add(nbr)
                queue.append(nbr)
                if len(visited) >= target_size:
                    break

    # If queue emptied before reaching target_size (disconnected components)
    if len(visited) < target_size:
        remaining = [n for n in candidates if n not in visited]
        for node in remaining:
            visited.add(node)
            if len(visited) >= target_size:
                break

    # Construct the induced directed MultiDiGraph copy
    subgraph = graph.subgraph(visited).copy()
    if "crs" in graph.graph:
        subgraph.graph["crs"] = graph.graph["crs"]
    return subgraph


def prepare_benchmark_datasets(
    graph: nx.MultiDiGraph,
    base_dataset_id: str,
    target_sizes: list[int],
    seed: int = 42,
    origin_label: str = "offline",
) -> list[BenchmarkDataset]:
    """Prepare multiple benchmark datasets corresponding to available graph sizes.

    For requested sizes smaller than graph, generates deterministic induced subgraphs.
    If requested size exceeds graph, skips it without fabricating data.
    Always includes the full original graph if no target sizes are smaller.
    """
    total_nodes = len(graph)
    datasets: list[BenchmarkDataset] = []

    # Filter target sizes
    valid_sub_sizes = sorted({s for s in target_sizes if 0 < s < total_nodes})

    for size in valid_sub_sizes:
        sub = _sample_connected_subgraph(graph, size, seed=seed)
        edge_count = sub.number_of_edges()
        density = (edge_count / (size * (size - 1))) if size > 1 else 0.0
        datasets.append(
            BenchmarkDataset(
                dataset_id=f"{base_dataset_id}_n{size}",
                dataset_origin=f"{origin_label} (sampled {size})",
                node_count=size,
                edge_count=edge_count,
                directed_density=round(density, 6),
                weak_component_count=nx.number_weakly_connected_components(sub),
                strong_component_count=nx.number_strongly_connected_components(sub),
                sampling_method="connected_region_expansion",
                random_seed=seed,
                graph=sub,
            )
        )

    # Full graph representation
    full_edge_count = graph.number_of_edges()
    full_density = (full_edge_count / (total_nodes * (total_nodes - 1))) if total_nodes > 1 else 0.0
    datasets.append(
        BenchmarkDataset(
            dataset_id=f"{base_dataset_id}_full",
            dataset_origin=f"{origin_label} (full)",
            node_count=total_nodes,
            edge_count=full_edge_count,
            directed_density=round(full_density, 6),
            weak_component_count=nx.number_weakly_connected_components(graph),
            strong_component_count=nx.number_strongly_connected_components(graph),
            sampling_method="full_dataset",
            random_seed=None,
            graph=graph.copy(),
        )
    )

    return datasets
