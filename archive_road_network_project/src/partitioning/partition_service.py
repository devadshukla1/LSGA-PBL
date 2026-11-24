"""Service facade for partitioning execution, validation, and comparative analysis."""

from typing import Any

import networkx as nx

from src.partitioning.geographic import geographic_partition
from src.partitioning.graph_aware import graph_aware_partition
from src.partitioning.partition_metrics import compute_partition_metrics
from src.partitioning.partition_models import (
    PartitionComparisonResult,
    PartitionQualityReport,
    PartitionResult,
)
from src.partitioning.partition_validation import assert_valid_partition


def partition_graph(
    graph: nx.MultiDiGraph,
    method: str = "geographic",
    k: int = 4,
    seed: int = 42,
    **kwargs: Any,
) -> tuple[PartitionResult, PartitionQualityReport]:
    """Execute the chosen graph partitioning algorithm and return verified results and metrics.

    Args:
        graph: Directed MultiDiGraph road network.
        method: Partitioning algorithm ('geographic' or 'graph_aware').
        k: Number of partitions.
        seed: Random seed for reproducibility.
        **kwargs: Additional algorithm-specific parameters (e.g. balance_tolerance).

    Returns:
        Tuple of (PartitionResult, PartitionQualityReport).
    """
    normalized_method = method.lower().strip()
    if normalized_method in {"geographic", "geo"}:
        result = geographic_partition(graph, k=k, seed=seed)
    elif normalized_method in {"graph_aware", "graph-aware", "connectivity"}:
        balance_tolerance = kwargs.get("balance_tolerance", 0.05)
        max_refinement_passes = kwargs.get("max_refinement_passes", 3)
        result = graph_aware_partition(
            graph,
            k=k,
            seed=seed,
            balance_tolerance=balance_tolerance,
            max_refinement_passes=max_refinement_passes,
        )
    else:
        raise ValueError(
            f"Unknown partitioning algorithm: {method}. Choose 'geographic' or 'graph_aware'."
        )

    # Validate output integrity
    assert_valid_partition(graph, result, expected_k=k)

    # Compute structural metrics
    quality = compute_partition_metrics(graph, result)
    return result, quality


def compare_partitioning_methods(
    graph: nx.MultiDiGraph,
    k: int = 4,
    seed: int = 42,
    **kwargs: Any,
) -> PartitionComparisonResult:
    """Execute and compare geographic versus graph-aware partitioning under identical conditions.

    Evaluates cut-edge counts, cut ratios, balance ratios, size standard deviations,
    and computational runtimes.
    """
    geo_result, geo_quality = partition_graph(graph, method="geographic", k=k, seed=seed, **kwargs)
    aware_result, aware_quality = partition_graph(
        graph, method="graph_aware", k=k, seed=seed, **kwargs
    )

    quality_comparison = {
        "geographic_cut_edges": geo_quality.cut_edge_count,
        "graph_aware_cut_edges": aware_quality.cut_edge_count,
        "cut_edge_difference": geo_quality.cut_edge_count - aware_quality.cut_edge_count,
        "geographic_cut_ratio": geo_quality.cut_edge_ratio,
        "graph_aware_cut_ratio": aware_quality.cut_edge_ratio,
        "geographic_balance_ratio": geo_quality.partition_balance_ratio,
        "graph_aware_balance_ratio": aware_quality.partition_balance_ratio,
        "geographic_size_std": geo_quality.partition_size_std,
        "graph_aware_size_std": aware_quality.partition_size_std,
        "geographic_cross_partition_length_m": geo_quality.cross_partition_road_length_m,
        "graph_aware_cross_partition_length_m": aware_quality.cross_partition_road_length_m,
    }

    timing_comparison = {
        "geographic_runtime_s": geo_result.runtime_seconds,
        "graph_aware_runtime_s": aware_result.runtime_seconds,
    }

    return PartitionComparisonResult(
        geographic_result=geo_result,
        graph_aware_result=aware_result,
        geographic_quality=geo_quality,
        graph_aware_quality=aware_quality,
        quality_metrics=quality_comparison,
        timing_metrics=timing_comparison,
    )
