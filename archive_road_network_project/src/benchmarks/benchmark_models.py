"""Typed configuration, execution, summary, and manifest models for benchmarking."""

from collections.abc import Hashable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx

from config import (
    BENCHMARKS_DIR,
    DEFAULT_BENCHMARK_PAIRS,
    DEFAULT_BENCHMARK_REPETITIONS,
    DEFAULT_RANDOM_SEED,
)

VALID_ALGORITHMS = ("dijkstra", "astar", "bidirectional_dijkstra")
VALID_OBJECTIVES = ("distance", "travel_time")


@dataclass(frozen=True)
class BenchmarkConfig:
    """Immutable benchmark configuration specification."""

    dataset_id: str = "offline_sample"
    graph_sizes: list[int] = field(default_factory=lambda: [100, 500, 1000, 2000])
    algorithms: list[str] = field(
        default_factory=lambda: ["dijkstra", "astar", "bidirectional_dijkstra"]
    )
    objectives: list[str] = field(default_factory=lambda: ["distance", "travel_time"])
    query_count: int = DEFAULT_BENCHMARK_PAIRS
    repetitions: int = DEFAULT_BENCHMARK_REPETITIONS
    random_seed: int = DEFAULT_RANDOM_SEED
    warmup_runs: int = 1
    memory_enabled: bool = True
    correctness_enabled: bool = True
    output_directory: Path = BENCHMARKS_DIR

    def __post_init__(self) -> None:
        if self.query_count < 1:
            raise ValueError(f"query_count must be >= 1, got {self.query_count}")
        if self.repetitions < 1:
            raise ValueError(f"repetitions must be >= 1, got {self.repetitions}")
        if self.warmup_runs < 0:
            raise ValueError(f"warmup_runs must be >= 0, got {self.warmup_runs}")
        if not self.algorithms:
            raise ValueError("algorithms cannot be empty")
        for algo in self.algorithms:
            if algo not in VALID_ALGORITHMS:
                raise ValueError(
                    f"Invalid algorithm '{algo}'. Supported algorithms: {VALID_ALGORITHMS}"
                )
        if not self.objectives:
            raise ValueError("objectives cannot be empty")
        for obj in self.objectives:
            if obj not in VALID_OBJECTIVES:
                raise ValueError(
                    f"Invalid objective '{obj}'. Supported objectives: {VALID_OBJECTIVES}"
                )


@dataclass(frozen=True)
class BenchmarkDataset:
    """Metadata and graph container for a benchmark target dataset or sampled subgraph."""

    dataset_id: str
    dataset_origin: str
    node_count: int
    edge_count: int
    directed_density: float
    weak_component_count: int
    strong_component_count: int
    sampling_method: str
    random_seed: int | None
    graph: nx.MultiDiGraph


@dataclass(frozen=True)
class BenchmarkQuery:
    """Origin-destination pair with reachability status and optional reference cost."""

    query_id: int
    source: Hashable
    target: Hashable
    is_reachable: bool = True
    reference_cost: float | None = None


@dataclass(frozen=True)
class BenchmarkRunResult:
    """Structured record for an individual algorithm execution run."""

    experiment_id: str
    dataset_id: str
    dataset_origin: str
    graph_size_label: str
    node_count: int
    edge_count: int
    source: Hashable
    target: Hashable
    algorithm: str
    objective: str
    repetition: int
    random_seed: int
    runtime_ns: int
    runtime_ms: float
    nodes_expanded: int
    edges_examined: int
    forward_nodes_expanded: int | None = None
    backward_nodes_expanded: int | None = None
    route_found: bool = False
    route_valid: bool = False
    optimality_verified: bool = False
    route_cost: float | None = None
    reference_cost: float | None = None
    absolute_cost_error: float | None = None
    relative_cost_error: float | None = None
    status: str = "ok"
    error_message: str = ""
    peak_python_memory_bytes: int | None = None
    peak_python_memory_mb: float | None = None
    measurement_mode: str = "timing"


@dataclass(frozen=True)
class BenchmarkSummary:
    """Aggregated statistical summary for a specific algorithm and configuration."""

    dataset_id: str
    graph_size_label: str
    node_count: int
    algorithm: str
    objective: str
    query_count: int
    successful_runs: int
    failed_runs: int
    mean_runtime_ms: float
    median_runtime_ms: float
    std_runtime_ms: float
    min_runtime_ms: float
    max_runtime_ms: float
    p95_runtime_ms: float
    mean_nodes_expanded: float
    mean_edges_examined: float
    mean_peak_memory_mb: float
    route_validity_rate: float
    optimality_verification_rate: float


@dataclass(frozen=True)
class BenchmarkComparison:
    """Paired speedup analysis comparing two algorithms on identical workloads."""

    baseline_algorithm: str
    candidate_algorithm: str
    dataset_id: str
    graph_size_label: str
    objective: str
    comparison_count: int
    mean_speedup: float
    median_speedup: float
    min_speedup: float
    max_speedup: float


@dataclass(frozen=True)
class BenchmarkManifest:
    """Reproducibility manifest capturing environment, configurations, and queries."""

    experiment_id: str
    timestamp_utc: str
    dataset_id: str
    dataset_fingerprint: str
    graph_sizes: list[int]
    algorithms: list[str]
    objectives: list[str]
    query_count: int
    repetitions: int
    warmup_count: int
    random_seed: int
    timing_scope: str
    memory_measurement_scope: str
    python_version: str
    dependency_versions: dict[str, str]
    os_platform: str
    details: dict[str, Any] = field(default_factory=dict)
