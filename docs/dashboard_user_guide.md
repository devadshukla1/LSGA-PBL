# MetroGraph Analytics — Dashboard User Guide

Welcome to the **MetroGraph Analytics** interactive dashboard. This application provides real-time route optimization, transit line transfer analysis, structural station importance evaluation, and simulated network resilience analysis using graph-theoretical algorithms.

---

## 1. Installation & Quickstart

### Prerequisites
- Python >= 3.11, < 3.13
- Virtual environment (`.venv`) with dependencies installed via `pip install -r requirements.txt`.

### Launching the Dashboard
Run the Streamlit application from the root directory:
```bash
streamlit run app.py
```
The interface will automatically launch in your browser at `http://localhost:8501`.

---

## 2. Global Navigation & Sidebar Controls

The sidebar persists across all six application pages:
- **Active Metro Dataset:** Toggle between the synthetic benchmark grid (12 stations) and the Delhi Metro Network (260 stations, 13 lines).
- **Persistent State Invalidation:** Changing the dataset automatically flushes stale routes, closure simulations, and analytics caches to prevent data mixing.
- **Runtime Parameters:** Displays operational defaults (NetworkX MultiGraph model, 5.0 min transfer penalty, 35.0 km/h commercial transit speed).

---

## 3. Application Pages & Capabilities

### Page 0: Landing Dashboard (`app.py`)
- High-level topology overview (`|V|`, `|E|`, interchange hubs).
- Offline Plotly schematic network diagram.
- Quick navigation shortcuts and dataset provenance card.

### Page 1: Metro Overview (`1_Metro_Overview.py`)
- Real-time line-by-line filtering.
- Interchange-only station filtering.
- Interactive system registries (Stations, Lines, Multi-edges, Interchange Hubs).
- Baseline reachability pair counts $\sum \frac{n_i(n_i-1)}{2}$.

### Page 2: Smart Route Planner (`2_Route_Planner.py`)
- Multi-objective routing:
  1. **Minimum Transfers (0-1 BFS)**: Minimizes line transitions on an expanded state graph $(V \times L)$.
  2. **Minimum Transfers, Then Fastest (Lexicographic Dijkstra)**: Optimizes transfers first, using travel time as a secondary objective.
  3. **Fastest with Transfer Penalty**: Integrates custom platform friction penalties (0–15 min).
  4. **Minimum Stops (BFS)**: Unweighted shortest path on station vertices.
  5. **Minimum Travel Time (Dijkstra)**: Physical segment travel time minimization.
  6. **Minimum Distance (Dijkstra)**: Physical track distance minimization.
- Visual route highlighting and step-by-step passenger transfer directions.

### Page 3: Station Importance (`3_Station_Importance.py`)
- Degree Centrality and Betweenness Centrality rankings.
- Centrality Heatmap with Cut-Vertex (Articulation Point) markers.
- Side-by-side pairwise station comparison table.

### Page 4: Closure Simulator (`4_Closure_Simulator.py`)
- Simulate single or multi-station closures without mutating the active graph.
- Topological impact table: Component count, core component retention, and lost reachable pairs.
- Automatic commuter detour recalculation (Status: `UNCHANGED`, `REROUTED`, `UNREACHABLE`, `ENDPOINT_CLOSED`).
- Red dotted severed track visualization.

### Page 5: Algorithm Lab (`5_Algorithm_Lab.py`)
- Theoretical vs. empirical complexity comparison table.
- Live multi-algorithm execution profiler with Plotly runtime latency charts.
- Single-station removal and centrality algorithm execution timing.

### Page 6: Results & Exports (`6_Results.py`)
- Download active dataset CSVs (Stations, Lines, Connections, Station-Lines).
- Export route itineraries (CSV & JSON).
- Export centrality rankings and interchange registries (CSV).
- Export resilience simulation metrics table (CSV) and full simulation payload (JSON).
- Generate and cache GraphML graph artifacts.

---

## 4. Architectural Guarantees
- **Zero External Map Dependencies:** Strictly offline Plotly coordinates without OSMnx, Leaflet, or Mapbox API keys.
- **Thread-Safe Graph Immutability:** All simulations run on deep isolated copies (`graph.copy()`).
