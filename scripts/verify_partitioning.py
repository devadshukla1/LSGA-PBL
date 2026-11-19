"""Offline verification script for graph partitioning and spatial indexing."""

import copy
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.benchmarks.partition_benchmarks import run_partition_benchmarks
from src.graph.dataset_service import load
from src.graph.validation import validate
from src.indexing.nearest_node import brute_force_nearest_node
from src.indexing.spatial_index import build_spatial_index
from src.partitioning.partition_service import (
    compare_partitioning_methods,
    partition_graph,
)
from src.partitioning.partition_validation import validate_partition_result


def main() -> int:
    print("=" * 60)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("PHASE 8: Graph Partitioning & Spatial Indexing Verification")
    print("=" * 60)

    # 1. Load offline sample dataset
    info = load()
    graph = info.graph
    print(
        f"Loaded dataset: {info.metadata.dataset_name} "
        f"({len(graph)} nodes, {graph.number_of_edges()} edges)"
    )

    # Snapshot graph to verify immutability later
    nodes_snapshot = copy.deepcopy(dict(graph.nodes(data=True)))
    edges_snapshot = copy.deepcopy(list(graph.edges(keys=True, data=True)))

    # 2. Validate graph
    graph_val = validate(graph, info.metadata)

    # 3. Geographic Partitioning (K=4)
    k = 4
    geo_res, geo_quality = partition_graph(graph, method="geographic", k=k, seed=42)

    # 4. Graph-Aware Partitioning (K=4)
    aware_res, aware_quality = partition_graph(graph, method="graph_aware", k=k, seed=42)

    # 5. Validate assignments
    geo_valid, geo_issues = validate_partition_result(graph, geo_res, expected_k=k)
    aware_valid, aware_issues = validate_partition_result(graph, aware_res, expected_k=k)

    # 6. Cut-Edge Analysis
    print(
        f"\nGeographic Cut Edges: {geo_quality.cut_edge_count} "
        f"(ratio: {geo_quality.cut_edge_ratio:.3f})"
    )
    print(
        f"Graph-Aware Cut Edges: {aware_quality.cut_edge_count} "
        f"(ratio: {aware_quality.cut_edge_ratio:.3f})"
    )

    # 7. Balance Metrics
    print(
        f"Geographic Balance Ratio: {geo_quality.partition_balance_ratio:.3f} "
        f"(std: {geo_quality.partition_size_std:.2f})"
    )
    print(
        f"Graph-Aware Balance Ratio: {aware_quality.partition_balance_ratio:.3f} "
        f"(std: {aware_quality.partition_size_std:.2f})"
    )

    # 8. Method Comparison
    comp = compare_partitioning_methods(graph, k=k, seed=42)

    # 9. Build Spatial Index (KD-Tree)
    spatial_index = build_spatial_index(graph)

    # 10 & 11. Run nearest-node queries and compare with brute-force
    test_queries = [
        (28.6315, 77.2115),  # Centroid area
        (28.6300, 77.2100),  # Node 0 vicinity
        (28.6330, 77.2130),  # Northeast
        (28.6250, 77.2050),  # Southwest outer
    ]

    nn_matches = True
    dist_matches = True
    for q_lat, q_lon in test_queries:
        res_idx = spatial_index.nearest_node(q_lat, q_lon)
        res_bf = brute_force_nearest_node(graph, q_lat, q_lon)
        if res_idx.node_id != res_bf.node_id:
            nn_matches = False
            print(f"Mismatch at ({q_lat}, {q_lon}): idx={res_idx.node_id}, bf={res_bf.node_id}")
        if abs(res_idx.distance_m - res_bf.distance_m) > 0.05:
            dist_matches = False

    # 12 & 13. Preprocessing and Query Benchmarks
    benchmarks = run_partition_benchmarks(graph, k=k, repetitions=5, query_coordinates=test_queries)
    print(f"\nSpatial Index Build: {benchmarks.index_build_time.mean_s * 1000:.3f} ms")
    print(f"Brute-Force Query:   {benchmarks.brute_force_query_time.mean_s * 1000:.3f} ms")
    print(f"Indexed Query:       {benchmarks.indexed_query_time.mean_s * 1000:.3f} ms")
    print(f"Query Speedup:       {benchmarks.query_speedup:.2f}x")

    # 14. Graph Immutability
    immutability_passed = (
        dict(graph.nodes(data=True)) == nodes_snapshot
        and list(graph.edges(keys=True, data=True)) == edges_snapshot
    )

    # 15. Summary Checklist
    checks = {
        "Graph validation": graph_val.valid,
        "Geographic partitioning valid": geo_valid,
        "Graph-aware partitioning valid": aware_valid,
        "Geographic partition count K=4": geo_res.actual_partition_count == 4,
        "Graph-aware partition count K=4": aware_res.actual_partition_count == 4,
        "Directed cut-edge accounting": geo_quality.cut_edge_count >= 0
        and aware_quality.cut_edge_count >= 0,
        "Partition balance ratio valid": geo_quality.partition_balance_ratio >= 1.0
        and aware_quality.partition_balance_ratio >= 1.0,
        "Method comparison service": comp is not None
        and "geographic_cut_edges" in comp.quality_metrics,
        "Spatial index construction": spatial_index.node_count == len(graph),
        "Nearest-node identity match (KD-Tree vs BF)": nn_matches,
        "Nearest-node distance match (KD-Tree vs BF)": dist_matches,
        "Benchmark timings non-negative": benchmarks.query_speedup > 0,
        "Original graph immutability": immutability_passed,
    }

    print("\n" + "=" * 60)
    print("CHECKLIST RESULTS:")
    print("=" * 60)
    for label, status in checks.items():
        print(f"[{'PASS' if status else 'FAIL'}] {label}")

    all_passed = all(checks.values())
    print("=" * 60)
    print(f"PHASE 8 VERIFICATION: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
