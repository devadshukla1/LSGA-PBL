# MetroGraph Analytics: Implementation Roadmap (Phases 1–8)

## Overview
MetroGraph Analytics is structured into 8 modular phases to ensure high software quality, rigorous testing, and clear boundaries between architecture, algorithms, analytics, and benchmarking.

---

### Phase 1: Project Foundation & Architecture
- **Status**: ✅ **COMPLETED**
- **Deliverables**: Modular architecture, central config, sample data, base MultiGraph builder, Plotly offline view, 6 Streamlit pages.

---

### Phase 2: Metro Dataset & Graph Construction
- **Status**: ✅ **COMPLETED**
- **Deliverables**:
  - Ingestion and normalization of the real Delhi Metro network dataset (260 stations, 13 lines, 273 connections).
  - Explicit relational schema: `stations.csv`, `lines.csv`, `connections.csv`, `station_lines.csv`, and `metadata.json`.
  - Structural interchange detection identifying 25 transit hubs (`src/graph/interchanges.py`).
  - NetworkX `MultiGraph` construction preserving parallel edges and line-specific service keys.
  - Basic connectivity diagnostics (connected components, isolated stations, average degree).
  - GraphML export and round-trip caching in `data/processed/` with metadata sidecar.
  - Dynamic dataset selector in the Streamlit sidebar allowing live switching between Delhi Metro and Synthetic Sample.
  - Interactive line filtering and interchange-only display on the offline Plotly schematic.
  - 25 automated pytest tests passing, 0 Ruff lint errors, and verified Streamlit `AppTest` execution across all 7 pages.

---

### Phase 3: BFS & Dijkstra Routing
- **Status**: ✅ **COMPLETED**
- **Deliverables**:
  - Pure manual BFS unweighted shortest-path routing algorithm (`src/algorithms/bfs.py`).
  - Pure manual Dijkstra weighted shortest-path routing algorithm with binary heap (`src/algorithms/dijkstra.py`).
  - MultiGraph parallel edge preservation and deterministic tie-breaking (`src/algorithms/route_utils.py`).
  - Head-to-head multi-algorithm comparison engine (`src/algorithms/comparison.py`).
  - Interactive Route Planner UI (`pages/2_Route_Planner.py`) with metric cards, station-by-station itinerary, segment tables, and algorithm comparison.
  - Interactive highlighted route visualizer in Plotly (`plot_metro_route` in `src/visualization/metro_plot.py`).
  - 44 passing automated pytest test cases covering BFS, Dijkstra, parallel edges, edge cases, and NetworkX oracle comparisons.
  - Routing verification script (`scripts/verify_routing.py`) verifying exact matches with NetworkX.

---

### Phase 4: Minimum Transfer Optimization
- **Status**: ⏳ **NEXT**
- **Objective**: Implement exact single-criterion routing algorithms.
- **Key Tasks**:
  - Unweighted Breadth-First Search (BFS) for minimum station hops.
  - Priority-queue Dijkstra's algorithm for minimum estimated travel time and track distance.
  - Path reconstruction utilities and step-by-step route itineraries.

---

### Phase 4: Minimum Transfer Optimization
- **Status**: ⏳ **PLANNED**
- **Objective**: Solve the multi-objective line-transfer penalty routing challenge.
- **Key Tasks**:
  - State-expanded graph representation `(Station, Line)` to explicitly capture line switching friction.
  - Configurable transfer penalty addition (default 5.0 minutes).
  - Comparative path analysis showing trade-offs between speed and transfer comfort.

---

### Phase 5: Station Importance Analysis
- **Status**: ⏳ **PLANNED**
- **Objective**: Quantify structural transit criticality using graph centrality theory.
- **Key Tasks**:
  - Degree centrality (direct connectivity).
  - Betweenness centrality (shortest path bridging bottleneck identification).
  - Closeness centrality (average network accessibility).
  - Critical station ranking tables and network heatmap overlays.

---

### Phase 6: Closure & Resilience Simulation
- **Status**: ⏳ **PLANNED**
- **Objective**: Simulate network vulnerability under disruptions and unplanned closures.
- **Key Tasks**:
  - Targeted node (station) and edge (track segment) outage simulations.
  - Calculation of giant connected component degradation and isolated stations.
  - Commuter rerouting delay impact and bottleneck spillover analysis.

---

### Phase 7: Professional Dashboard
- **Status**: ⏳ **PLANNED**
- **Objective**: Elevate the UI/UX with route comparison panels, interactive itinerary cards, and custom station filters.
- **Key Tasks**:
  - Synchronized side-by-side route path comparisons.
  - Visual route trace overlays on the offline Plotly schematic.
  - Enhanced accessibility and responsiveness.

---

### Phase 8: Testing, Benchmarking & Report
- **Status**: ⏳ **PLANNED**
- **Objective**: Final empirical benchmarking, academic report compilation, and presentation assets.
- **Key Tasks**:
  - Multi-iteration latency benchmarks across varying path lengths and graph densities.
  - Memory profiling and scalability verification.
  - CSV and JSON report exports.
  - Academic viva demonstration materials.
