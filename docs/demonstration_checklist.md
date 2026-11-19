# College Viva & Project Demonstration Checklist

**Product:** SmartRoute Analytics (Smart City Traffic & Emergency Route Optimizer)  
**Project:** Large-Scale Graph Analysis (LSGA PBL)  
**Phase:** 11 of 12 — Testing, Optimization & Quality Assurance  
**Operating Mode:** 100% Offline, Deterministic, Zero Network Reliance  

---

## 1. Pre-Presentation Checklist (Setup & Environment)

| Check Item | Command / Action | Expected Result | Status |
|---|---|---|---|
| **Python Version** | `python --version` | Python 3.11.x (>=3.11, <3.13) | [x] PASS |
| **Virtual Environment** | `.venv\Scripts\activate` | Active virtual environment with all dependencies | [x] PASS |
| **Code Hygiene** | `python -m ruff check .` | 0 errors across all 177 files | [x] PASS |
| **Code Formatting** | `python -m ruff format --check .` | All files properly formatted | [x] PASS |
| **Automated Test Suite** | `python -m pytest` | **260 passed, 0 failed** in ~10–14s | [x] PASS |
| **Master Phase Verification** | `python scripts/verify_all.py` | 9 of 9 phase verification suites passing (100%) | [x] PASS |
| **Demo Script Dry Run** | `python scripts/verify_demo.py` | 8 of 8 demonstration pipeline checks passing | [x] PASS |
| **Offline Cache Check** | Inspect `data/cache/` | `chandigarh_drive.graphml` & sample graphs present | [x] PASS |
| **Streamlit Server Start** | `streamlit run app.py` | Server starts locally at `http://localhost:8501` | [x] PASS |

---

## 2. Live Demonstration Flow (Step-by-Step Viva Walkthrough)

Follow this scripted 12-step walkthrough during the live project evaluation:

### Step 1: Application Launch & Overview
1. Open web browser to `http://localhost:8501`.
2. Introduce the system as **SmartRoute Analytics**, an academic platform for large-scale graph analysis on urban road networks.
3. Show the sidebar dataset selector loaded with offline synthetic grids and cached Chandigarh networks.

### Step 2: Road Network Exploration (`pages/1_Network_Overview.py`)
1. Select the **Offline Sample (4x4 Grid)** or **Chandigarh Core** dataset.
2. View graph metrics: Node count (16), Edge count (34), Directed Density, Strongly Connected Component count.
3. Inspect the PyDeck interactive geographic map displaying node coordinates and directed edge vectors.

### Step 3: Graph Traversal & Connectivity (`pages/2_Traversal_Lab.py`)
1. Select source node `0`.
2. Execute **Breadth-First Search (BFS)**: Show layer-by-layer frontier expansion and shortest-hop tree.
3. Execute **Depth-First Search (DFS)**: Show branch discovery, discovery/finish timestamps, and back-edge cycle detection.
4. Review reachability breakdown and SCC distribution.

### Step 4: Shortest-Path Routing & Cost Equivalence (`pages/3_Route_Optimizer.py`)
1. Set Source = `0`, Target = `15`, Objective = `travel_time`.
2. Run **Dijkstra's Algorithm**: Note cost, path `[0, 1, 2, 3, 7, 11, 15]`, runtime, and explored nodes.
3. Run **A* Search (Haversine Heuristic)**: Note exact identical cost (admissibility guarantee) with significantly reduced explored node count.
4. Run **Bidirectional Dijkstra**: Verify identical cost matching from both frontiers simultaneously.
5. Display comparative table demonstrating $C_{\text{Dijkstra}} = C_{\text{A*}} = C_{\text{BiDijkstra}}$.

