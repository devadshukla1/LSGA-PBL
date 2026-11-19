# Live Demonstration Walkthrough Guide

**Product:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Target Duration:** 10–12 Minutes  
**Audience:** College Evaluation Committee / External Viva Examiners  
**Operating Mode:** 100% Offline (Zero Internet Reliance)  

---

## 1. Demonstration Sequence & Timing Matrix

| Step | Page / Component | Key Action & Algorithm | What to Demonstrate & Explain | Duration | Fallback Action if Issue Occurs |
|---|---|---|---|---|---|
| **1. Intro & Architecture** | `app.py` | System Architecture | Academic scope, MultiDiGraph model, offline reproducibility | 1.0 min | Refresh browser (`F5`); app restarts in <2s |
| **2. Road Network Overview** | `1_Network_Overview.py` | Graph Representation | 16-node grid vs. Chandigarh Core; nodes, directed edges, density | 1.5 min | Switch back to "Offline Sample (4x4 Grid)" |
| **3. Traversal Lab** | `2_Traversal_Lab.py` | BFS vs. DFS | Queue layer expansion vs. stack back-edge cycles | 1.0 min | Reset start node to `0` |
| **4. Shortest Path Routing** | `3_Route_Optimizer.py` | Dijkstra vs. A* vs. BiDijkstra | Cost equivalence, explored node reduction, Haversine admissibility | 2.0 min | Use verified endpoints: Source `0`, Target `15` |
| **5. Alternative Paths** | `3_Route_Optimizer.py` | Yen's K-Shortest Paths | $K=3$ loopless detours, non-decreasing travel times, parallel roads | 1.0 min | Lower $K$ to `2` |
| **6. Traffic Simulation** | `4_Traffic_Simulation.py` | Deterministic Congestion | Severity tiers (1.0x to 2.5x), travel time inflation, route diversion | 1.5 min | Ensure seed is locked to `42` |
| **7. Emergency Rerouting** | `4_Traffic_Simulation.py` | Road Closures & Incidents | Closed links excluded; graph immutability; instant emergency detour | 1.5 min | Click "Restore Baseline" and re-apply |
| **8. Analytics & Resilience** | `5_Analytics_Studio.py` | Centralities & Percolation | Betweenness hubs vs. random percolation degradation curve | 1.5 min | Limit centrality to Degree/Betweenness |
| **9. Partitioning & KD-Tree** | `6_Partitioning_Lab.py` | Geographic/Aware & KD-Tree | Cut-edges, balance ratio; KD-tree vs. $O(V)$ brute-force query | 1.0 min | Select partition count $K=4$ |
| **10. Benchmarking & Exports**| `7_Benchmarking_Suite.py` | Automated Benchmark Suite | 100% optimality check, Pareto runtime vs. memory, download CSV/JSON | 1.0 min | Click "Load Latest Run" instead of re-running |

---

## 2. Step-by-Step Viva Presentation Script

### Step 1: System Launch & Architecture Overview (1:00)
- **Action:** Open browser at `http://localhost:8501`.
- **Spoken Points:**
  > *"Good morning respected examiners. I present **SmartRoute Analytics**, an academic platform designed to evaluate emergency vehicle routing and structural network resilience using large-scale graph algorithms. The system represents urban road topologies as directed NetworkX MultiDiGraphs with parallel edge keys, running 100% offline with zero cloud dependencies."*

### Step 2: Road Network Representation (1:30)
- **Action:** Navigate to **`1_Network_Overview.py`**. Select **"Offline Sample (4x4 Grid)"**.
- **Spoken Points:**
  > *"Here we examine the network topology: 16 intersections and 34 directed road segments. Notice that every edge maintains length in meters, legal speed in km/h, and free-flow travel time. The interactive PyDeck map renders spatial coordinates and one-way directional vectors."*

