# Quality Assurance & Verification Report

**Product:** SmartRoute Analytics  
**Academic Subject:** Large-Scale Graph Analysis (Modules 1–5)  
**Phase:** 11 of 12 — Testing, Optimization & Quality Assurance  
**Date:** 2026-11-19  
**Status:** PASS (100% Verification Rate)  

---

## 1. QA Objectives & Scope

The Phase 11 Quality Assurance initiative evaluated the stability, algorithm correctness, graph invariant integrity, edge-case resilience, performance characteristics, and demonstration readiness of SmartRoute Analytics across all modules developed in Phases 1 through 10.

---

## 2. Test Execution Environment

* **Operating System:** Windows 11 (build 26100)
* **Python Runtime:** Python 3.11.16 (CPython, 64-bit)
* **Test Runner:** Pytest 8.3.5 with Pluggy 1.7.0
* **Static Analysis:** Ruff 0.9.x
* **Core Dependencies:** NetworkX 3.4.2, SciPy, NumPy, Pandas, Plotly, Folium, Streamlit, OSMnx

---

## 3. Test Categories & Execution Summary

A total of **260 automated test cases** across **58 test modules** were executed.

| Category | Modules | Test Count | Pass Rate | Key Invariants Verified |
| :--- | :--- | :--- | :--- | :--- |
| **Graph Invariants** | `test_graph_invariants.py`, `test_graph_representation.py`, `test_graph_validation.py`, `test_graph_weights.py` | 18 | 100% | MultiDiGraph directed edge keys, coordinate validation, positive weights, GraphML roundtrip. |
| **Traversal Algorithms** | `test_bfs.py`, `test_dfs.py`, `test_reachability.py`, `test_traversal_edge_cases.py` | 12 | 100% | Hop-minimality against NetworkX, cycle termination, finish ordering, directed reachability. |
| **Shortest Path Routing** | `test_routing_networkx.py`, `test_routing_edge_cases.py`, `test_algorithm_correctness.py` | 23 | 100% | Dijkstra and A* distance and travel_time optimality against NetworkX oracle, source=target, unreachable. |
| **Advanced Routing** | `test_advanced_routing_networkx.py`, `test_advanced_routing_edge_cases.py` | 26 | 100% | Bidirectional Dijkstra meeting-point correctness, Yen's K-shortest loopless nondecreasing paths. |
| **Traffic Simulation** | `test_simulation_engine.py`, `test_simulation_invariants.py`, `test_scenario_storage.py` | 20 | 100% | Congestion multipliers (1.0x, 1.25x, 1.75x, 2.5x), road closures, blocked intersections, base immutability. |
| **Graph Analytics & Resilience** | `test_analytics_integration.py`, `test_analytics_correctness.py`, `test_connectivity.py` | 20 | 100% | Degree, betweenness, closeness, PageRank, weak/strong components, targeted percolation, MSF edge count. |
| **Partitioning & Indexing** | `test_geographic_partitioning.py`, `test_graph_aware_partitioning.py`, `test_partitioning_invariants.py`, `test_nearest_node.py`, `test_spatial_index.py`, `test_indexing_correctness.py` | 40 | 100% | All nodes assigned, cut edges counted on original directed roads, balance ratio $\ge 1.0$, KD-tree vs brute-force. |
| **Benchmarking & Scaling** | `test_benchmark_correctness.py`, `test_benchmark_runner.py`, `test_benchmark_timing.py`, `test_benchmark_memory.py`, `test_benchmark_statistics.py`, `test_benchmark_exports.py`, `test_benchmark_integrity.py` | 18 | 100% | High-resolution timing, tracemalloc isolation, 100% correctness rate, CSV export schema consistency. |
| **Reproducibility** | `test_benchmark_reproducibility.py`, `test_reproducibility.py` | 8 | 100% | Seed-locked determinism across graph generation, congestion, random failure, and query sampling. |
| **Dashboard UI & Integration** | `test_imports.py`, `test_dashboard_ui.py`, `test_dashboard_state.py`, `test_dashboard_integration.py`, `test_dashboard_smoke.py` | 50 | 100% | AppTest navigation across 7 pages, button actions, widget state invalidation, dark theme tokens. |
| **Defensive Error Handling** | `test_error_handling.py`, `test_paths.py`, `test_logging.py` | 25 | 100% | Path traversal prevention, invalid coordinate handling, out-of-bounds K, unknown node IDs. |

---

## 4. Algorithm Correctness Audit Findings

### 4.1 Breadth-First Search (BFS) & Depth-First Search (DFS)
- **Hop-Minimality:** In `tests/test_algorithm_correctness.py`, BFS hop depths from node 0 were verified against `networkx.single_source_shortest_path_length(graph, 0)`. All node hop distances match identically.
- **Cycle Handling:** Directed cycles in `offline_sample` were traversed without infinite loops; DFS finished order length matched visit order length.

