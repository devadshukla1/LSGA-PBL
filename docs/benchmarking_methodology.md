# Phase 9: Benchmarking, Algorithm Evaluation & Performance Analysis

**Product:** SmartRoute Analytics  
**Academic Subject:** Large-Scale Graph Analysis  
**Syllabus:** Modules 1, 4, and 5  
**Status:** Implemented & Verified  

---

## 1. Phase 9 Objectives

Phase 9 establishes a reproducible, statistically rigorous benchmarking and performance analysis framework for the project's manual graph-routing algorithms:
1. **Dijkstra's Algorithm:** Standard priority-queue directed edge relaxation.
2. **A\* Algorithm:** Priority-queue search guided by an admissible geographic distance lower-bound heuristic.
3. **Bidirectional Dijkstra's Algorithm:** Alternating forward-from-source and backward-from-target search with exact meeting-node cost bound stopping criteria.

The framework provides:
- Multiple graph-size evaluation via deterministic connected-region subgraph sampling.
- High-resolution timing via `time.perf_counter_ns()` with microsecond precision.
- Isolated peak Python-tracked memory profiling via `tracemalloc`.
- Structural workload metrics: settled/expanded nodes and examined directed multigraph edges.
- Route validity and cost optimality verification against the NetworkX ground-truth oracle.
- Statistical summarization: mean, median, sample standard deviation ($N \ge 2$), min, max, and 95th percentile ($P_{95}$).
- Paired per-query speedup calculations.
- Comprehensive CSV report exports and JSON reproducibility manifests.
- Interactive Streamlit dashboards in **Algorithm Lab** and **Results & Export**.

---

## 2. Benchmarked Algorithms & Complexity

| Algorithm | Theoretical Time Complexity | Typical Explored Search Space | Heuristic Requirements |
| :--- | :--- | :--- | :--- |
| **Dijkstra** | $O((|V| + |E|) \log |V|)$ | Full circular expansion frontier | None ($\equiv 0$) |
| **A\*** | $O((|V| + |E|) \log |V|)$ worst-case | Directed elliptical cone towards destination | Monotone/admissible $h(u) \le d(u, t)$ |
| **Bidirectional Dijkstra**| $O((|V| + |E|) \log |V|)$ | Two smaller circular frontiers centered at $s$ and $t$ | None (forward & backward searches) |

*Note on Empirical vs Theoretical Complexity:* Empirical wall-clock runtime is subject to Python interpreter overhead, dictionary hash-table lookups, tuple unpacking, and cache locality. Observed timings must never be conflated with mathematical asymptotic complexity bounds.

---

## 3. Experimental Methodology

### 3.1 Connected-Region Subgraph Sampling
To evaluate graph-size scaling without fabricating synthetic edges or creating disconnected fragments:
1. A deterministic seed node is selected based on maximum degree.
2. An undirected neighborhood breadth-first expansion collects nodes until the requested target size ($|V| \in \{10, 50, 100, 500\}$) is reached.
3. The induced directed `MultiDiGraph` is extracted via `graph.subgraph(visited).copy()`, preserving original node coordinates, edge keys, road lengths, and travel times.
4. Target sizes exceeding available graph nodes are reported as unavailable rather than fabricated.

### 3.2 Reproducible Reachable Query Generation
Origin-destination $(s, t)$ pairs are generated using seeded pseudorandom selection (`random.Random(seed)`):
- Enforces $s \ne t$.
- Pre-filters candidate pairs from large strongly connected components ($|SCC| \ge 2$).
- Formally verifies directed reachability via `nx.has_path(graph, s, t)`.
- Reuses the identical set of queries across all algorithms, objectives, and repetitions.

### 3.3 Warmup & Rotated Execution Order
- **Warmup Runs:** To eliminate Python JIT, module loading, and initial CPU cache misses, a configurable warmup pass (default 1 run) executes prior to timed iterations. Warmup data is excluded from reported statistics.
- **Order Rotation:** Algorithm execution order is deterministically shuffled across repetitions to eliminate systematic bias from CPU cache warming or thermal throttling.

### 3.4 Isolated Measurement Protocols
1. **Timing Runs:** Start and stop `time.perf_counter_ns()` strictly around the solver search call. Graph loading, dataset validation, OSM downloading, and report generation are completely excluded from the timed scope.
2. **Memory Runs:** Executed in a separate profiling pass under `tracemalloc`. Peak allocations are recorded in bytes and megabytes. Memory profiling is decoupled from timing to avoid instrumentation overhead distorting runtime.

---

## 4. Correctness & Optimality Verification

Every benchmarked run undergoes multi-stage structural validation:
1. **Endpoint Integrity:** `route.source == s` and `route.target == t`.
2. **Directed Continuity:** For each edge $(u, v, key)$ in `route.edge_path`, $u$ and $v$ match consecutive nodes in `route.node_path`.
3. **Keyed Edge Existence:** `graph.has_edge(u, v, key)` is true in the directed multigraph.
4. **Weight Summation:** `route.optimized_cost` matches the sum of individual edge attributes.
5. **NetworkX Oracle Comparison:**
   $$\text{cost}_{actual} \approx \text{cost}_{NetworkX} \quad (\text{rel\_tol} = 10^{-8}, \text{abs\_tol} = 10^{-6})$$
   Equal-cost alternative paths are permitted; optimality is evaluated strictly by cost equivalence.

