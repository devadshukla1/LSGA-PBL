# SmartRoute Analytics: Dashboard User Guide & College Demonstration Manual

**Product:** SmartRoute Analytics  
**Academic Subject:** Large-Scale Graph Analysis (Modules 1–5)  
**Phase:** 10 of 12 — Professional Streamlit Dashboard & Full System Integration  

---

## 1. System Architecture & Overview

SmartRoute Analytics is an interactive graph algorithms and urban road intelligence workbench built with Streamlit, NetworkX, OSMnx, SciPy, NumPy, and Folium.

The application adheres to five core design principles:
1. **Academic Rigor:** Algorithms are implemented manually without relying on external routing black-boxes; optimality is mathematically verified against NetworkX ground truth.
2. **Directed Multigraph Faithfulness:** All calculations use directed multigraphs (`MultiDiGraph`), correctly accounting for one-way roads, dual carriageways, turning penalties, and parallel road links.
3. **Reproducibility & Offline Autonomy:** The system ships with pre-validated offline datasets (`offline_sample`) and seed-locked pseudorandom generators, ensuring identical outputs without internet access or live OSM queries.
4. **Cohesive Visual Aesthetics:** Unified dark-slate design system (`#0B1120`, `#111827`, `#1E293B`) with sky-blue accents (`#38BDF8`), status badges, responsive metric cards, and tile-free Folium map rendering.
5. **Defensive Error Handling:** Form validations, boundary clamps, and error boundaries prevent unhandled exceptions from exposing raw tracebacks during demonstrations.

---

## 2. Launching the Application

### 2.1 Standard Local Execution (PowerShell)

Ensure the Python virtual environment is activated:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Streamlit will launch locally and display:
```text
  Local URL: http://localhost:8501
  Network URL: http://<ip>:8501
```

### 2.2 Headless / Custom Port Execution

To launch on an alternative port or in headless mode:

```powershell
python -m streamlit run app.py --server.port 8505 --server.headless true
```

---

## 3. Comprehensive Page Walkthroughs

The dashboard is structured into seven distinct pages, corresponding to the university syllabus modules:

### Page 1: Overview (Module 2: Representation & Storage)
* **Purpose:** Inspect road graph topologies, adjacency lists, adjacency matrices, and spatial overlays.
* **Key Features:**
  * **Dataset Switcher:** Toggle between synthetic testbeds (`offline_sample`) and real-world road networks (`connaught_place`).
  * **Network Metric Cards:** Immediate visualization of $|V|$ (junctions), $|E|$ (directed roads), total road length (km), and component counts.
  * **Validation Badge:** Real-time reporting of isolated nodes, missing coordinates, or connectivity anomalies.
  * **Interactive Road Map:** High-performance Folium map rendering road segments and junction markers with offline fallback support.
  * **Adjacency & Matrix Inspector:** Inspect outgoing road links, road geometries, speed limits, and matrix representations.

### Page 2: Route Optimizer (Modules 1 & 4: Fundamental Routing & Traversal)
* **Purpose:** Compare shortest-distance and shortest-time routes for simulated emergency vehicles.
* **Supported Algorithms:**
  * **Dijkstra's Algorithm:** Uniform-cost search with binary min-heap priority queue ($O((V + E) \log V)$).
  * **A\* Search:** Goal-directed search utilizing admissible Haversine coordinate heuristics ($O((V + E) \log V)$).
  * **Bidirectional Dijkstra:** Dual-frontier search meeting in the middle, reducing search space ($O((V + E) \log V)$).
* **Key Features:**
  * **Multi-Objective Optimization:** Toggle between *Shortest Distance* (meters) and *Shortest Travel Time* (seconds).
  * **Yen's K-Shortest Paths:** Generates $K$ loopless alternative detour routes with similarity and overlap metrics.
  * **Diagnostic Badges:** Displays nodes expanded, directed edges examined, heuristic admissibility checks, and turn-by-turn waypoint logs.

### Page 3: Traffic Simulator (Modules 4 & 5: Congestion & Disruption Modeling)
* **Purpose:** Simulate synthetic urban disruptions, congestion levels, road closures, and emergency rerouting.
* **Key Features:**
  * **Four Congestion Levels:** Normal (1.0x), Light (1.25x), Moderate (1.75x), and Heavy (2.5x) travel time multipliers.
  * **Disruption Controls:** Bounded random seed, road coverage slider (0–100%), closed directed edges `[[u, v, key]]`, and blocked junctions `[u]`.
  * **Before-and-After Metric Cards:** Comparison of baseline travel time vs congested scenario time, with delay deltas.
  * **Folium Multi-Layer Map:** Cyan baseline path, green scenario rerouted path, amber congested roads, and red closed links.
  * **Scenario Persistence:** Save and reload custom disruption profiles from `data/scenarios/`.

### Page 4: Graph Analytics (Modules 4 & 5: Connectivity, Centrality & Resilience)
* **Purpose:** Deep structural examination of connectivity, importance ranking, and network resilience under attack.
* **Key Features:**
  * **Traversal Inspection:** Step-by-step BFS (hop minimality) and DFS (discovery order).
  * **Component Decomposition:** Weakly and strongly connected component counts and size distributions.
  * **Centrality Metrics:** In-degree, out-degree, betweenness (exact or Ulrik Brandes randomized sampling), closeness, and PageRank.
  * **Critical Intersections:** Multi-metric composite vulnerability ranking identifying single points of failure.
  * **Targeted vs Random Degradation:** Percolation experiments removing nodes in order of centrality vs random failure, plotting connectivity retention curves.
  * **Minimum Spanning Forest:** Kruskal's algorithm on undirected projection to evaluate baseline connectivity infrastructure.

