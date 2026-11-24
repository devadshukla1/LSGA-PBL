"""Data models for graph partitioning configuration, results, and quality metrics."""

from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PartitionConfig:
    """Configuration parameters for a graph partitioning execution."""

    algorithm: str
    partition_count: int
    random_seed: int = 42
    balance_tolerance: float = 0.05
    weight_objective: str = "length_m"
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PartitionStatistics:
    """Structural properties and boundary metrics for an individual partition."""

    partition_id: int
    node_count: int
    internal_edge_count: int
    outgoing_cut_edges: int
    incoming_cut_edges: int
    total_road_length_m: float


@dataclass(frozen=True)
class PartitionQualityReport:
    """Global partition quality metrics evaluating balance and edge cuts."""

    total_nodes: int
    total_edges: int
    partition_sizes: dict[int, int]
    cut_edge_count: int
    cut_edge_ratio: float
    partition_balance_ratio: float
    partition_size_std: float
    largest_partition_size: int
    smallest_partition_size: int
    empty_partition_count: int
    cross_partition_road_length_m: float = 0.0
    partition_statistics: dict[int, PartitionStatistics] = field(default_factory=dict)


@dataclass(frozen=True)
class PartitionResult:
    """Complete node-to-partition assignments and execution diagnostics."""

    algorithm: str
    requested_partition_count: int
    actual_partition_count: int
    node_to_partition: dict[Hashable, int]
    partition_to_nodes: dict[int, list[Hashable]]
    parameters: dict[str, Any] = field(default_factory=dict)
    runtime_seconds: float = 0.0


@dataclass(frozen=True)
class PartitionComparisonResult:
    """Side-by-side comparison between geographic and graph-aware partitioning."""

    geographic_result: PartitionResult
    graph_aware_result: PartitionResult
    geographic_quality: PartitionQualityReport
    graph_aware_quality: PartitionQualityReport
    quality_metrics: dict[str, Any]
    timing_metrics: dict[str, Any]
