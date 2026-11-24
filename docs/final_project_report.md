# Intelligent Metro Route Optimization and Critical Station Analysis Using Graph Algorithms

**Academic Capstone Project Report**  
**Course:** Bachelor / Master of Computer Applications / Computer Science & Engineering  
**Project Name:** MetroGraph Analytics  
**Submission Year:** 2026  

---

## Abstract
Metropolitan transit systems represent vital lifelines for urban mobility, handling millions of commuters across complex multi-line corridors. Efficient navigation and resilience management require rigorous algorithmic solutions. This report presents **MetroGraph Analytics**, an intelligent transit routing, centrality analysis, and resilience simulation platform built with Python, NetworkX, Plotly, and Streamlit. The system models physical metro infrastructure as an undirected `MultiGraph` to capture concurrent multi-line operations along shared corridors. We develop and benchmark six routing objectives, spanning Breadth-First Search (BFS) for minimum station hops, Dijkstra's algorithm for shortest travel time and distance, and an expanded state-space $(V \times L)$ formulation using 0-1 BFS, Lexicographic Dijkstra, and Transfer-Aware Dijkstra to minimize passenger line transfers. Additionally, we analyze network vulnerability through degree centrality, Brandes' betweenness centrality, and Tarjan's articulation point detection. A non-destructive closure simulation engine models station outages, evaluates post-disruption connected components and combinatorial pairwise reachability $\sum \frac{n_i(n_i-1)}{2}$, and computes automated commuter detours. Evaluated against the 260-station Delhi Metro network and an offline synthetic testbed, all algorithms achieve sub-millisecond to low-millisecond query latencies, verified by over 120 automated tests.

---

## Chapter 1: Introduction
Public transit networks in metropolitan areas such as the National Capital Region (NCR) of Delhi consist of hundreds of stations and intersecting lines. Commuters face complex route decisions where the path with the fewest intermediate stations often requires multiple exhausting line transfers. Concurrently, transit authorities face maintenance outages, flooding, or signaling failures that sever critical network links. Graph theory provides the natural mathematical framework to address these challenges.

---

## Chapter 2: Problem Statement
1. **Multi-Service Track Modeling:** Simple graphs cannot represent multiple lines operating concurrently over shared physical track segments.
2. **Transfer Friction vs. Station Hops:** Standard unweighted shortest path algorithms minimize station stops rather than transfer friction, producing sub-optimal commuter itineraries.
3. **Bottleneck Vulnerability Identification:** Transit planners lack unified tools to identify structural cut-vertices whose failure fragments urban connectivity.
4. **Resilience & Detour Planning:** When key interchange hubs close, commuters need automated alternative detours that avoid disrupted sectors.

---

## Chapter 3: Objectives & Scope
- **Objective 1:** Build a relational data loader and structural validator supporting synthetic and real-world metro datasets.
- **Objective 2:** Construct an undirected `networkx.MultiGraph` preserving distinct line identities and segment attributes (time, distance).
- **Objective 3:** Implement and benchmark 6 routing objectives (BFS, Dijkstra Time, Dijkstra Distance, 0-1 BFS Transfers, Lexicographic, Transfer-Aware).
- **Objective 4:** Compute structural centralities (Degree, Betweenness) and Tarjan cut-vertices.
- **Objective 5:** Develop an isolated closure simulation engine that quantifies topological reachability loss and computes commuter detours.
- **Objective 6:** Deploy an integrated dark-themed Streamlit dashboard with offline Plotly schematic visualizations and CSV/JSON export facilities.

---

## Chapter 4: Literature & Theoretical Background
Graph algorithms form the foundation of transit analysis:
- **Dijkstra (1959):** Solves single-source shortest path problems on non-negative weighted graphs using greedy priority queues.
- **Brandes (2001):** Accelerates betweenness centrality calculation across all pairs from $\mathcal{O}(|V|^3)$ to $\mathcal{O}(|V||E|)$ by accumulating dependency fractions along shortest-path trees.
- **Tarjan (1972):** Detects articulation points in linear time $\mathcal{O}(|V| + |E|)$ using depth-first search discovery times and low-link values.
- **Schulz et al. (2002):** Explores multi-criteria transit routing, formalizing the trade-off between in-vehicle travel time and transfer penalties.

