# Academic Presentation Outline: MetroGraph Analytics

**Slide 1: Title Slide**
- **Title:** MetroGraph Analytics: Intelligent Metro Route Optimization and Critical Station Analysis Using Graph Algorithms
- **Subtitle:** Undergraduate Capstone Project in Computer Applications / Data Science
- **Presenter:** [Student Name / Roll Number]

**Slide 2: Motivation & Problem Statement**
- Modern metropolitan transit networks face daily passenger demand and unforeseen structural disruptions.
- Commuters require multi-objective route guidance (minimum stops vs. minimum transfers vs. fastest travel time).
- Transit planners need quantitative tools to detect topological bottlenecks and evaluate network vulnerability during station closures.

**Slide 3: Project Objectives**
1. Model complex metro topologies with parallel services using NetworkX MultiGraphs.
2. Implement and benchmark 6 routing objectives (BFS, Dijkstra, 0-1 BFS, Lexicographic, Transfer-Aware).
3. Compute structural centralities and Tarjan cut-vertices (articulation points).
4. Simulate station outages and evaluate topological reachability fragmentation.
5. Deliver an offline, interactive Streamlit dashboard.

**Slide 4: System Architecture & Technology Stack**
- **Core Technology:** Python 3.11, NetworkX, Pandas, NumPy.
- **Visualization:** Plotly (Strictly offline schematic coordinate engine).
- **Interface:** Streamlit (Dark theme design system, cached session state).
- **Quality Assurance:** Pytest (120+ tests), Ruff linter.

**Slide 5: Graph Representation & MultiGraph Invariants**
- Why MultiGraph? Accommodates multiple metro lines operating concurrently on shared track corridors.
- State Representation: Expanded states $(v, \ell) \in V \times L$ for line-aware transfer optimization.
- Dataset Scope: Real Delhi Metro Network (260 stations, 13 lines, 25 interchanges) and offline synthetic testbed.

**Slide 6: Routing Engine: BFS vs. Dijkstra**
- **BFS:** Minimizes unweighted station stops ($\mathcal{O}(|V| + |E|)$).
- **Dijkstra:** Minimizes physical track travel time or distance ($\mathcal{O}((|V| + |E|) \log |V|)$).
- Empirical finding: Minimum-stop journeys often require unnecessary line transfers that increase total trip friction.

**Slide 7: Minimum Transfer Optimization (0-1 BFS)**
- Formulated on expanded routing states where riding along the same line costs 0 and switching lines costs 1.
- Solved efficiently via double-ended queue (deque) in $\mathcal{O}(|L| \cdot (|V| + |E|))$.
- Generates step-by-step passenger walking instructions.

**Slide 8: Station Importance & Centrality Analysis**
- **Degree Centrality:** Measures immediate physical station neighbors.
- **Betweenness Centrality (Brandes):** Identifies stations bridging disparate metro corridors.
- **Articulation Points (Tarjan DFS):** Identifies critical cut-vertices whose failure partitions the network.
- Top Delhi Metro Bridge: Rajiv Chowk (`STN199`) and Hauz Khas (`STN065`).

**Slide 9: Station Closure & Network Resilience Simulator**
- Safe simulation on isolated graph deep copies (`MultiGraph.copy()`).
- Excision of closed nodes and all incident multi-edges.
- Connected component decomposition and pairwise reachability loss:
  $$\text{Reachable Pairs} = \sum_{i=1}^k \frac{n_i(n_i - 1)}{2}$$

**Slide 10: Commuter Detour Rerouting**
- Automatic post-closure re-evaluation across all 6 routing algorithms.
- Disruption categorization: `UNCHANGED`, `REROUTED`, `UNREACHABLE`, or `ENDPOINT_CLOSED`.
- Visual red cross marker (`✕`) and red dotted severed track links.

**Slide 11: Live Multi-Algorithm Benchmarking**
- Microbenchmarking across 15 iterations with warmups (`time.perf_counter_ns()`).
- Delhi Metro (260 nodes): BFS median runtime $< 0.8\text{ ms}$; Dijkstra $< 1.1\text{ ms}$; 0-1 BFS $< 2.0\text{ ms}$.
- Brandes Betweenness median runtime $\approx 45\text{ ms}$.

**Slide 12: Streamlit Dashboard Demonstration**
- Overview of the 6 integrated dashboard pages:
  - Page 1: Metro Overview & Line Filtering
  - Page 2: Route Planner & Comparison
  - Page 3: Station Importance & Heatmap
  - Page 4: Closure Simulator & Resilience
  - Page 5: Algorithm Lab & Execution Profiler
  - Page 6: Results & Export Center (CSV/JSON)

**Slide 13: Limitations & Assumptions**
- Schematic station layouts (straight lines represent service links, not physical track curves).
- Fixed commercial speed (35 km/h) and default transfer friction penalty (5.0 min).
- Does not model live signaling delays or passenger crowding.

**Slide 14: Conclusion & Future Scope**
- Successfully demonstrated that graph algorithms provide powerful insights into transit routing and topological resilience.
- Future enhancements: Dynamic timetable scheduling, fare matrix integration, and multi-modal transit expansions.
