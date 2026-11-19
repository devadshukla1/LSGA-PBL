# ACADEMIC PROJECT REPORT

# Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms

**Product Name:** SmartRoute Analytics  
**Course Code / Title:** Large-Scale Graph Analysis (LSGA) — Project-Based Learning (PBL)  
**Academic Session:** 2026–2027  
**Department:** Department of Computer Science & Engineering  
**Institution:** Faculty of Engineering and Technology  

---

## CANDIDATE DECLARATION

I hereby declare that this project report entitled **"Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms"** submitted in partial fulfillment of the requirements for the degree in Computer Science and Engineering is an authentic record of our own work carried out under the guidance of our academic supervisor.

The matter embodied in this report has not been submitted elsewhere for the award of any other degree or diploma. All algorithms, mathematical models, experimental results, and code implementations presented are genuine and verified against the actual software codebase.

**Student Name:** [Candidate Name / Roll Number]  
**Signature:** __________________________  
**Date:** November 2026  

---

## CERTIFICATE OF APPROVAL

This is to certify that the project work entitled **"Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms"** carried out by [Candidate Name] has been examined and approved as satisfying the academic requirements for the subject **Large-Scale Graph Analysis (LSGA PBL)**.

**Project Supervisor:** [Supervisor Name & Title]  
**Department:** Computer Science & Engineering  
**Signature:** __________________________  
**Date:** November 2026  

**Internal Examiner:** ____________________  
**External Examiner:** ____________________  

---

## ACKNOWLEDGEMENTS

I express my sincere gratitude to my project supervisor for providing invaluable academic guidance, constructive critique, and technical direction throughout the design, implementation, and verification of this research project.

I also extend my heartfelt appreciation to the faculty members of the Department of Computer Science and Engineering for providing the computational resources, laboratory facilities, and academic framework necessary to complete this work. Finally, I thank my peers and family for their continuous encouragement and support.

---

## ABSTRACT

Urban emergency response efficiency depends on rapidly identifying optimal transit corridors across dense, directed street networks subject to dynamic traffic congestion, unexpected road closures, and localized structural bottlenecks. Traditional shortest-path routing based purely on physical distance often fails during emergencies because the geographically shortest route may suffer from severe traffic delays or impassable physical blockages.

This project, titled **SmartRoute Analytics**, presents an in-memory graph analytics and optimization platform engineered to evaluate emergency vehicle routing and structural network resilience using large-scale graph algorithms. Urban street networks are mathematically modeled as directed multigraphs $G = (V, E)$ using NetworkX MultiDiGraph structures, preserving intersection coordinates, one-way vehicular restrictions, and parallel edges with unique edge keys.

We implement and evaluate three core shortest-path algorithms: classic Dijkstra's algorithm, goal-directed A* search with an admissible and consistent spherical Haversine heuristic, and Bidirectional Dijkstra with dual min-heap frontiers. For emergency detour planning, Yen's algorithm is implemented to generate $K$-shortest loopless alternative paths. Dynamic traffic is modeled through reproducible, deterministic congestion multiplier tiers (1.0x to 2.5x), while emergency road closures and blocked intersections are evaluated by inducing active subgraphs while maintaining the immutability of the baseline road network.

To assess structural network vulnerability, we compute network centralities (Degree, Betweenness, Closeness, and PageRank) and perform site percolation experiments comparing targeted attacks on high-betweenness hubs against uniform random node failures. Furthermore, we implement and compare Recursive Geographic Bisection and Graph-Aware Region Growing partitioning techniques, coupled with a 3D Earth-Centered Earth-Fixed (ECEF) KD-Tree spatial index that achieves a 25x–52x query acceleration over linear brute-force scanning.

The entire system is integrated into an interactive, dark-themed Streamlit multi-page dashboard that operates 100% offline without external network dependencies. Experimental benchmarking across 96 query iterations verified a 100% path validity and optimality rate, confirming that all three routing algorithms discover identical optimal path costs while A* and Bidirectional Dijkstra reduce the search space by 32.7% and 45.0%, respectively. The codebase is backed by 260 automated Pytest test cases passing with zero failures.

---

## TABLE OF CONTENTS

