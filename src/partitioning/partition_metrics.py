"""Calculation of cut edges, partition balance, and structural quality metrics."""

from collections import defaultdict

import networkx as nx
import numpy as np

from src.partitioning.partition_models import (
    PartitionQualityReport,
    PartitionResult,
    PartitionStatistics,
)


def compute_partition_metrics(
    graph: nx.MultiDiGraph,
    result: PartitionResult,
) -> PartitionQualityReport:
    """Evaluate directed edge cuts, partition balance, and boundary statistics.

    Each directed edge (u, v, key) in the MultiDiGraph is examined:
    If partition(u) != partition(v), it is counted as a cut edge, contributing
    to outgoing cuts for partition(u) and incoming cuts for partition(v).
    Parallel edges and bidirectional pairs are counted individually.
    """
    total_nodes = len(graph)
    total_edges = graph.number_of_edges()
    node_to_partition = result.node_to_partition
    k = result.actual_partition_count

    partition_sizes = {p: len(result.partition_to_nodes.get(p, [])) for p in range(k)}

    # Track edge metrics per partition
    internal_edge_counts: dict[int, int] = defaultdict(int)
    outgoing_cuts: dict[int, int] = defaultdict(int)
    incoming_cuts: dict[int, int] = defaultdict(int)
    internal_length_m: dict[int, float] = defaultdict(float)

    total_cut_edges = 0
    cross_partition_length_m = 0.0

    for u, v, _key, data in graph.edges(keys=True, data=True):
        pu = node_to_partition.get(u)
        pv = node_to_partition.get(v)
        length = float(data.get("length_m", data.get("length", 0.0)))

        if pu is not None and pv is not None and pu != pv:
            total_cut_edges += 1
            cross_partition_length_m += length
            outgoing_cuts[pu] += 1
            incoming_cuts[pv] += 1
        elif pu is not None and pv is not None:
            internal_edge_counts[pu] += 1
            internal_length_m[pu] += length

    cut_edge_ratio = (total_cut_edges / total_edges) if total_edges > 0 else 0.0

    # Balance calculations
    sizes_list = list(partition_sizes.values())
    if sizes_list and total_nodes > 0 and k > 0:
        mean_size = total_nodes / k
        largest_size = max(sizes_list)
        smallest_size = min(sizes_list)
        size_std = float(np.std(sizes_list))
        balance_ratio = (largest_size / mean_size) if mean_size > 0 else 1.0
    else:
        mean_size = 0.0
        largest_size = 0
        smallest_size = 0
        size_std = 0.0
        balance_ratio = 1.0

    empty_count = sum(1 for s in sizes_list if s == 0)

    # Compile partition statistics per partition ID
    stats: dict[int, PartitionStatistics] = {}
    for p in range(k):
        stats[p] = PartitionStatistics(
            partition_id=p,
            node_count=partition_sizes.get(p, 0),
            internal_edge_count=internal_edge_counts[p],
            outgoing_cut_edges=outgoing_cuts[p],
            incoming_cut_edges=incoming_cuts[p],
            total_road_length_m=round(internal_length_m[p], 3),
        )

    return PartitionQualityReport(
        total_nodes=total_nodes,
        total_edges=total_edges,
        partition_sizes=partition_sizes,
        cut_edge_count=total_cut_edges,
        cut_edge_ratio=round(cut_edge_ratio, 6),
        partition_balance_ratio=round(balance_ratio, 6),
        partition_size_std=round(size_std, 4),
        largest_partition_size=largest_size,
        smallest_partition_size=smallest_size,
        empty_partition_count=empty_count,
        cross_partition_road_length_m=round(cross_partition_length_m, 3),
        partition_statistics=stats,
    )
