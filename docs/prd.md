# MetroGraph Analytics: Product Requirements Document (PRD)

## 1. Executive Summary
**MetroGraph Analytics** (*Intelligent Metro Route Optimization and Critical Station Analysis Using Graph Algorithms*) is a modular, high-reliability academic application engineered to study, simulate, and optimize urban rail transit networks using classical and advanced graph algorithms.

## 2. Problem Statement
Urban metro networks are complex topological systems carrying millions of commuters daily. Commuters face trade-offs between stop counts, travel time, and line-transfer penalties. Concurrently, transit planners must evaluate vulnerability to station failures, track closures, and bottleneck congestion. Existing GIS and road tools (like OSMnx or Overpass) are heavy, non-offline, and poorly suited for schematic, multi-line rail transit topologies.

MetroGraph Analytics addresses this with a tailored graph analytics architecture:
- Fast multi-objective routing (BFS for minimum stops, Dijkstra for shortest travel time, and transfer-penalty minimization).
- Graph-theoretic vulnerability analysis (degree, betweenness, closeness centralities, and disruption simulations).
- Completely offline operational capability with zero mandatory external API dependencies.

## 3. Target Users
- **Academic Evaluators & Researchers**: Demonstrating graph data structures and algorithmic complexity under real-world constraints.
- **Urban Transit Engineers**: Simulating network resilience, maintenance outages, and passenger rerouting.
- **Commuters & Transit Planners**: Evaluating travel time tradeoffs and transfer friction.

## 4. Scope & Functional Requirements

### In Scope (Phases 1–8 Roadmap)
1. **Network Visualization**: Interactive offline schematic graph visualization highlighting lines and interchange hubs.
2. **Multi-Objective Routing**:
   - Minimum stops (BFS traversal).
   - Shortest travel time (Dijkstra algorithm).
   - Minimum transfer routing (state-expanded multi-line penalty model).
3. **Station Criticality Analysis**: Degree, betweenness, and closeness centrality computation.
4. **Resilience & Closure Simulation**: Dynamic station/segment removal and network fragmentation tracking.
5. **Algorithm Benchmarking**: Empirical runtime and memory profiling comparing theoretical vs observed bounds.
6. **Data Portability**: Standardized CSV/JSON import and export pipelines.

### Excluded from Scope
- General road network processing (no OSMnx, Overpass API, or street-level routing).
- High-latency external mapping APIs (no mandatory Leaflet/OSM tile fetching).
- Microscopic train signaling, timetabling blocks, or rolling stock dispatch.
- External database servers (PostgreSQL, Redis, MongoDB) or container virtualization.

## 5. Non-Functional Requirements
- **Performance**: Graph construction and routing queries execute in under 100ms on networks of up to 500 stations.
- **Offline Reliability**: Application boots and functions completely without internet access.
- **Code Quality**: Strict PEP 8 adherence, zero Ruff lint errors, 100% passing pytest suites, and clean modular architecture.
- **Platform Compatibility**: Native local execution on Windows 10/11 using Python 3.11+.
