"""Focused benchmark suite for graph partitioning and spatial indexing performance."""

import statistics
import time
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from src.indexing.nearest_node import brute_force_nearest_node
from src.indexing.spatial_index import build_spatial_index, extract_node_coordinates
from src.partitioning.geographic import geographic_partition
from src.partitioning.graph_aware import graph_aware_partition


@dataclass(frozen=True)
class TimingStats:
    """Summary statistics for repeated timing measurements."""

    mean_s: float
    median_s: float
    std_s: float
    min_s: float
    max_s: float
    repetitions: int


def _compute_stats(samples: list[float]) -> TimingStats:
    """Compute summary statistics for a list of execution times in seconds."""
    if not samples:
        return TimingStats(0.0, 0.0, 0.0, 0.0, 0.0, 0)
    mean = statistics.mean(samples)
    med = statistics.median(samples)
    std = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return TimingStats(
        mean_s=round(mean, 6),
        median_s=round(med, 6),
        std_s=round(std, 6),
        min_s=round(min(samples), 6),
        max_s=round(max(samples), 6),
        repetitions=len(samples),
    )


@dataclass(frozen=True)
class PartitionBenchmarkReport:
    """Complete benchmark report comparing partitioning algorithms and spatial indexing."""

    geographic_time: TimingStats
    graph_aware_time: TimingStats
    index_build_time: TimingStats
    brute_force_query_time: TimingStats
    indexed_query_time: TimingStats
    query_speedup: float
    correctness_verified: bool
    k: int
    node_count: int
    edge_count: int
    query_count: int
    details: dict[str, Any] = field(default_factory=dict)


def run_partition_benchmarks(
    graph: nx.MultiDiGraph,
    k: int = 4,
    repetitions: int = 5,
    seed: int = 42,
    query_coordinates: list[tuple[float, float]] | None = None,
) -> PartitionBenchmarkReport:
    """Benchmark partitioning runtimes, spatial index construction, and query latencies.

    Verifies nearest-node correctness between KD-tree and brute-force before
    computing speedup ratios.
    """
    if len(graph) == 0:
        raise ValueError("Cannot benchmark an empty graph")

    # 1. Benchmark Geographic Partitioning
    geo_times: list[float] = []
    for _ in range(repetitions):
        t0 = time.perf_counter()
        geographic_partition(graph, k=k, seed=seed)
        geo_times.append(time.perf_counter() - t0)

    # 2. Benchmark Graph-Aware Partitioning
    aware_times: list[float] = []
    for _ in range(repetitions):
        t0 = time.perf_counter()
        graph_aware_partition(graph, k=k, seed=seed)
        aware_times.append(time.perf_counter() - t0)

    # 3. Benchmark Spatial Index Construction
    index_build_times: list[float] = []
    spatial_index = None
    for _ in range(repetitions):
        t0 = time.perf_counter()
        idx = build_spatial_index(graph)
        index_build_times.append(time.perf_counter() - t0)
        spatial_index = idx

    assert spatial_index is not None

    # Determine query coordinates
    coords = extract_node_coordinates(graph)
    if query_coordinates is None:
        # Use node coordinates slightly perturbed, plus centroid
        lats = [c[0] for c in coords.values()]
        lons = [c[1] for c in coords.values()]
        mid_lat = sum(lats) / len(lats)
        mid_lon = sum(lons) / len(lons)
        query_coordinates = [
            (mid_lat, mid_lon),
            (min(lats) + 0.0001, min(lons) + 0.0001),
            (max(lats) - 0.0001, max(lons) - 0.0001),
            (lats[0], lons[0]),
        ]

    # Verify correctness before measuring query timings
    correctness_verified = True
    for q_lat, q_lon in query_coordinates:
        res_bf = brute_force_nearest_node(graph, q_lat, q_lon)
        res_idx = spatial_index.nearest_node(q_lat, q_lon)
        if res_bf.node_id != res_idx.node_id or abs(res_bf.distance_m - res_idx.distance_m) > 0.05:
            correctness_verified = False
            break

    # 4. Benchmark Brute-Force Query Latency (strictly query time, no index build)
    bf_query_times: list[float] = []
    for _ in range(repetitions):
        t0 = time.perf_counter()
        for q_lat, q_lon in query_coordinates:
            brute_force_nearest_node(graph, q_lat, q_lon)
        bf_query_times.append(time.perf_counter() - t0)

    # 5. Benchmark Indexed Query Latency (strictly query time, tree already built)
    idx_query_times: list[float] = []
    for _ in range(repetitions):
        t0 = time.perf_counter()
        for q_lat, q_lon in query_coordinates:
            spatial_index.nearest_node(q_lat, q_lon)
        idx_query_times.append(time.perf_counter() - t0)

    bf_stats = _compute_stats(bf_query_times)
    idx_stats = _compute_stats(idx_query_times)

    speedup = (
        (bf_stats.mean_s / idx_stats.mean_s)
        if (idx_stats.mean_s > 0 and correctness_verified)
        else 1.0
    )

    return PartitionBenchmarkReport(
        geographic_time=_compute_stats(geo_times),
        graph_aware_time=_compute_stats(aware_times),
        index_build_time=_compute_stats(index_build_times),
        brute_force_query_time=bf_stats,
        indexed_query_time=idx_stats,
        query_speedup=round(speedup, 3),
        correctness_verified=correctness_verified,
        k=k,
        node_count=len(graph),
        edge_count=graph.number_of_edges(),
        query_count=len(query_coordinates),
    )