### Step 5: Alternative Paths (`pages/3_Route_Optimizer.py`)
1. Enable **K-Shortest Routes (Yen's Algorithm)** with $K=3$.
2. Verify loopless alternative routes ordered by non-decreasing travel time.
3. Highlight route diversity metrics and detour trade-offs on the map.

### Step 6: Traffic Congestion & Dynamic Penalties (`pages/4_Traffic_Simulation.py`)
1. Configure traffic congestion: Severity = `HEAVY` (2.0x factor) or `SEVERE` (2.5x factor).
2. Set seed = `42` for exact reproducibility.
3. Apply congestion to 30% of edges; observe dynamic travel time inflation.
4. Re-calculate route: Show the optimizer automatically diverting away from congested arteries.

### Step 7: Emergency Incidents & Road Blockages (`pages/4_Traffic_Simulation.py`)
1. Add an incident: Block intersection node `1` or close edge `(0, 1)`.
2. Trigger **Emergency Evacuation Rerouting**.
3. Point out that the original graph is preserved via deepcopy/scenario isolation, and the emergency vehicle takes an instant, obstruction-free detour.

### Step 8: Network Centrality & Critical Arteries (`pages/5_Analytics_Studio.py`)
1. Compute centrality measures:
   - **Betweenness Centrality**: Pinpoints bottleneck bridge nodes and critical transit hubs.
   - **Degree Centrality & Closeness Centrality**: Identifies accessible core nodes.
   - **PageRank**: Computes global structural influence.
2. View top-5 critical intersections table and ranking chart.

### Step 9: Structural Resilience & Percolation (`pages/5_Analytics_Studio.py`)
1. Run **Network Resilience Percolation**:
   - Random Node Failure vs. Targeted Attack on high-betweenness hubs.
2. Observe Giant Component degradation curve: Targeted removal rapidly disintegrates connectivity compared to random removal.
3. Inspect **Minimum Spanning Forest (MSF)** for baseline backbone connectivity.

### Step 10: Graph Partitioning & Cut-Edge Analysis (`pages/6_Partitioning_Lab.py`)
1. Set $K=4$ partitions.
2. Run **Geographic Partitioning** (Bounding-box centroid spatial clustering).
3. Run **Graph-Aware Partitioning** (Breadth-first balanced growth).
4. Compare partition metrics: Partition balance ratio ($\approx 1.0$) and directed cut-edge counts.
5. Emphasize how cut edges correspond to boundary roads requiring inter-partition coordination.

### Step 11: 3D Spatial Indexing vs. Brute-Force (`pages/6_Partitioning_Lab.py`)
1. Provide arbitrary GPS coordinate $(lat, lon)$ or click the map.
2. Query nearest road network node using **Spatial 3D ECEF KD-Tree** vs. **Brute-Force $O(V)$ Scan**.
3. Verify that both methods return the exact same node ID and metric distance.
4. Point out the orders-of-magnitude query time speedup ($O(\log V)$ vs. $O(V)$).

### Step 12: Rigorous Benchmarking & Artifact Export (`pages/7_Benchmarking_Suite.py`)
1. Set trial count = 10 queries across Dijkstra, A*, and Bidirectional Dijkstra with fixed seed `42`.
2. Run benchmark: Review runtime, peak memory delta, explored nodes, and validity verification rate (100%).
3. Inspect the Pareto frontier and speedup factor charts.
4. Export results: Download generated summary CSV, raw measurements CSV, and JSON reproducibility manifest.

---

## 3. Post-Presentation Checklist (Artifact & State Verification)

| Check Item | Expected State | Verified |
|---|---|---|
| **Export Directory** | `results/benchmarks/` contains valid CSV and JSON files | [x] PASS |
| **QA Artifacts** | `results/qa/` contains `junit_report.xml`, `test_summary.json`, `test_report.txt`, `performance_profile.csv` | [x] PASS |
| **Graph Immutability** | No persistent mutations on disk to `data/cache/` base GraphML files | [x] PASS |
| **Reproducibility** | All experiments re-run with seed `42` yield identical numeric values | [x] PASS |
| **Clean Shutdown** | Streamlit process terminates gracefully with `Ctrl+C` | [x] PASS |