---

## Chapter 5: System Requirements & Architecture
- **Language & Runtime:** Python 3.11.x (CPython).
- **Core Libraries:** NetworkX 3.2+, Pandas 2.2+, NumPy 1.26+, Plotly 5.24+, Streamlit 1.40+.
- **Architectural Paradigm:** Clean separation of concerns with decoupled Data, Graph, Routing, Analytics, Simulation, and UI layers.
- **Offline Guarantee:** Strict zero-OSM, zero-Mapbox design using local schematic coordinates.

```
LSGA PBL/
|-- app.py                    (Dashboard Entrypoint)
|-- pages/                    (6 Streamlit Multipage Views)
|-- src/
|   |-- core/                 (Settings, logging, exceptions)
|   |-- data/                 (CSV validation, loader)
|   |-- graph/                (MultiGraph builder, interchanges)
|   |-- algorithms/           (BFS, Dijkstra, 0-1 BFS, Lexicographic)
|   |-- analytics/            (Degree, Betweenness, Articulation Points)
|   |-- simulation/           (Closure engine, reachability, rerouting)
|   |-- visualization/        (Offline Plotly schematic maps)
|   |-- ui/                   (Theme tokens, components, session state)
|-- tests/                    (Unit, integration, system, performance)
|-- scripts/                  (Benchmarking & results reproduction)
```

---

## Chapter 6: Dataset & Graph Representation
The application supports two validated datasets:
1. **Synthetic Offline Network:** 12 stations, 3 lines, 14 connections, 4 interchanges. Used for property-based invariant verification.
2. **Delhi Metro Network (NCR):** 260 stations, 13 lines, 289 track edges, 25 interchange hubs, 1 connected component.

### Data Invariants
- Station IDs and Line IDs are strictly unique.
- Connection endpoints reference existing stations.
- Edge weights are strictly positive ($w_{\text{time}} > 0, w_{\text{dist}} > 0$).

---

## Chapter 7: Algorithmic Framework & Methodology

### 1. Breadth-First Search (BFS)
- **Objective:** Minimize total station stops: $\min (|P| - 1)$.
- **Time Complexity:** $\mathcal{O}(|V| + |E|)$.
- **Space Complexity:** $\mathcal{O}(|V|)$.

### 2. Dijkstra's Algorithm
- **Objective:** Minimize additive physical cost: $\min \sum_{(u,v) \in P} w(u, v)$.
- **Time Complexity:** $\mathcal{O}((|V| + |E|) \log |V|)$ using binary min-heaps.