1. **Chapter 1: Introduction**
   - 1.1 Context and Motivation
   - 1.2 Academic Scope and Syllabus Alignment
   - 1.3 Contributions of the Work
2. **Chapter 2: Problem Statement and Objectives**
   - 2.1 Urban Emergency Routing Challenges
   - 2.2 Formal Problem Formulation
   - 2.3 Research and Implementation Objectives
3. **Chapter 3: System Requirements and Architecture**
   - 3.1 Software Requirements
   - 3.2 Modular System Architecture
   - 3.3 Data Flow and Invariants
4. **Chapter 4: Mathematical Graph Model**
   - 4.1 Directed MultiDiGraph Formulation
   - 4.2 Edge Metrics and Cost Functions
   - 4.3 Admissible Spherical Heuristic Proof
   - 4.4 Spanning Forest Projection
5. **Chapter 5: Routing Algorithm Design & Implementation**
   - 5.1 Manual Dijkstra's Algorithm
   - 5.2 Heuristic-Guided A* Search
   - 5.3 Bidirectional Dijkstra Search
   - 5.4 Yen's K-Shortest Loopless Paths
6. **Chapter 6: Traffic Simulation & Network Resilience**
   - 6.1 Macroscopic Congestion Multipliers
   - 6.2 Incident Handling and Subgraph Induction
   - 6.3 Centrality Metric Analysis
   - 6.4 Percolation Degradation Experiments
7. **Chapter 7: Graph Partitioning & Spatial Indexing**
   - 7.1 Recursive Geographic Bisection
   - 7.2 Graph-Aware Region Growing
   - 7.3 Partition Quality Metrics
   - 7.4 3D ECEF KD-Tree Nearest-Node Lookup
8. **Chapter 8: Experimental Benchmarking & Performance Analysis**
   - 8.1 Experimental Protocol
   - 8.2 Measured Latency and Speedup Results
   - 8.3 Search Space Exploration Reduction
   - 8.4 Memory Profiling Findings
9. **Chapter 9: Quality Assurance & Verification**
   - 9.1 Test Automation Suite (260 Tests)
   - 9.2 Master Verification Protocol
   - 9.3 Invariant and In-Memory Correctness
10. **Chapter 10: Conclusion & Future Scope**
    - 10.1 Concluding Remarks
    - 10.2 Known Architectural Limitations
    - 10.3 Future Research Directions
11. **References**

---

## CHAPTER 1: INTRODUCTION

### 1.1 Context and Motivation
Urban road transport systems form the critical economic and logistical backbone of modern smart cities. In emergency medical services (EMS), disaster response, and fire rescue operations, transit latency is directly correlated with human survivability. However, contemporary metropolitan street networks exhibit high topological complexity, non-uniform link capacities, one-way traffic restrictions, severe peak-hour congestion, and unexpected road blockages caused by accidents or natural hazards.

Finding an optimal path for an emergency response vehicle is fundamentally a graph-theoretic problem. Although algorithms such as Dijkstra's algorithm and A* search are well-established in computer science literature, their empirical performance, memory consumption, heuristic efficacy, and resilience under network disruption require systematic, reproducible evaluation on real-world urban road topologies.

### 1.2 Academic Scope and Syllabus Alignment
This project was developed under the academic curriculum of **Large-Scale Graph Analysis (LSGA PBL)**. It provides end-to-end practical coverage of all five core syllabus modules:
- **Module 1 (Graph Representation):** Directed multigraphs, edge key indexing, adjacency structures, GraphML persistence.
- **Module 2 (Graph Traversal):** BFS hop minimality, DFS cycle back-edges, spherical geodesic distance.
- **Module 3 (Partitioning & Indexing):** Spatial bisection, graph-aware clustering, 3D KD-Tree indexing.
- **Module 4 (Shortest Paths & Routing):** Dijkstra, A*, Bidirectional Dijkstra, Yen's K-shortest paths.
- **Module 5 (Analytics & Resilience):** Centrality rankings, site percolation degradation, statistical benchmarking.

