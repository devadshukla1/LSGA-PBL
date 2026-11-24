# MetroGraph Analytics

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/pytest-120%2B%20passed-brightgreen.svg)]()
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Zero OSMnx Guarantee](https://img.shields.io/badge/maps-100%25%20offline%20schematic-green.svg)]()

> **Academic Capstone Title:** *Intelligent Metro Route Optimization and Critical Station Analysis Using Graph Algorithms*

MetroGraph Analytics is an interactive transit network modeling, multi-objective route optimization, structural centrality analysis, and network resilience simulation platform built with Python, NetworkX, Plotly, and Streamlit.

---

## 🚇 Project Highlights & Key Features

- **MultiGraph Representation:** Accurately models parallel metro services and branch lines operating on shared track infrastructure using `networkx.MultiGraph`.
- **6 Routing Objectives:**
  1. **Minimum Stops (BFS):** Unweighted shortest-hop station paths.
  2. **Minimum Travel Time (Dijkstra):** Segment travel time minimization.
  3. **Minimum Distance (Dijkstra):** Physical track distance minimization.
  4. **Minimum Transfers (0-1 BFS):** Line-switch minimization on an expanded state graph $(V \times L)$.
  5. **Minimum Transfers, Then Fastest (Lexicographic):** Sequential multi-objective optimization.
  6. **Transfer-Aware Dijkstra:** Incorporates configurable platform friction penalties (0–15 min).
- **Structural Station Importance:**
  - Normalized **Degree Centrality** on projected simple graphs.
  - Brandes **Betweenness Centrality** identifying topological bridge stations.
  - Tarjan DFS **Articulation Point (Cut-Vertex)** detection identifying single points of failure.
- **Station Closure & Resilience Simulator:**
  - Non-destructive simulations executing on isolated graph copies (`graph.copy()`).
  - Topological fragmentation analysis and pairwise reachability loss:
    $$\text{Reachable Pairs} = \sum_{i=1}^k \frac{n_i(n_i - 1)}{2}$$
  - Automated commuter detour recalculation with visual severed-link rendering.
- **Interactive Offline Dashboard:**
  - Built with Streamlit in a professional dark theme (`#0B1120`, `#1E293B`, `#38BDF8`).
  - Zero external map/tile dependencies (strictly Plotly schematic layout).
  - CSV and JSON artifact export center for itineraries, metrics, and GraphML caches.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.11.x | Core execution environment |
| **Graph Model** | NetworkX 3.2+ | In-memory MultiGraph & algorithm baseline |
| **Data Processing** | Pandas 2.2+, NumPy 1.26+ | Dataset validation, metrics computation |
| **Visualization** | Plotly 5.24+ | Interactive offline network & route rendering |
| **Web Interface** | Streamlit 1.40+ | Reactive multipage dashboard & session caching |
| **Quality & Tests**| Pytest, Streamlit AppTest, Ruff | Testing suite & zero-defect linting |

---

## 🚀 Quickstart & Installation (Windows PowerShell)

```powershell
# 1. Clone or navigate to the repository
cd "C:\Users\devad\OneDrive\Desktop\LSGA PBL"

# 2. Create and activate a Python 3.11 virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Launch the Streamlit dashboard
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing, Benchmarking & Reproduction

### Run Complete Test Suite
```powershell
python -m pytest -v
```

### Run Static Analysis & Linter
```powershell
python -m ruff check .
```

### Run Performance Benchmarks
```powershell
python scripts\benchmark_algorithms.py
```

### Reproduce All Experimental Results
```powershell
python scripts\reproduce_results.py --dataset metro --benchmarks
```

### Master Phase 8 System Verification
```powershell
python scripts\verify_final_project.py
```

---

## 📂 Project Structure

```
LSGA PBL/
|-- app.py                              # Main Streamlit Landing Dashboard
|-- config.py                           # Central System Settings & Path Resolution
|-- requirements.txt                    # Project Dependencies
|-- pyproject.toml                      # Tooling & Linting Config
|-- README.md                           # Master Project Documentation
|
|-- data/
|   |-- sample/                         # Offline Synthetic Grid (12 Stations, 3 Lines)
|   |-- metro/                          # Real Delhi Metro Network (260 Stations, 13 Lines)
|   |-- processed/                      # Cached GraphML Graph Serializations
|
|-- src/
|   |-- core/                           # Logging, Configuration, Exception Classes
|   |-- data/                           # Relational CSV Loaders & Schema Validators
|   |-- graph/                          # MultiGraph Builder & Interchange Detection
|   |-- algorithms/                     # BFS, Dijkstra, 0-1 BFS, Lexicographic Routing
|   |-- analytics/                      # Centralities, Tarjan Cut-Vertices, Rankings
|   |-- simulation/                     # Closure Engine, Reachability, Detour Rerouting
|   |-- visualization/                  # Plotly Schematic Plots & Route Maps
|   |-- ui/                             # Design System, Components, Session State
|
|-- pages/
|   |-- 1_Metro_Overview.py             # Network Map, Line Filters & Registries
|   |-- 2_Route_Planner.py              # 6-Objective Routing Engine & Directions
|   |-- 3_Station_Importance.py         # Centrality Heatmap & Station Comparisons
|   |-- 4_Closure_Simulator.py          # Station Outages, Fragmentations & Detours
|   |-- 5_Algorithm_Lab.py              # Theoretical Bounds & Live Latency Charts
|   |-- 6_Results.py                    # CSV/JSON Data & Report Export Center
|
|-- tests/
|   |-- unit/                           # Property-Based Invariant Tests
|   |-- integration/                    # Dashboard UI AppTest & Module Tests
|   |-- system/                         # Full End-to-End Workflow Tests
|
|-- scripts/
|   |-- benchmark_algorithms.py         # High-Resolution Microbenchmarking Suite
|   |-- run_route_experiments.py        # Multi-Objective Route Comparison Runner
|   |-- run_station_analysis.py         # Centrality & Ranking Experiment Runner
|   |-- run_resilience_experiments.py   # Outage Resilience Experiment Runner
|   |-- reproduce_results.py            # Master Results Reproduction Script
|   |-- verify_final_project.py         # Complete Phase 8 Submission Verifier
|
|-- results/
|   |-- benchmarks/                     # Benchmark CSVs, Summary JSON, HTML Charts
|   |-- experiments/                    # Experimental Route, Centrality & Closure CSVs
|   |-- reports/                        # Visual Reports & Top 10 Centrality Charts
|
|-- docs/
|   |-- final_project_audit.md          # Comprehensive Component Status Audit
|   |-- final_project_report.md         # Full Academic Research & Capstone Report
|   |-- windows_installation.md         # Detailed Windows PowerShell Setup Guide
|   |-- architecture.md                 # System Architecture & Mermaid Diagram
|   |-- presentation_outline.md         # 14-Slide Evaluation Deck Structure
|   |-- demo_script.md                  # 5-7 Minute Live Examiner Demonstration
|   |-- viva_questions.md               # 42 Comprehensive Viva Questions & Answers
```

---

## 📊 Dataset Invariants & Ethical Transparency

- **Schematic Visualization Notice:** Station coordinates and track links are plotted schematically. They represent topological metro connections, not surveyed railway vector curves.
- **Zero Fabricated Results:** All reported timings and metrics reflect actual code execution using Python's high-resolution timers (`time.perf_counter_ns()`).
- **Academic Disclaimer:** The application provides structural analysis. It does not predict live signaling train delays or real-time passenger crowd movements.