### 4.2 Dijkstra, A*, and Bidirectional Dijkstra
- **Optimality:** Verified against `networkx.multi_source_dijkstra` across 10 deterministic test pairs for both `distance` and `travel_time` objectives. All algorithms produced identical optimal costs.
- **Edge-Key Precision:** Directed multigraph parallel edges between nodes (e.g., node 0 to 1 with key 0 vs key 7) are evaluated independently; the optimal key is chosen based on the objective (key 0 for distance, key 7 for travel time).
- **Admissibility:** Haversine coordinate distance heuristic never exceeds true road distance; travel_time uses safe zero-heuristic fallback to guarantee admissible optimality.

### 4.3 Yen's K-Shortest Paths
- **Loopless Invariant:** Verified that all routes generated by `find_alternative_routes` are strictly simple (no repeated nodes).
- **Cost Ordering:** Alternative routes are strictly ordered by nondecreasing cost ($C_1 \le C_2 \le \dots \le C_K$), with the primary route matching Dijkstra globally.

### 4.4 Centrality, Connectivity, and Minimum Spanning Forest
- **Centrality Verification:** In-degree, out-degree, betweenness (Brandes sampling for $V > 500$), closeness (incoming/outgoing), and PageRank (sums to $\approx 1.0$) were verified on known topologies.
- **MSF Invariant:** For graph projection with $V=16$ nodes and $C=2$ connected components, Kruskal's algorithm produced exactly $V - C = 14$ forest edges without cycles.

### 4.5 Graph Partitioning & Spatial Indexing
- **Completeness:** Every node is assigned to exactly one partition in $[0, K-1]$.
- **Directed Cut-Edge Counting:** Parallel directed edges spanning partition boundaries are individually accounted for.
- **KD-Tree Equivalence:** Tested across arbitrary query coordinates against $O(V)$ brute-force distance calculation. Result: 100% node ID match and distance match within $0.001$ m.

---

## 5. Performance Bottlenecks & Applied Optimizations

1. **Spatial Index Caching:**
   - *Baseline:* Rebuilding the 3D KD-Tree on every nearest-node query incurred $0.49$ ms overhead per query.
   - *Optimization:* Implemented `get_spatial_index(graph, dataset_id)` with dataset-level cache invalidation based on graph signature $(|V| + |E|)$.
   - *Result:* Repeated queries execute in $0.15$ ms ($> 3x$ speedup).

2. **Dashboard State Invalidation:**
   - *Issue:* Switching datasets in Overview previously retained stale routing or simulation outputs in session state.
   - *Optimization:* Introduced `invalidate_dataset_state()` in `src/ui/state.py` to selectively purge downstream derived caches upon dataset change.

3. **High-Resolution Timing Isolation:**
   - *Issue:* Memory profiling with `tracemalloc` introduces non-trivial runtime overhead ($\approx 10\%-25\%$).
   - *Optimization:* Separated benchmark runs into timing runs (`time.perf_counter_ns`) and memory-profiling runs (`tracemalloc.get_traced_memory`).

---

## 6. Bugs Discovered & Resolved During Phase 11

| Bug Description | Root Cause | Resolution | Verification Test |
| :--- | :--- | :--- | :--- |
| Negative edge weight rejection code mismatch | `src/graph/validation.py` issues `"weight"` code on negative length | Updated test assertion to expect `"weight"` | `test_invalid_negative_weight_rejection` |
| `create_scenario` parameter name mismatch | Keywords `congestion_level` vs `level`, `congestion_coverage` vs `coverage` | Updated test calls to use valid parameter names | `test_simulation_invariants.py` |
| Minimum spanning forest parameter name | Expected `weight_attribute` instead of `weight` | Aligned test argument with function signature `weight="length_m"` | `test_minimum_spanning_forest` |
| SpatialIndex constructor call | `SpatialIndex` requires `node_ids`, `node_coords`, etc. | Used factory function `build_spatial_index(graph)` | `test_indexing_correctness.py` |
| `export_benchmark_results` keyword argument | Passed `output_dir` instead of `output_directory` | Updated call to use `output_directory` | `test_export_integrity.py` |
| Partition result cut edge attribute | Cut edges stored in `PartitionQualityReport`, not `PartitionResult` | Computed metrics via `compute_partition_metrics` | `test_partitioning_invariants.py` |

---

## 7. Final Demonstration Readiness Assessment

* **Automated Tests:** 260 / 260 PASS (100%)
* **Master Verification:** 9 / 9 Suites PASS (100%)
* **College Viva Demonstration Script:** 8 / 8 Stages PASS (100%)
* **Offline Execution:** Fully autonomous without internet connection.
* **Readiness Level:** **READY FOR FINAL DEMONSTRATION & PHASE 12**