### Page 5: Partitioning & Spatial Indexing (Module 3: Partitioning & Indexing)
* **Purpose:** Distributed graph partitioning and spatial nearest-junction lookups.
* **Key Features:**
  * **Geographic Recursive Bisection:** Alternating latitude/longitude coordinate median splits for spatially compact partitions.
  * **Graph-Aware Region Growing:** Greedy boundary expansion minimizing cross-partition cut edges.
  * **Partition Quality Metrics:** Exact directed cut-edge count, cut-edge ratio, and partition balance ratio.
  * **3D Spherical KD-Tree Spatial Index:** Earth-centered 3D Cartesian coordinates ($X, Y, Z$) eliminating equirectangular distortion, with deterministic tie-breaking.
  * **Query Benchmark:** Microsecond-resolution comparison showing KD-Tree speedups (typically 8x–20x) over $O(V)$ brute-force distance scans.

### Page 6: Algorithm Lab (Modules 1, 4 & 5: Empirical Benchmarking)
* **Purpose:** Statistically rigorous performance evaluation across varying graph sizes.
* **Key Features:**
  * **Isolated Measurements:** High-resolution runtime timing (`time.perf_counter_ns`) separated from memory profiling (`tracemalloc`).
  * **NetworkX Oracle Verification:** Every executed query verifies cost optimality and route validity against NetworkX.
  * **Interactive Plotly Visualizations:** Runtime vs Graph Size scaling curves, Box plots of latency distributions, Explored nodes comparison, Peak memory consumption, and Paired speedup bar charts.
  * **Automatic CSV Export:** Automatically persists raw and summarized results to `results/benchmarks/`.

### Page 7: Results & Export (Data Persistence & Reporting)
* **Purpose:** Central repository for auditing historical benchmark runs and exporting research data.
* **Key Features:**
  * **Experiment Manifest Viewer:** Review timestamp, random seed, query count, and repetition configuration.
  * **Statistical Tables:** Mean, median, standard deviation, P95, and P99 latency percentiles.
  * **Download Center:** One-click CSV downloads for raw query records, statistical summaries, paired comparisons, and JSON manifest.

---

## 4. 10-Minute College Demonstration Script

Follow this step-by-step flow when presenting the project to professors, evaluators, or viva panels:

| Step | Time | Page | Recommended Action & Talking Points |
| :--- | :--- | :--- | :--- |
| **1** | 0:00–1:30 | **Overview** | • Select `offline_sample` dataset.<br>• Explain MultiDiGraph modeling (16 nodes, 34 edges, directed one-ways).<br>• Point out the validation status ("Valid") and topological density.<br>• Show the geographic road map and adjacency list. |
| **2** | 1:30–3:00 | **Route Optimizer** | • Set Source = `0`, Destination = `1`.<br>• Run **Dijkstra** with *Shortest Distance* (100.0 m, 14.4 s).<br>• Switch to *Shortest Estimated Travel Time* (140.0 m, 10.08 s).<br>• **Key Insight:** Explain why the fastest route is longer in distance (higher-speed arterial vs residential street).<br>• Enable alternative routes ($K=3$) and show Yen's detour comparisons. |
| **3** | 3:00–4:30 | **Traffic Simulator** | • Select Congestion = `heavy` (2.5x multiplier), Coverage = 50%, Seed = 42.<br>• Click *Run Simulation*.<br>• Show Before/After metric cards: explain the delay increase and route diversion.<br>• Point out the dual-colored Folium map: cyan baseline vs green emergency reroute avoiding congested segments. |
| **4** | 4:30–6:00 | **Graph Analytics** | • Run BFS from junction `0` to `1`: show directed hop minimality (1 hop).<br>• Switch to the *Centrality & Resilience* section: select *Critical Intersections*.<br>• Highlight Junction `5` as the top bottleneck (highest betweenness and PageRank).<br>• Show the Network Resilience chart: targeted failure causes faster connectivity collapse than random node failure. |
| **5** | 6:00–7:30 | **Partitioning** | • Run Geographic Partitioning ($K=4$), then Graph-Aware Partitioning ($K=4$).<br>• Compare cut edges: explain why graph-aware region growing reduces communication cross-talk.<br>• Switch to the *Spatial Indexing* tab: execute coordinate query `(28.63, 77.21)`.<br>• Demonstrate the 3D KD-Tree nearest-neighbor lookup speedup (~10x faster than brute force). |
| **6** | 7:30–9:00 | **Algorithm Lab** | • Click *Run Benchmark Experiment* with 10 query pairs and 3 repetitions.<br>• Show real-time progress bar.<br>• Inspect the scaling chart: show how A* search expands fewer nodes than Dijkstra due to the Haversine heuristic.<br>• Emphasize the 100% NetworkX optimality match rate. |
| **7** | 9:00–10:00 | **Results & Export** | • Show the historical experiment manifest.<br>• Demonstrate CSV export of the benchmark run for academic review.<br>• Conclude with viva summary: modular architecture, zero unhandled errors, complete syllabus coverage. |

---

## 5. Offline Verification & Automated Test Commands

To demonstrate software verification to examiners:

```powershell
# 1. Full automated test suite (209 tests across 10 modules)
python -m pytest -v

# 2. Phase 10 Dashboard integration verification
python scripts/verify_dashboard.py

# 3. Code formatting and linting audit
python -m ruff check .
python -m ruff format --check .
```