### 1.3 Contributions of the Work
1. **High-Fidelity Representation:** Formulated a directed MultiDiGraph representation that preserves parallel road segments, one-way restrictions, and physical speed limits without structural data loss.
2. **Custom Verified Algorithmic Engines:** Developed independent, project-owned implementations of Dijkstra, A*, Bidirectional Dijkstra, and Yen's K-shortest paths, achieving 100% cost optimality against reference implementations.
3. **Provably Admissible Heuristics:** Established and validated an admissible spherical Haversine travel-time heuristic dividing great-circle distance by the global speed limit $v_{\max}$, guaranteeing optimal path discovery.
4. **Deterministic Simulation & Resilience Framework:** Built an isolated scenario framework evaluating congestion penalties and incident exclusions while guaranteeing original graph immutability.
5. **Spatial Acceleration Engine:** Implemented a 3D ECEF KD-Tree spatial index delivering up to a 52x query speedup over linear brute-force scanning.
6. **Exhaustive Quality Assurance:** Validated the complete system through 260 automated Pytest test cases passing with zero failures.

---

## CHAPTER 2: PROBLEM STATEMENT AND OBJECTIVES

### 2.1 Urban Emergency Routing Challenges
Urban street networks present unique structural challenges that invalidate naive routing assumptions:
- **Distance vs. Time Duality:** The shortest physical path frequently passes through congested residential corridors with lower speed limits, while a longer peripheral bypass may yield a much faster travel time.
- **One-Way Asymmetry:** Street directions prohibit arbitrary reversals; $u \to v$ does not imply $v \to u$.
- **Parallel Road Links:** Dual carriageways, service roads, and flyovers connect the same intersection pairs with differing capacities.
- **Localized Disruptions:** Road incidents create impassable blockages that require immediate real-time diversion.

### 2.2 Formal Problem Formulation
Let an urban road network be represented as a directed weighted multigraph $G = (V, E)$, where $V$ is the set of intersections and $E$ is the set of directed road segments $e = (u, v, k)$. Given an emergency origin $v_s \in V$ and destination $v_t \in V$, the objective is to find a simple path $P^* = (v_0, e_0, v_1, \dots, v_m)$ with $v_0 = v_s$ and $v_m = v_t$ that minimizes:

$$\min_{P} \sum_{i=0}^{m-1} T_s(v_i, v_{i+1}, k_i) \quad \text{s.t. } e_i \notin E_{\text{closed}} \land v_i \notin V_{\text{blocked}}$$

where $T_s(e)$ is the scenario-adjusted travel time.

### 2.3 Research and Implementation Objectives
1. Implement and verify exact shortest-path and alternative routing algorithms on directed multigraphs.
2. Quantify empirical speedup, explored vertex reduction, and memory usage across graph scales.
3. Develop deterministic traffic simulation models that preserve base graph immutability.
4. Measure network degradation curves under targeted hub attacks versus random failures.
5. Provide a responsive, multi-page Streamlit web dashboard operating 100% offline.

---

## CHAPTER 3: SYSTEM REQUIREMENTS AND ARCHITECTURE

### 3.1 Software Requirements
- **Operating System:** Microsoft Windows 10 / 11 (64-bit)
- **Runtime Environment:** Python 3.11.x (>=3.11, <3.13)
- **Key Libraries:** `networkx>=3.2`, `osmnx>=1.9.0`, `streamlit>=1.32.0`, `pydeck>=0.8.0`, `scipy>=1.12.0`, `pytest>=8.0.0`, `ruff>=0.3.0`

### 3.2 Modular System Architecture
SmartRoute Analytics follows a 4-tier modular architecture:
1. **Presentation Layer:** Multi-page Streamlit application (`app.py` and 7 studio pages in `pages/`) utilizing PyDeck WebGL mapping and interactive Altair charting.
2. **Service Layer:** Application services managing in-memory datasets (`DatasetService`), routing coordination (`RoutingService`), simulation scenarios (`SimulationEngine`), and benchmarking (`BenchmarkRunner`).
3. **Core Algorithm Layer:** Custom Python implementations of graph traversal, single-source and bidirectional shortest paths, Yen's alternative paths, spatial KD-Trees, and resilience evaluators.
4. **Data & Storage Layer:** OpenStreetMap ingestion via OSMnx, GraphML serialization/caching, synthetic grid generators, and CSV/JSON export handlers.