### Step 3: Graph Traversal & Cycle Detection (1:00)
- **Action:** Navigate to **`2_Traversal_Lab.py`**. Set Source Node = `0`. Run BFS, then DFS.
- **Spoken Points:**
  > *"In the Traversal Lab, we validate fundamental graph exploration. BFS advances through concentric topological frontiers to produce the minimum-hop tree. DFS explores branch depth and detects directed cycles by identifying back-edges."*

### Step 4: Shortest-Path Routing & Heuristic Admissibility (2:00)
- **Action:** Navigate to **`3_Route_Optimizer.py`**. Set Source = `0`, Target = `15`, Objective = `travel_time`. Click **"Run Comparison"**.
- **Spoken Points:**
  > *"This is the core routing engine. We compare manual Dijkstra, manual A*, and manual Bidirectional Dijkstra. Notice in the summary table: all three algorithms discover the exact same optimal travel time of 57.17 seconds. However, while Dijkstra expanded 12 nodes, A* used our admissible spherical Haversine heuristic to expand only 8 nodes—a 33% reduction in search space."*

### Step 5: Yen's Alternative Routes (1:00)
- **Action:** In **`3_Route_Optimizer.py`**, enable **"K-Shortest Routes"** with $K=3$.
- **Spoken Points:**
  > *"In emergency logistics, primary roads may experience localized blockages. Using Yen's algorithm, we generate the top 3 loopless alternative routes. The paths are monotonically sorted by cost, and parallel road links are properly preserved."*

### Step 6: Traffic Congestion Simulation (1:30)
- **Action:** Navigate to **`4_Traffic_Simulation.py`**. Select Severity = **Heavy (2.0x)**, Coverage = **30%**, Seed = **42**. Apply Congestion.
- **Spoken Points:**
  > *"In the Traffic Simulator, we inject reproducible congestion multipliers. Notice that travel time along congested arteries doubles. When we recompute the route, the vehicle automatically diverts to secondary roads where free-flow speeds offer a faster overall journey."*

### Step 7: Incident Closures & Emergency Rerouting (1:30)
- **Action:** In **`4_Traffic_Simulation.py`**, close edge `(0, 1)` or block intersection `1`. Recompute Emergency Route.
- **Spoken Points:**
  > *"When an intersection is blocked by an active incident, the edge is completely excised from the active routing subgraph. The base GraphML graph remains completely immutable. The emergency rerouting engine immediately identifies an alternate corridor."*

### Step 8: Network Analytics & Resilience Percolation (1:30)
- **Action:** Navigate to **`5_Analytics_Studio.py`**. View Centrality Rankings and click **"Run Percolation Experiment"**.
- **Spoken Points:**
  > *"Here we identify structurally critical intersections. High betweenness centrality highlights key bridge junctions like Node 5. In our percolation resilience experiment, targeted removal of these top hubs causes the giant component to rapidly collapse with under 20% node loss, while random failures preserve connectivity up to 40%+ loss."*

### Step 9: Graph Partitioning & Spatial KD-Tree Indexing (1:00)
- **Action:** Navigate to **`6_Partitioning_Lab.py`**. Set $K=4$. Compare Geographic vs. Graph-Aware cuts. Query nearest node.
- **Spoken Points:**
  > *"For large-scale distributed architectures, we implement Recursive Geographic Bisection and Graph-Aware Region Growing. Graph-aware partitioning achieves lower cut-edge ratios by respecting road corridors. For spatial coordinate queries, our 3D ECEF KD-Tree delivers a 25x–52x query speedup over linear $O(V)$ brute-force scanning."*

### Step 10: Benchmark Suite & Artifact Export (1:00)
- **Action:** Navigate to **`7_Benchmarking_Suite.py`**. View performance charts and click **"Download Benchmark Summary (CSV)"**.
- **Spoken Points:**
  > *"Finally, the Benchmarking Suite provides statistically rigorous evaluation with warmup runs and memory profiling. In 100% of trials, routing correctness and optimality match NetworkX ground truth. All data can be downloaded as CSV reports and JSON reproducibility manifests. Thank you, I am ready for questions."*
