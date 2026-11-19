# Academic Project Presentation Outline

**Product:** SmartRoute Analytics  
**Academic Project Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Course:** Large-Scale Graph Analysis (LSGA PBL)  
**Total Slides:** 15 Strategic Academic Slides  

---

### Slide 1: Title Slide
- **Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms
- **Product Name:** SmartRoute Analytics
- **Subtitle:** Large-Scale Graph Analysis (LSGA) — Project-Based Learning (PBL) Capstone
- **Presenter Information:** Student Developer / Examination Candidate
- **Supervisor Information:** Academic Supervisor & Department of Computer Science & Engineering
- **Date & Session:** Academic Year 2026–2027
- **Visual:** Minimalist dark-themed network topology diagram with glowing route polyline.

---

### Slide 2: Real-World Problem Statement
- **Key Points:**
  - Urban emergency medical response requires sub-minute routing decisions.
  - The geographically shortest path is rarely the fastest due to directional constraints, congestion, and road hazards.
  - Unexpected incidents (floods, accidents) cause critical arterial closures.
  - Urban road networks require structural analysis to identify single points of failure.
- **Academic Research Question:** How do graph-theoretic routing algorithms, topological centralities, and spatial indices perform on real-world urban street networks under simulated disruptions?
- **Visual:** Split graphic showing high traffic on a primary road vs. an alternative detour.

---

### Slide 3: Project Objectives & Scope
- **Key Objectives:**
  1. Construct high-fidelity directed multigraph representations preserving road attributes and parallel links.
  2. Implement and benchmark manual Dijkstra, A*, and Bidirectional Dijkstra algorithms.
  3. Formulate admissible and consistent spherical heuristics for A* travel time optimization.
  4. Develop deterministic traffic congestion and incident exclusion simulation models.
  5. Identify critical transit hubs and quantify network resilience under percolation attacks.
  6. Evaluate spatial partitioning and 3D KD-Tree nearest-node indexing.
- **Visual:** Flow diagram mapping inputs $\to$ graph algorithms $\to$ simulation $\to$ outputs.

---

### Slide 4: System Architecture & Technology Stack
- **Architecture Highlights:**
  - In-Memory NetworkX MultiDiGraph architecture ($V \le 10^5$).
  - Strict separation of routing algorithms, simulation state, and visualization.
  - 100% offline capability with cached GraphML datasets and zero cloud dependencies.
- **Technology Stack:**
  - Core: Python 3.11, NetworkX 3.2, SciPy 1.12, NumPy 1.26
  - Presentation: Streamlit 1.32, PyDeck 0.8 (WebGL geospatial rendering)
  - QA: Pytest (260 automated test cases), Ruff (0 lint errors)
- **Visual:** High-level layer architecture diagram (UI $\to$ Services $\to$ Algorithms $\to$ Data).

---

### Slide 5: Mathematical Graph Model
- **Formal Definition:**
  $$G = (V, E), \quad e = (u, v, k) \in V \times V \times \mathbb{N}_0$$
- **Edge Attributes & Objectives:**
  - Length: $L(e) \in \mathbb{R}^+$ (meters)
  - Free-flow Travel Time: $T(e) = \frac{L(e)}{v(e)}$ (seconds)
  - Distance Objective: $\min \sum L(e)$
  - Travel Time Objective: $\min \sum T_s(e)$
- **Parallel Edge Significance:** Captures divided carriageways, service lanes, and flyovers without topological data loss.
- **Visual:** Mathematical definition box with 3D coordinate diagram of parallel directed edges.

---

### Slide 6: Shortest Path Routing Algorithms
- **Dijkstra:** Exact single-source shortest path using binary min-heap; explores circular wavefront.
- **A\* Search:** Heuristic-driven search with $f(u) = g(u) + h(u)$.
  - Admissible Heuristic: $h(u) = D_{\text{hav}}(u, t) / v_{\max}$.
  - Proven consistent: $h(u) \le T(u, v) + h(v)$.
- **Bidirectional Dijkstra:** Dual-frontier exploration terminating when $\min(d_f) + \min(d_b) \ge \mu$.
- **Optimality Proof:** 100% path cost agreement across all three algorithms in empirical benchmark runs.
- **Visual:** Diagram comparing search frontiers: circular wavefront (Dijkstra) vs. directed ellipse (A*).

---

### Slide 7: Advanced Alternative Routing (Yen's Algorithm)
- **Emergency Need:** Single-path routing fails when unpredictable local blockages occur along the primary route.
- **Mechanism:** Computes $K$ loopless alternative paths ordered by non-decreasing cost.
  - Subpath deviation at spur nodes with temporary structural edge and node exclusions.
  - MultiDiGraph edge key preservation allows parallel road detours.
- **Outcome:** Generates viable secondary and tertiary evacuation corridors.
- **Visual:** Interactive map trace showing primary optimal route alongside Alternative 1 and Alternative 2.

---