### 3.3 Data Flow and Invariants
All data operations respect strict system invariants:
- **Graph Immutability:** Loaded road networks in `data/cache/` are never overwritten or mutated by simulation runs.
- **Deterministic Seeding:** Random number generators are explicitly seeded (`seed=42`).
- **Memory Containment:** Graph structures are maintained in-memory for microsecond-scale execution without external database overhead.

---

## CHAPTER 4: MATHEMATICAL GRAPH MODEL

*(See full mathematical derivations in [mathematical_model.md](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/docs/mathematical_model.md))*

- **Graph Structure:** $G = (V, E)$, with directed edge $e = (u, v, k) \in V \times V \times \mathbb{N}_0$.
- **Edge Travel Time:** $T(e) = \frac{L(e) \cdot 3.6}{S(e)}$ seconds.
- **Congestion Multiplier:** $T_s(e) = T(e) \cdot (1 + C_s(e))$, where $C_s(e) \in \{0.0, 0.2, 0.5, 1.0, 1.5\}$.
- **Admissible Travel Time Heuristic:**
  $$h(u) = \frac{D_{\text{hav}}(u, v_t)}{v_{\max}}$$
  where $D_{\text{hav}}$ is the Haversine great-circle distance and $v_{\max} = 33.333\text{ m/s}$ (120 km/h). Because no road segment allows speeds exceeding $v_{\max}$, $h(u) \le T^*(u, v_t)$ is strictly guaranteed.
- **Spanning Forest Invariant:** For an undirected projection with $C$ connected components, $|E_{\text{MSF}}| = |V| - C$.

---

## CHAPTER 5: ROUTING ALGORITHM DESIGN & IMPLEMENTATION

*(See algorithm mechanics and pseudocode in [algorithms_explained.md](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/docs/algorithms_explained.md))*

1. **Dijkstra's Algorithm:** Uses a binary min-heap (`heapq`) to maintain tentative distance labels, relaxing outgoing directed edges $(u, v, k)$ until the target node is settled. Complexity: $O((|E| + |V|) \log |V|)$.
2. **A* Search:** Guides frontier expansion using the priority key $f(u) = g(u) + h(u)$. Heuristic consistency ensures vertices are settled at most once and the first settlement of $v_t$ is optimal.
3. **Bidirectional Dijkstra:** Advances two concurrent frontiers (forward from $s$, backward from $t$ on $G^{\text{rev}}$). Terminates when $\min(d_f) + \min(d_b) \ge \mu$, where $\mu$ is the best complete path cost found.
4. **Yen's K-Shortest Paths:** Computes $K$ loopless alternative paths by systematically deviating from root subpaths at spur nodes with temporary edge/node exclusions, preserving parallel road links.

---

## CHAPTER 6: TRAFFIC SIMULATION & NETWORK RESILIENCE

### 6.1 Congestion Modeling
Congestion is simulated deterministically across 5 discrete tiers:
- Free-Flow (1.0x), Light (1.2x), Moderate (1.5x), Heavy (2.0x), Severe (2.5x).
Edges are selected based on configurable coverage fractions using a fixed random seed.

### 6.2 Centrality Metrics & Critical Intersections
- **Betweenness Centrality:** Identifies bridge intersections that appear on disproportionately large numbers of shortest paths.
- **Degree & Closeness:** Measure local connectivity density and global reachability.
- **PageRank:** Evaluates stationary transit convergence along directed roads.

### 6.3 Site Percolation Resilience Findings
Percolation experiments on urban networks demonstrated:
- **Targeted Hub Attack:** Removing the top 15%–20% of high-betweenness intersections causes catastrophic fragmentation of the giant strongly connected component ($|V_{\text{giant}}| / |V| \to 0$).
- **Random Failure:** Uniform random node removal preserves the giant component ($>60\%$ connectivity retained) even at 40% node failure.

---

## CHAPTER 7: GRAPH PARTITIONING & SPATIAL INDEXING

### 7.1 Partitioning Techniques
- **Recursive Geographic Bisection:** Slices spatial bounding boxes along alternating latitude/longitude coordinate medians.
- **Graph-Aware Region Growing:** Expands synchronized BFS frontiers from $K$ geographically dispersed seed nodes, respecting topological road connectivity.
- **Finding:** Graph-aware partitioning consistently achieves lower cut-edge ratios ($\approx 0.35$ vs. $0.48$) while maintaining balance ratios near $1.0$.

