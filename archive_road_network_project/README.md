# SmartRoute Analytics: Smart City Traffic & Emergency Route Optimizer

**Academic Project Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Course / Subject:** Large-Scale Graph Analysis (LSGA PBL — Modules 1, 2, 3, 4, and 5)  
**Academic Session:** 2026–2027  
**Platform:** Python 3.11 / Streamlit Interactive Web Application  
**Execution Mode:** 100% Offline, Deterministic, Zero Cloud Reliance  

---

## 1. Project Abstract

SmartRoute Analytics is an academic graph analytics, optimization, and simulation platform designed to evaluate emergency vehicle routing and urban road network resilience on real-world and synthetic street networks. Road networks are modeled as directed multigraphs $G = (V, E)$ using NetworkX MultiDiGraph structures, preserving intersection coordinates, one-way restrictions, physical speed limits, and parallel road links with unique edge keys.

The platform implements and evaluates three fundamental single-source shortest-path algorithms: manual Dijkstra's algorithm, goal-directed A* search with an admissible spherical Haversine heuristic, and manual Bidirectional Dijkstra with dual-frontier search. For emergency logistics, Yen's algorithm is implemented to compute $K$-shortest loopless alternative routes. The system deterministically simulates traffic congestion across five multiplier tiers (1.0x to 2.5x) and evaluates emergency road closures and blocked intersections by inducing active subgraphs while maintaining the strict immutability of the base road network.

To assess structural vulnerability, the system computes network centralities (Betweenness, Degree, Closeness, and PageRank) and performs site percolation experiments comparing targeted attacks on high-betweenness hubs against uniform random node failures. Furthermore, it implements Recursive Geographic Bisection and Graph-Aware Region Growing partitioning alongside a 3D Earth-Centered Earth-Fixed (ECEF) KD-Tree spatial index that delivers a 25x–52x query speedup over linear brute-force scanning. The platform is delivered via an interactive Streamlit dashboard backed by 260 automated Pytest test cases passing with zero failures.

---

## 2. Key Features

- **Directed MultiDiGraph Representation:** Preserves one-way roads and parallel carriageways using edge keys $k \in \mathbb{N}_0$.
- **Shortest-Path Optimization:** Custom manual implementations of Dijkstra, A*, and Bidirectional Dijkstra.
- **Provably Admissible Heuristics:** Spherical Haversine distance divided by global maximum speed $v_{\max}$ guarantees optimal A* path discovery.
- **Yen's K-Shortest Loopless Paths:** Discovers top alternative evacuation corridors with parallel edge awareness.
- **Deterministic Traffic Simulation:** Reproducible congestion multipliers (1.0x to 2.5x) and incident closures with guaranteed graph immutability.
- **Topological Centrality Analysis:** Identifies critical bottleneck bridges using Brandes' betweenness centrality.
- **Network Resilience Percolation:** Quantifies giant component degradation under targeted hub attacks versus random failures.
- **Graph Partitioning & Spatial Indexing:** Recursive Geographic Bisection, Graph-Aware Region Growing, and $O(\log V)$ 3D ECEF KD-Tree nearest-node queries.
- **Automated Benchmarking Suite:** Measures runtime latency, peak memory allocation (`tracemalloc`), and explored node counts with 100% ground-truth validation against NetworkX.
- **100% Offline Operation:** Bundles pre-cached GraphML road networks and synthetic grid generators with zero internet requirement.

---

## 3. Technology Stack

- **Core Language & Runtime:** Python 3.11.16
- **Graph Modeling & Algorithms:** `networkx>=3.2`, `osmnx>=1.9.0`
- **Spatial Indexing & Math:** `scipy>=1.12.0`, `numpy>=1.26.4`
- **Interactive UI & Mapping:** `streamlit>=1.32.0`, `pydeck>=0.8.0`
- **Data Serialization:** GraphML, CSV, JSON
- **Testing & Code Quality:** `pytest>=8.0.0`, `ruff>=0.3.0`

---

## 4. Repository & Directory Structure