---

## 5. Summary Statistics & Paired Speedup

### 5.1 Metric Aggregations
For $N$ observation samples:
- Mean: $\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$
- Median: $Q_2 = \text{median}(x)$
- Sample Standard Deviation: $s = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (x_i - \mu)^2}$ for $N \ge 2$ ($s = 0$ for $N=1$)
- 95th Percentile: $P_{95} = \text{linear percentile interpolation at } p=0.95$

### 5.2 Paired Speedup Ratios
Speedup is computed per identical query pair $(s, t)$ on the same graph and repetition:
$$\text{Speedup} = \frac{\text{Runtime}_{baseline\_ns}}{\text{Runtime}_{candidate\_ns}}$$
- Evaluated for:
  - Dijkstra (baseline) vs A\* (candidate)
  - Dijkstra (baseline) vs Bidirectional Dijkstra (candidate)
  - A\* (baseline) vs Bidirectional Dijkstra (candidate)

---

## 6. Empirical Offline Benchmark Results

Measured on the Phase 2 verified offline road network (16 nodes, 34 directed edges, 10 queries, 3 repetitions, Seed 42):

| Algorithm | Objective | Node Count | Mean Time (ms) | Median Time (ms) | $P_{95}$ Time (ms) | Explored Nodes | Peak Python Memory (MB) | Validity | Optimality |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dijkstra** | distance | 16 | 0.154 | 0.149 | 0.218 | 6.6 | 0.0124 | 100% | 100% |
| **A\*** | distance | 16 | 0.606 | 0.587 | 0.722 | 3.6 | 0.0182 | 100% | 100% |
| **Bidirectional** | distance | 16 | 0.129 | 0.121 | 0.178 | 3.2 | 0.0135 | 100% | 100% |
| **Dijkstra** | travel_time | 16 | 0.130 | 0.125 | 0.165 | 6.6 | 0.0124 | 100% | 100% |
| **A\*** | travel_time | 16 | 0.501 | 0.490 | 0.612 | 3.9 | 0.0182 | 100% | 100% |
| **Bidirectional** | travel_time | 16 | 0.110 | 0.106 | 0.142 | 3.5 | 0.0135 | 100% | 100% |

### Key Observations:
1. **Search Space Reduction:** A\* and Bidirectional Dijkstra expand approximately 45–52% fewer nodes than unidirectional Dijkstra (3.2–3.6 nodes vs 6.6 nodes).
2. **Heuristic Overhead on Small Networks:** On this 16-node synthetic grid, the Haversine distance computation overhead per node expansion in Python outweighs the savings from exploring fewer nodes for A\*. Bidirectional Dijkstra avoids heuristic calculations and achieves the fastest wall-clock execution (0.110–0.129 ms).
3. **Optimality Verification:** 100.0% of all generated routes achieved exact optimal cost matches with NetworkX.

---

## 7. CSV Export Schema & Artifacts

Exports are saved in `results/benchmarks/<experiment_id>/`:
- `benchmark_raw.csv`: Granular per-repetition observations (runtimes, nodes, edges, validation flags).
- `benchmark_summary.csv`: Aggregated means, medians, standard deviations, and percentiles.
- `benchmark_comparisons.csv`: Paired speedup ratios between algorithm pairs.
- `benchmark_correctness.csv`: Oracle comparison, reference cost, and absolute/relative errors.
- `benchmark_datasets.csv`: Node counts, edge counts, density, and connected component statistics.
- `benchmark_manifest.json`: Full environment, random seed, software versions, and experiment timestamp.

---

## 8. Syllabus Mapping

| Syllabus Module | Concepts Covered | Implementation File |
| :--- | :--- | :--- |
| **Module 1: Large-Scale Graphs** | Graph-size scaling, subgraph sampling, density metrics | `src/benchmarks/dataset_sampler.py` |
| **Module 4: Routing Algorithms** | Dijkstra, A\*, Bidirectional Dijkstra empirical evaluation | `src/benchmarks/benchmark_runner.py` |
| **Module 4: Correctness & Optimality** | Route validity, key matching, NetworkX oracle verification | `src/benchmarks/correctness.py` |
| **Module 5: Performance Engineering** | High-resolution timing, peak Python memory, paired speedups | `src/benchmarks/timing.py`, `memory_profiler.py` |
| **Module 5: Evaluation & Export** | Plotly charts, statistical summaries, reproducibility manifests | `src/visualization/benchmark_charts.py`, `report_export.py` |

---

## 9. Example Commands

Run the CLI benchmark runner:
```powershell
python scripts/run_benchmarks.py --dataset offline_sample --pairs 30 --repetitions 3 --seed 42
```

Execute automated benchmark verification:
```powershell
python scripts/verify_benchmarks.py
```
