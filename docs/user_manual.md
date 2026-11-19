# User Manual: Operating the SmartRoute Analytics Dashboard

**Product:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Project Root:** `LSGA PBL`  
**Platform:** Streamlit Web Application (Local: `http://localhost:8501`)  

---

## 1. Navigating the Dashboard

SmartRoute Analytics features a dark-themed, responsive multi-page user interface organized into 7 specialized functional studios accessed via the left-hand navigation sidebar:

```text
Dashboard Navigation:
├── app.py                     <- System Overview & Dataset Management
├── 1_Network_Overview.py      <- Topological & Spatial Road Exploration
├── 2_Traversal_Lab.py         <- Step-by-Step BFS & DFS Traversal
├── 3_Route_Optimizer.py       <- Dijkstra, A*, Bidirectional & Yen's Routing
├── 4_Traffic_Simulation.py    <- Congestion Levels, Incidents & Emergency Rerouting
├── 5_Analytics_Studio.py      <- Centrality Hubs, Resilience Percolation & MSF
├── 6_Partitioning_Lab.py      <- Spatial Partitioning & 3D KD-Tree Lookup
└── 7_Benchmarking_Suite.py    <- Automated Benchmarks & Exportable Artifacts
```

---

## 2. Page-by-Page Operational Guide

### 2.1 Main Application Hub (`app.py`)
- **Dataset Selection:** Use the sidebar dropdown to switch between:
  - **"Offline Sample (4x4 Grid)":** Fast, 16-node synthetic grid ideal for step-by-step algorithmic tracing.
  - **"Chandigarh Core":** Real-world urban road network of Chandigarh, India, loaded from pre-cached GraphML.
- **System Metrics:** Displays active node count, edge count, density, and directedness.

### 2.2 Network Overview (`pages/1_Network_Overview.py`)
- **Geographic Visualizer:** Inspect the PyDeck map rendering intersection vertices and directed road vectors.
- **Adjacency Explorer:** Examine the sparse adjacency list representation and inspect localized subgraph adjacency matrices.

### 2.3 Traversal Lab (`pages/2_Traversal_Lab.py`)
- **Source Selection:** Choose an origin intersection node.
- **BFS Execution:** Click "Execute BFS" to view layer-by-layer frontier expansion and the minimal-hop spanning tree.
- **DFS Execution:** Click "Execute DFS" to view branch discovery intervals, finish timestamps, and detected directed cycle back-edges.

### 2.4 Route Optimizer (`pages/3_Route_Optimizer.py`)
- **Routing Setup:** Choose Source Node, Target Node, and Routing Objective (**Physical Distance** or **Estimated Travel Time**).
- **Algorithm Comparison:** Click "Run Comparison" to execute manual Dijkstra, manual A*, and manual Bidirectional Dijkstra simultaneously.
- **Results:** Review path geometries, optimal traversal costs, execution runtimes, and the number of explored vertices.
- **Alternative Routes:** Enable "K-Shortest Routes" ($K=2$ to $5$) to generate loopless detour corridors via Yen's algorithm.

### 2.5 Traffic Simulator (`pages/4_Traffic_Simulation.py`)
- **Congestion Multipliers:** Select congestion tier (**Free-Flow**, **Light 1.2x**, **Moderate 1.5x**, **Heavy 2.0x**, or **Severe 2.5x**) and edge coverage percentage.
- **Reproducibility Seed:** Lock the integer random seed (`42`) to reproduce exact traffic patterns.
- **Road Closures:** Select specific road links or intersections to simulate emergency incidents or physical blockages.
- **Emergency Recalculation:** Click "Simulate & Reroute" to compute an instant, obstruction-free emergency detour route.

### 2.6 Analytics Studio (`pages/5_Analytics_Studio.py`)
- **Centrality Metrics:** Select betweenness, degree, closeness, or PageRank. View ranked critical junctions on the map and ranking charts.
- **Network Resilience:** Click "Run Percolation Experiment" to simulate targeted removal of high-betweenness hubs vs. random node failure, tracking the degradation curve of the giant connected component.
- **Spanning Forest:** View the Minimum Spanning Forest (MSF) computed on the undirected projection.

### 2.7 Partitioning Lab (`pages/6_Partitioning_Lab.py`)
- **Partitioning Configuration:** Set the partition count $K$ ($K \in \{2, 4, 8\}$).
- **Method Comparison:** Compare **Recursive Geographic Bisection** with **Graph-Aware Region Growing**.
- **Metrics:** Review the Cut-Edge Ratio and Balance Ratio ($\approx 1.0$).
- **Spatial KD-Tree Query:** Enter arbitrary $(lat, lon)$ coordinates to benchmark 3D KD-Tree nearest-node lookup against linear $O(V)$ brute-force scanning.

### 2.8 Benchmarking Suite (`pages/7_Benchmarking_Suite.py`)
- **Benchmark Execution:** Configure trial repetitions and run automated performance evaluation across Dijkstra, A*, and Bidirectional Dijkstra.
- **Visual Analytics:** Inspect runtime latency distributions, explored node reductions, and memory consumption.
- **Export Artifacts:** Download results as summary CSVs, raw measurement tables, or structured JSON reproducibility manifests.