```text
LSGA PBL/
├── app.py                       <- Streamlit application entry point & dataset manager
├── config.py                    <- Global settings, paths, and speed parameters
├── requirements.txt             <- Pinned Python dependencies
├── pyproject.toml               <- Project build and tool configurations
│
├── pages/                       <- Streamlit Multi-Page Dashboard Views
│   ├── 1_Network_Overview.py    <- Road network topology & PyDeck visualizer
│   ├── 2_Traversal_Lab.py       <- Layer-by-layer BFS & cycle-detecting DFS
│   ├── 3_Route_Optimizer.py     <- Dijkstra, A*, Bidirectional & Yen's routing
│   ├── 4_Traffic_Simulation.py  <- Congestion levels, incident closures & rerouting
│   ├── 5_Analytics_Studio.py    <- Centrality rankings, percolation & MSF
│   ├── 6_Partitioning_Lab.py    <- Spatial partitioning & 3D KD-Tree lookup
│   └── 7_Benchmarking_Suite.py  <- Automated benchmarking & artifact export
│
├── src/                         <- Modular Core Implementation
│   ├── algorithms/              <- Custom Dijkstra, A*, Bidirectional Dijkstra, BFS, DFS
│   ├── analytics/               <- Centrality, connectivity, percolation, MST
│   ├── benchmarks/              <- Query generators, benchmark runner, statistics
│   ├── graph/                   <- OSMnx loader, GraphML storage, validation, sampler
│   ├── indexing/                <- 3D ECEF KD-Tree spatial index
│   ├── partitioning/            <- Geographic bisection, graph-aware region growing
│   ├── routing/                 <- RoutingService & Yen's alternative paths
│   ├── simulation/              <- Scenario builder & active subgraph engine
│   ├── ui/                      <- Reusable Streamlit components & styling
│   └── visualization/           <- PyDeck map builders & Altair chart generators
│
├── data/                        <- Data Cache & Offline Datasets
│   ├── cache/                   <- Pre-cached GraphML networks (Chandigarh Core)
│   └── samples/                 <- Offline synthetic grid graphs
│
├── docs/                        <- Comprehensive Academic & Technical Documentation
│   ├── installation_guide.md    <- Step-by-step Windows setup instructions
│   ├── user_manual.md           <- Dashboard operational manual
│   ├── system_architecture.md   <- Multi-tier architecture & data flows
│   ├── mathematical_model.md    <- Formal graph models & heuristic proofs
│   ├── algorithms_explained.md  <- Mechanics, data structures & pseudocode
│   ├── algorithm_complexity.md  <- Asymptotic time and space complexity table
│   ├── syllabus_mapping.md      <- Modules 1–5 curriculum alignment matrix
│   ├── experimental_methodology.md <- Benchmarking protocols & instrumentation
│   ├── experimental_results.md  <- Measured runtime, node & memory findings
│   ├── project_report.md        <- Formal academic project report
│   ├── viva_questions.md        <- 65-question viva examination question bank
│   ├── demo_walkthrough.md      <- 10-minute college viva demonstration script
│   ├── presentation_outline.md  <- 15-slide academic presentation outline
│   ├── known_limitations.md     <- Architectural & domain constraints disclosure
│   ├── future_scope.md          <- Realistic post-academic research horizons
│   └── final_verification.md    <- Final readiness certification
│
├── results/                     <- Experimental Output & QA Artifacts
│   ├── benchmarks/              <- Exported raw CSVs, summary tables & manifests
│   ├── final/                   <- Official benchmark summary & manifest
│   └── qa/                      <- JUnit XML, test reports & performance profile CSV
│
├── scripts/                     <- Automated Verification & Profiling Scripts
│   ├── verify_all.py            <- Master verification running all phase suites
│   ├── verify_demo.py           <- End-to-end 20-step demonstration verification
│   └── profile_application.py   <- Application runtime & memory profiler
│
└── tests/                       <- Automated Test Suite (260 Passing Tests)
```

---

## 5. Quick Start (Windows & Python 3.11)

### Step 1: Create & Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run Master System Verification
```powershell
python scripts/verify_all.py
```

### Step 4: Launch the Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 6. Testing & Quality Assurance Summary

```powershell
python -m pytest
```
```text
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-8.3.5
collected 260 items

260 passed in 14.21s (100% pass rate)
```

All 177 repository files pass static analysis with zero errors:
```powershell
python -m ruff check .
```

---

## 7. Syllabus Coverage Matrix (Modules 1–5)

| Syllabus Module | Key Topics Covered | Implemented Code | Dashboard Page |
|---|---|---|---|
| **Module 1: Graph Fundamentals** | Directed multigraphs, parallel edges, GraphML, matrices | `src/graph/` | `1_Network_Overview.py` |
| **Module 2: Traversal & Spatial** | BFS hop minimality, DFS cycles, Haversine formula | `src/algorithms/traversal.py` | `2_Traversal_Lab.py` |
| **Module 3: Partitioning & Indexing** | Geographic bisection, region growing, 3D KD-Tree | `src/partitioning/`, `src/indexing/` | `6_Partitioning_Lab.py` |
| **Module 4: Shortest Paths & Routing** | Dijkstra, A*, Bidirectional Dijkstra, Yen's K-paths | `src/algorithms/`, `src/routing/` | `3_Route_Optimizer.py` |
| **Module 5: Analytics & Resilience** | Centrality, percolation, MSF, benchmarking | `src/analytics/`, `src/benchmarks/`| `4_`, `5_`, `7_` pages |

---

## 8. Measured Performance Highlights

- **Route Cost Optimality:** 100% agreement between manual Dijkstra, manual A*, manual Bidirectional Dijkstra, and NetworkX ground truth ($0.000000$ deviation).
- **Search Space Pruning:**
  - A* reduces explored nodes by **32.7%** compared to Dijkstra.
  - Bidirectional Dijkstra reduces explored nodes by **45.0%** compared to Dijkstra.
- **Spatial Nearest-Node Query Speedup:**
  - 3D ECEF KD-Tree achieves a **25x to 52x speedup** over linear brute-force scanning.
- **Resilience Vulnerability:**
  - Targeted removal of the top 15%–20% of high-betweenness hubs destroys network connectivity, while random node failure preserves connectivity beyond 40% node loss.

---

## 9. Academic Prototype Notice

SmartRoute Analytics is an academic research and demonstration prototype developed for coursework evaluation. It is not designed or certified for real-world emergency vehicle dispatch, live GPS telemetry, or municipal traffic signal preemption.
