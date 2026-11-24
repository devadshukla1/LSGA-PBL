# Syllabus-to-Implementation Mapping

**Product:** SmartRoute Analytics  
**Academic Project Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Course / Subject:** Large-Scale Graph Analysis (LSGA)  
**Academic Framework:** Project-Based Learning (PBL)  

---

## 1. Syllabus Overview & Module Alignment

The SmartRoute Analytics platform directly implements and validates core competencies across all 5 prescribed syllabus modules of the Large-Scale Graph Analysis curriculum:

```
[Module 1: Graph Representation & Fundamentals]
                     │
                     ▼
[Module 2: Graph Traversal & Spatial Processing]
                     │
                     ▼
[Module 3: Graph Partitioning & Spatial Indexing]
                     │
                     ▼
[Module 4: Shortest Paths & Advanced Routing]
                     │
                     ▼
[Module 5: Graph Analytics, Resilience & Benchmarking]
```

---

## 2. Detailed Module Mapping Matrix

### Module 1: Graph Representation & Network Fundamentals
- **Syllabus Topics Covered:** Directed graphs, multigraphs, parallel edges, node/edge attributes, adjacency lists, adjacency matrices, sparse graph storage formats, and graph validation.
- **Implemented Algorithms & Concepts:**
  - `networkx.MultiDiGraph` directed edge key indexing $e = (u, v, k)$.
  - GraphML XML round-trip persistence with typed custom properties.
  - Sparse adjacency-list representation and local subgraph adjacency matrices.
  - Graph structural validation (coordinate checks, non-negative weights).
- **Source Code Files:**
  - [`src/graph/representation.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/graph/representation.py)
  - [`src/graph/storage.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/graph/storage.py)
  - [`src/graph/validation.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/graph/validation.py)
  - [`src/graph/dataset_sampler.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/graph/dataset_sampler.py)
- **Interactive Dashboard Location:** `pages/1_Network_Overview.py`
- **Verification Evidence:** `tests/test_graph_representation.py`, `tests/test_graph_invariants.py`.

---

### Module 2: Graph Traversal and Spatial Processing
- **Syllabus Topics Covered:** Breadth-First Search (BFS), Depth-First Search (DFS), topological layers, discovery/finish intervals, cycle detection (back-edges), directed reachability, and spherical geospatial distance calculations.
- **Implemented Algorithms & Concepts:**
  - Manual FIFO queue-based BFS producing minimal-hop trees and layer frontiers.
  - Manual DFS tracking vertex state transitions (`UNVISITED`, `VISITING`, `VISITED`) and cycle back-edges.
  - Haversine great-circle formula for accurate spherical distance on WGS 84 coordinates.
- **Source Code Files:**
  - [`src/algorithms/traversal.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/algorithms/traversal.py)
  - [`src/graph/weights.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/graph/weights.py)
- **Interactive Dashboard Location:** `pages/2_Traversal_Lab.py`
- **Verification Evidence:** `tests/test_bfs.py`, `tests/test_dfs.py`, `tests/test_algorithm_correctness.py`.

---

### Module 3: Graph Partitioning and Spatial Indexing
- **Syllabus Topics Covered:** Graph partitioning objectives, edge-cut minimization, partition balance, recursive coordinate bisection, region-growing clustering, nearest-neighbor search, and spatial search trees.
- **Implemented Algorithms & Concepts:**
  - Recursive Geographic Bisection using median coordinate splits.
  - Graph-Aware Partitioning using multi-source synchronized BFS expansion.
  - Formal partition quality evaluation: Cut-Edge Count, Cut Ratio, and Balance Ratio $\ge 1.0$.
  - 3D Earth-Centered Earth-Fixed (ECEF) Cartesian coordinate projection.
  - Logarithmic spatial nearest-intersection indexing via `scipy.spatial.cKDTree`.
- **Source Code Files:**
  - [`src/partitioning/geographic.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/partitioning/geographic.py)
  - [`src/partitioning/graph_aware.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/partitioning/graph_aware.py)
  - [`src/partitioning/metrics.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/partitioning/metrics.py)
  - [`src/indexing/spatial_index.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/indexing/spatial_index.py)
- **Interactive Dashboard Location:** `pages/6_Partitioning_Lab.py`
- **Verification Evidence:** `tests/test_geographic_partitioning.py`, `tests/test_graph_aware_partitioning.py`, `tests/test_spatial_index.py`, `tests/test_indexing_correctness.py`.

---

### Module 4: Shortest Paths and Advanced Routing
- **Syllabus Topics Covered:** Single-source shortest paths with non-negative weights, priority queues (min-heaps), goal-directed heuristic search, admissible and consistent heuristics, bidirectional search, and $K$-shortest loopless paths.
- **Implemented Algorithms & Concepts:**
  - Custom Dijkstra's algorithm with binary min-heap (`heapq`).
  - Custom A* search using admissible Haversine / $v_{\max}$ heuristic function.
  - Custom Bidirectional Dijkstra with dual min-heap frontiers and stopping criteria $\min(d_f) + \min(d_b) \ge \mu$.
  - Yen's algorithm computing $K$ loopless alternative paths with spur node deviations and parallel edge handling.
- **Source Code Files:**
  - [`src/algorithms/dijkstra.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/algorithms/dijkstra.py)
  - [`src/algorithms/astar.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/algorithms/astar.py)
  - [`src/algorithms/bidirectional.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/algorithms/bidirectional.py)
  - [`src/routing/route_alternatives.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/routing/route_alternatives.py)
  - [`src/routing/routing_service.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/routing/routing_service.py)
- **Interactive Dashboard Location:** `pages/3_Route_Optimizer.py`
- **Verification Evidence:** `tests/test_routing_networkx.py`, `tests/test_advanced_routing_networkx.py`, `tests/test_algorithm_correctness.py`.

---

### Module 5: Graph Analytics, Resilience and Performance Benchmarking
- **Syllabus Topics Covered:** Centrality metrics (Degree, Betweenness, Closeness, PageRank), critical network nodes, Strongly/Weakly Connected Components, network resilience, site percolation, Minimum Spanning Trees (MST/MSF), experimental design, and statistical benchmarking.
- **Implemented Algorithms & Concepts:**
  - Network-wide centrality analysis (Brandes' algorithm, PageRank power iterations).
  - Component analysis using Tarjan's SCC algorithm.
  - Network percolation: Targeted removal of high-betweenness hubs vs. random node removal, tracking giant component degradation curves.
  - Minimum Spanning Forest (MSF) on symmetric undirected projections ($|E| = |V| - C$).
  - Rigorous benchmarking framework measuring execution runtime, peak memory consumption (`tracemalloc`), and explored nodes with fixed random seeds.
- **Source Code Files:**
  - [`src/analytics/centrality.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/analytics/centrality.py)
  - [`src/analytics/connectivity.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/analytics/connectivity.py)
  - [`src/analytics/resilience.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/analytics/resilience.py)
  - [`src/analytics/mst.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/analytics/mst.py)
  - [`src/benchmarks/runner.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/benchmarks/runner.py)
  - [`src/benchmarks/statistics.py`](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/src/benchmarks/statistics.py)
- **Interactive Dashboard Location:** `pages/4_Traffic_Simulation.py`, `pages/5_Analytics_Studio.py`, `pages/7_Benchmarking_Suite.py`
- **Verification Evidence:** `tests/test_analytics_integration.py`, `tests/test_analytics_correctness.py`, `tests/test_benchmark_runner.py`, `tests/test_benchmark_integrity.py`.
