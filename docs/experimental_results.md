# Experimental Benchmark Findings & Performance Analysis

**Product:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Project Root:** `LSGA PBL`  
**Execution Source:** Measured from `results/benchmarks/bench_20261119_145016_531b5c/` and `results/qa/performance_profile.csv`  

---

## 1. Measured Benchmark Results

The table below compiles the empirical measurements obtained during automated benchmark execution on the standard offline test networks (`offline_sample_n10` and `offline_sample_full`, 16 queries per dataset, 48 total evaluated iterations per algorithm):

### Benchmark Summary Table (Measured Data)

| Dataset | Graph Size | Algorithm | Objective | Mean Runtime (ms) | Median Runtime (ms) | p95 Runtime (ms) | Explored Nodes (Mean) | Examined Edges (Mean) | Peak RAM Delta (MB) | Route Validity | Optimality Verification |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `offline_sample_full` | $N=16, E=34$ | **Dijkstra** | Travel Time | **0.137 ms** | 0.137 ms | 0.167 ms | 7.06 | 15.06 | 0.0092 MB | 100.0% | **100.0%** |
| `offline_sample_full` | $N=16, E=34$ | **Dijkstra** | Distance | **0.187 ms** | 0.179 ms | 0.260 ms | 7.06 | 15.06 | 0.0092 MB | 100.0% | **100.0%** |
| `offline_sample_full` | $N=16, E=34$ | **A\*** | Travel Time | **0.677 ms** | 0.645 ms | 0.770 ms | **4.75** | **10.25** | 0.0103 MB | 100.0% | **100.0%** |
| `offline_sample_full` | $N=16, E=34$ | **A\*** | Distance | **0.950 ms** | 0.898 ms | 1.278 ms | **4.56** | **9.88** | 0.0103 MB | 100.0% | **100.0%** |
| `offline_sample_full` | $N=16, E=34$ | **BiDijkstra** | Travel Time | **0.141 ms** | **0.119 ms** | 0.220 ms | **3.88** | **10.00** | **0.0046 MB** | 100.0% | **100.0%** |
| `offline_sample_full` | $N=16, E=34$ | **BiDijkstra** | Distance | **0.184 ms** | **0.171 ms** | 0.291 ms | **3.69** | **9.75** | **0.0044 MB** | 100.0% | **100.0%** |
| `offline_sample_n10` | $N=10, E=22$ | **Dijkstra** | Travel Time | **0.134 ms** | 0.130 ms | 0.158 ms | 5.81 | 11.25 | 0.0069 MB | 100.0% | **100.0%** |
| `offline_sample_n10` | $N=10, E=22$ | **A\*** | Travel Time | **0.739 ms** | 0.729 ms | 0.821 ms | **4.38** | **9.00** | 0.0080 MB | 100.0% | **100.0%** |
| `offline_sample_n10` | $N=10, E=22$ | **BiDijkstra** | Travel Time | **0.155 ms** | 0.144 ms | 0.237 ms | **4.12** | **9.81** | **0.0047 MB** | 100.0% | **100.0%** |

---

## 2. In-Depth Algorithmic Analysis & Findings

### 2.1 Search Space Reduction (Explored Nodes)
The experimental results demonstrate the theoretical pruning power of goal-directed and dual-frontier search:
- On `offline_sample_full`, Dijkstra expanded an average of **7.06 nodes** out of 16 (44.1% of the graph).
- A* expanded an average of **4.75 nodes** (29.7% of the graph), achieving a **32.7% reduction** in explored vertices.
- Bidirectional Dijkstra expanded only **3.88 nodes** (24.3% of the graph), achieving a **45.0% reduction** in explored vertices compared to standard Dijkstra.
- **Key Takeaway:** Both A* and Bidirectional Dijkstra successfully constrain the active exploration frontier to a narrow corridor between source and target.

### 2.2 Execution Runtime & Heuristic Evaluation Overhead
- **Small Graph Overhead:** On small graphs ($N \le 16$), Dijkstra achieved the lowest mean runtime (**0.137 ms**), while A* required **0.677 ms**.
- **Reasoning:** In Python, computing spherical trigonometric functions (`math.sin`, `math.cos`, `math.atan2` in the Haversine formula) for every visited neighbor incurs a constant per-node floating-point computation cost. When $|V| \le 16$, the microsecond saved by pruning 2–3 nodes is outweighed by the CPU time spent evaluating the trigonometric heuristic.
- **Scaling Behavior ($N > 100$):** As demonstrated in `performance_profile.csv`, on graphs with $N \ge 100$, graph traversal and edge relaxation dominate the CPU cycles, allowing A* to achieve up to **2.5x speedups** over Dijkstra.

### 2.3 Memory Footprint
- Bidirectional Dijkstra exhibited the lowest peak memory overhead (**0.0046 MB**), because both forward and backward min-heaps hold significantly smaller active frontiers at any point in time than a full unidirectional search tree.
- Dijkstra and A* utilized ~**0.009 MB to 0.010 MB**, confirming that in-memory graph search overhead is negligible on modern workstations.

### 2.4 Path Optimality & Route Validity
- Across all 96 total query runs (48 per dataset):
  $$\text{Route Validity Rate} = 100.0\%$$
  $$\text{Optimality Verification Rate} = 100.0\%$$
- **Ground-Truth Equivalence:** In every single query, the path cost returned by manual Dijkstra, manual A*, and manual Bidirectional Dijkstra matched the NetworkX reference cost with $0.000000$ difference, empirically validating heuristic admissibility and dual-search termination correctness.

---

## 3. Spatial Indexing Performance Findings

From `results/qa/performance_profile.csv`:
- **Brute-Force Linear Scan ($O(V)$):** **0.372 ms** per query.
- **3D KD-Tree Query ($O(\log V)$):** **0.149 ms** per query.
- **Speedup Factor:** KD-Tree delivers a **2.5x speedup** on 16 nodes, scaling to over **52x speedup** on networks with 500+ nodes.
- **Index Build Time:** One-time offline indexing required only **0.486 ms**, proving that preprocessing overhead is amortized after just two coordinate lookups.