### 7.2 3D ECEF KD-Tree Spatial Indexing
- Geodetic coordinates $(\phi, \lambda)$ are converted to 3D Cartesian coordinates $(X, Y, Z)$ on Earth's sphere:
  $$X = R \cos \phi \cos \lambda, \quad Y = R \cos \phi \sin \lambda, \quad Z = R \sin \phi$$
- A `scipy.spatial.cKDTree` enables nearest-intersection queries in $O(\log |V|)$ time.
- **Empirical Speedup:** Achieves a **25x–52x speedup** over $O(V)$ linear brute-force scanning on urban road networks.

---

## CHAPTER 8: EXPERIMENTAL BENCHMARKING & PERFORMANCE ANALYSIS

*(See measured numerical tables in [experimental_results.md](file:///c:/Users/devad/OneDrive/Desktop/LSGA%20PBL/docs/experimental_results.md))*

- **Optimality & Validity Rate:** Across all 96 evaluated query iterations, 100% of routes were valid and optimal, achieving exact cost equality:
  $$C_{\text{Dijkstra}} \equiv C_{\text{A*}} \equiv C_{\text{BiDijkstra}} \equiv C_{\text{NetworkX}}$$
- **Search Space Reduction:**
  - Dijkstra expanded an average of **7.06 nodes** on the 16-node network.
  - A* expanded an average of **4.75 nodes** (**32.7% search space reduction**).
  - Bidirectional Dijkstra expanded an average of **3.88 nodes** (**45.0% search space reduction**).
- **Runtime Dynamics:**
  - On small graphs ($N \le 16$), Dijkstra had the lowest mean runtime (**0.137 ms**) due to the absence of trigonometric heuristic overhead.
  - On medium-to-large graphs ($N \ge 100$), search space pruning dominates, allowing A* to achieve up to a **2.5x speedup** over Dijkstra.
- **Peak Memory Delta:** Bidirectional Dijkstra utilized the lowest peak RAM (**0.0046 MB**) by maintaining smaller active frontier heaps.

---

## CHAPTER 9: QUALITY ASSURANCE & VERIFICATION

- **Automated Test Coverage:** 260 Pytest tests passing with 100% pass rate in 14.2 seconds.
- **Master Phase Verification:** `python scripts/verify_all.py` confirms all 9 phase test harnesses pass.
- **Demonstration Script:** `python scripts/verify_demo.py` verifies the complete 20-step viva demonstration pipeline.
- **Static Code Hygiene:** `ruff check .` confirms 0 lint errors across all 177 repository files.

---

## CHAPTER 10: CONCLUSION & FUTURE SCOPE

### 10.1 Concluding Remarks
The SmartRoute Analytics project successfully demonstrates how advanced graph algorithms, rigorous mathematical modeling, and spatial data structures can be integrated to analyze urban emergency vehicle routing and network resilience. All academic syllabus requirements across Modules 1–5 have been fully implemented, verified, and integrated into a professional Streamlit dashboard.

### 10.2 Known Architectural Limitations
1. Static snapshot edge weights (no time-dependent dynamic flows).
2. Macroscopic static congestion multipliers (no microscopic car-following physics).
3. Single-node in-memory architecture (bounded to metropolitan graphs $V \le 10^5$).

### 10.3 Future Research Directions
- Contraction Hierarchies (CH) for millisecond routing on continental graphs.
- Microscopic co-simulation with SUMO for emergency siren preemption modeling.
- Live traffic IoT sensor ingestion and mobile driver navigation interfaces.

---

## REFERENCES

1. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.
2. Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1(1), 269–271.
3. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2), 100–107.
4. Yen, J. Y. (1971). Finding the K shortest loopless paths in a network. *Management Science*, 17(11), 712–716.
5. Brandes, U. (2001). A faster algorithm for betweenness centrality. *Journal of Mathematical Sociology*, 25(2), 163–177.
6. Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139.
7. Tarjan, R. (1972). Depth-first search and linear graph algorithms. *SIAM Journal on Computing*, 1(2), 146–160.
8. Callaway, D. S., Newman, M. E., Strogatz, S. H., & Watts, D. J. (2000). Network robustness and fragility: Percolation on random graphs. *Physical Review Letters*, 85(25), 5468.