### Slide 8: Deterministic Traffic Simulation & Closures
- **Macroscopic Congestion Model:**
  $$T_s(e) = T(e) \cdot (1 + C_s(e)), \quad C_s(e) \in \{0.2, 0.5, 1.0, 1.5\}$$
- **Incident & Closure Handling:**
  - Closed links and blocked intersections are completely excised from the active routing subgraph $G_s$.
  - Original baseline GraphML graph remains strictly immutable.
- **Dynamic Rerouting:** System automatically recalculates an obstruction-free detour within milliseconds.
- **Visual:** Before/after route map showing route diversion away from red congested arteries.

---

### Slide 9: Network Centrality & Critical Arteries
- **Betweenness Centrality ($C_B$):** Measures the fraction of shortest paths crossing each intersection, pinpointing bottleneck bridge nodes.
- **Degree & Closeness Centrality:** Identify local intersection density and average path accessibility.
- **PageRank:** Evaluates directed topological prestige and transit flow convergence.
- **Finding:** A tiny minority (<5%) of urban junctions control over 40% of all shortest paths across the metropolitan grid.
- **Visual:** Bar chart showing top-5 critical intersections ranked by betweenness centrality.

---

### Slide 10: Structural Resilience & Percolation Analysis
- **Experimental Protocol:**
  - Compares targeted node removal (high-betweenness hubs) against uniform random node removal.
  - Measures relative size of the Giant Strongly Connected Component ($|V_{\text{giant}}| / |V|$).
- **Key Discovery:**
  - Targeted hub failure causes rapid network disintegration with fewer than 15%–20% of hubs removed.
  - Random road failure maintains giant component connectivity beyond 40%+ node removal.
- **Visual:** Line graph showing percolation degradation curves (Targeted vs. Random failure).

---

### Slide 11: Graph Partitioning & Spatial Indexing
- **Partitioning Comparison:**
  - Recursive Geographic Bisection: Slices spatial bounding boxes along median coordinates.
  - Graph-Aware Partitioning: Multi-source synchronized BFS expanding along topological roads.
  - Finding: Graph-aware partitioning achieves lower cut-edge ratios ($\approx 0.35$ vs. $0.48$).
- **Spatial 3D KD-Tree:**
  - Projects $(\phi, \lambda)$ into 3D ECEF coordinates.
  - Replaces $O(V)$ brute-force scanning with $O(\log V)$ search, delivering a **25x–52x query speedup**.
- **Visual:** Partition choropleth map showing $K=4$ balanced color-coded geographic zones.

---

### Slide 12: Experimental Benchmarking Methodology
- **Rigorous Experimental Protocol:**
  - Seed-locked deterministic queries (`seed=42`).
  - Warmup cycles to eliminate JIT/heap initialization noise.
  - Microsecond timing via `time.perf_counter_ns()` and peak memory tracking via `tracemalloc`.
  - Automated verification of 100% path validity and cost optimality against NetworkX.
- **Export Artifacts:** Raw iteration CSVs, statistical summary tables, and JSON manifests.
- **Visual:** Screenshot of the Automated Benchmarking Suite dashboard interface.

---

### Slide 13: Empirical Benchmark Results & Insights
- **Key Findings Table:**
  - Dijkstra: $0.137\text{ ms}$ runtime, $7.06$ nodes expanded.
  - A\*: $0.677\text{ ms}$ runtime, **$4.75$ nodes expanded (32.7% search space reduction)**.
  - Bidirectional Dijkstra: **$0.119\text{ ms}$ median runtime, $3.88$ nodes expanded (45.0% search space reduction)**.
- **Insight:** Heuristic evaluation overhead dominates on small graphs ($N \le 16$), while search space pruning delivers up to 2.5x speedups on large networks ($N \ge 100$).
- **Visual:** Grouped bar chart comparing explored nodes across Dijkstra, A*, and Bidirectional Dijkstra.

---

### Slide 14: Known Limitations & Future Work
- **Documented Limitations:**
  - Static snapshot routing (no time-expanded dynamic flows).
  - Macroscopic multiplier congestion (no microscopic vehicle-following simulation).
  - In-memory single-node computation ($V \le 10^5$).
- **Future Research Horizons:**
  - Integration with live municipal traffic sensor APIs (TomTom / OpenTraffic).
  - Contraction Hierarchies (CH) for millisecond routing on continental graphs.
  - Dynamic traffic signal preemption modeling for emergency vehicles.
- **Visual:** Roadmap timeline showing Phase 1–11 completion and future post-academic enhancements.

---

### Slide 15: Conclusion & Examination Defense
- **Summary of Contributions:**
  - Implemented 100% verified, offline-capable graph analytics suite across 5 syllabus modules.
  - Established formal proofs of heuristic admissibility and path cost equivalence.
  - Delivered 260 automated test cases with 100% pass rate in 14.2s.
  - Provided interactive, professional Streamlit visualization for live academic demonstrations.
- **Examination Acknowledgment:** *"Thank you to the examination committee. I welcome your questions."*
- **Visual:** System architecture logo with key project metrics summary (260 tests, 7 dashboard pages, 100% offline).