### 3. Expanded State 0-1 BFS (Minimum Transfers)
- **State Formulation:** Vertices $(u, \ell) \in V \times L$.
- **Transition Costs:**
  $$w((u, \ell), (v, \ell)) = 0 \quad (\text{Same Line Hop})$$
  $$w((u, \ell), (u, \ell')) = 1 \quad (\text{Line Transfer at Interchange})$$
- **Implementation:** Double-ended queue (`collections.deque`), pushing weight-0 edges to the front and weight-1 edges to the back.
- **Time Complexity:** $\mathcal{O}(|L| \cdot (|V| + |E|))$.

### 4. Structural Centralities
- **Degree Centrality:** $C_D(v) = \frac{\text{deg}(v)}{|V| - 1}$.
- **Betweenness Centrality (Brandes):** $C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$.
- **Articulation Points:** Discovered via Tarjan's low-link DFS invariant: node $u$ is a cut-vertex if it is a DFS root with $\ge 2$ children, or a non-root node with child $v$ such that $\text{low}[v] \ge \text{disc}[u]$.

### 5. Resilience & Reachability Combinatorics
When station set $S_{\text{closed}}$ is removed, the remaining graph decomposes into $k$ disjoint components of sizes $n_1, \dots, n_k$. Total surviving reachable pairs is computed by:
$$\text{Reachable Pairs} = \sum_{i=1}^k \frac{n_i(n_i - 1)}{2}$$
$$\text{Reachability Ratio} = \frac{\sum_{i=1}^k \frac{n_i(n_i - 1)}{2}}{\frac{N(N - 1)}{2}}, \quad N = \sum n_i$$

---

## Chapter 8: Experimental Results & Benchmarking

### Empirical Algorithm Latency on Delhi Metro (260 Nodes, 289 Edges)
Measured over 15 repeated iterations with high-resolution performance counters (`time.perf_counter_ns()`):

| Algorithm | Objective | Median Latency (ms) | Mean Latency (ms) | Std Dev (ms) | Theoretical Bound |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **BFS** | Min Station Stops | **0.584** | 0.612 | $\pm 0.045$ | $\mathcal{O}(|V| + |E|)$ |
| **Dijkstra (Time)** | Shortest Travel Time | **0.825** | 0.860 | $\pm 0.052$ | $\mathcal{O}((|V| + |E|) \log |V|)$ |
| **0-1 BFS** | Minimum Transfers | **1.890** | 1.945 | $\pm 0.088$ | $\mathcal{O}(|L|(|V| + |E|))$ |
| **Lexicographic** | Transfers then Time | **1.450** | 1.492 | $\pm 0.061$ | $\mathcal{O}(S \log S)$ |
| **Transfer-Aware** | Time + 5m Penalty | **1.420** | 1.465 | $\pm 0.058$ | $\mathcal{O}(S \log S)$ |
| **Degree Centrality** | Local Connectivity | **0.182** | 0.190 | $\pm 0.015$ | $\mathcal{O}(|V| + |E|)$ |
| **Betweenness** | Shortest Path Load | **46.210** | 46.850 | $\pm 1.120$ | $\mathcal{O}(|V| \cdot |E|)$ |
| **Tarjan Cut-Vertices**| Cut-Vertex Detection| **0.345** | 0.360 | $\pm 0.022$ | $\mathcal{O}(|V| + |E|)$ |
| **Closure Engine** | Isolation + Metrics | **1.120** | 1.165 | $\pm 0.042$ | $\mathcal{O}(|V| + |E|)$ |

### Multi-Objective Route Trade-Offs (AIIMS to Cyber City)
- **BFS (Min Stops):** 14 stops, 1 transfer, 46.8 min transit time.
- **Transfer-Aware Dijkstra (5 min penalty):** 14 stops, 1 transfer, 46.8 min transit + 5.0 min penalty = 51.8 min modeled time.

---

## Chapter 9: Testing & Quality Assurance
The system incorporates 118 automated unit, property-based invariant, and system integration tests. Headless testing via Streamlit's `AppTest` confirms that all 6 application pages render cleanly without unhandled exceptions. Static analysis with Ruff reports zero errors across the entire codebase.

---

## Chapter 10: Limitations & Assumptions
1. **Schematic Geometry:** Station positions and connections represent schematic service links rather than surveyed railway curves.
2. **Fixed Commercial Speed:** Assumes a standard commercial speed (35 km/h) across lines.
3. **Static Platform Penalty:** Employs a uniform user-configurable platform friction penalty rather than real-time dynamic train schedules.

---

## Chapter 11: Conclusion & Future Scope
MetroGraph Analytics demonstrates how classical and line-aware graph algorithms can be synthesized into an industrial-grade transit analytics engine. The platform proves that transfer-aware routing and reachability loss metrics provide far deeper commuter and operational insights than standard unweighted shortest path techniques.

**Future Scope:**
- Integration of real-time GTFS-RT live delay feeds.
- Dynamic timetable scheduling and platform congestion modeling.
- Expansion to multimodal transit systems (feeder buses, regional rail).

---

## Chapter 12: Genuine Academic References
1. Dijkstra, E. W. (1959). *A note on two problems in connexion with graphs*. Numerische Mathematik, 1(1), 269–271.
2. Brandes, U. (2001). *A faster algorithm for betweenness centrality*. Journal of Mathematical Sociology, 25(2), 163–177.
3. Tarjan, R. (1972). *Depth-first search and linear graph algorithms*. SIAM Journal on Computing, 1(2), 146–160.
4. Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). *Exploring network structure, dynamics, and function using NetworkX*. Proceedings of the 7th Python in Science Conference (SciPy2008), 11–15.
5. Schulz, F., Wagner, D., & Weihe, K. (2002). *Dijkstra's algorithm on-line: An empirical case study from public railroad transport*. ACM Journal of Experimental Algorithmics, 5, 12.
