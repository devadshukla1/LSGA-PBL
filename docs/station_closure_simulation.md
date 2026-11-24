# Station Closure & Metro Network Resilience Simulation (Phase 6)

## 1. Problem Formulation & Scope Boundaries
Transit disruptions (maintenance closures, flood incidents, signaling breakdowns) remove stations and their associated track connections. Measuring network degradation and identifying detour availability requires isolated topological simulation.

**Academic Disclaimers**:
- This simulator models **structural topological connectivity and shortest-path rerouting**.
- It does **not** predict train schedules, railway signaling constraints, live crowd densities, official DMRC advisory delays, or passenger platform crowding.
- Operates entirely offline without external map tiles or OpenStreetMap.

---

## 2. Graph Node Removal & Isolation Architecture

### A. Non-Mutating Isolation Model (`src/simulation/closure_engine.py`)
- When a user selects a set of closed stations $\{v_c\}$, an isolated deep copy of the transit `MultiGraph` is instantiated:
  $$G_{\text{sim}} = G.\text{copy}()$$
- The selected stations and all their incident multi-edges are removed:
  $$G_{\text{sim}}.\text{remove\_nodes\_from}(\{v_c\})$$
- **Memory Footprint**: A full copy of the 260-node, 273-edge MultiGraph consumes $\approx 100\text{ KB}$, ensuring high performance, zero state leakage, and absolute thread-safety.
- The baseline graph $G$ remains permanently unmutated.

---

## 3. Connectivity & Reachability Formulation (`src/simulation/connectivity_impact.py`)

### A. Connected Component Decomposition
Using BFS/DFS component exploration, remaining nodes are partitioned into disjoint components:
$$\mathcal{C} = \{C_1, C_2, \dots, C_k\}, \quad \text{where } |C_i| = n_i$$

### B. Pairwise Reachability Metrics
For an undirected network, two stations can reach each other if and only if they belong to the same connected component.
$$\text{Reachable Station Pairs} = \sum_{i=1}^k \frac{n_i (n_i - 1)}{2}$$

For $N_{\text{remaining}}$ total operational stations, the total theoretical possible pairs is:
$$\text{Possible Station Pairs} = \frac{N_{\text{remaining}} (N_{\text{remaining}} - 1)}{2}$$

$$\text{Reachability Ratio} = \frac{\text{Reachable Station Pairs}}{\text{Possible Station Pairs}}$$
*(Defined as 1.0 for $N_{\text{remaining}} = 1$ and 0.0 for $N_{\text{remaining}} = 0$).*

---

## 4. Automatic Route Recalculation & Disruption Classification (`src/simulation/route_rerouting.py`)

Routing queries between origin $S$ and destination $D$ are evaluated on both $G$ and $G_{\text{sim}}$ across all 6 objectives (BFS, Dijkstra Time, Dijkstra Distance, 0-1 BFS Transfers, Lexicographic, and Transfer-Aware).

### Disruption Taxonomies:
1. `ENDPOINT_CLOSED`: Origin or destination station itself is among the closed stations.
2. `ALREADY_UNREACHABLE`: No baseline route existed between endpoints prior to closure.
3. `UNREACHABLE`: A baseline route existed, but station closures completely severed all surviving network paths.
4. `UNCHANGED`: Baseline route did not pass through any closed station and remains the exact optimal route.
5. `REROUTED`: The baseline route was severed, but an alternative detour path was successfully computed.

---

## 5. Critical Station Vulnerability Impact (`src/simulation/critical_station_impact.py`)
Evaluates the isolated vulnerability impact of removing each station:
- $\Delta \mathcal{C} = \mathcal{C}_{\text{post}} - \mathcal{C}_{\text{base}}$: Component increase (cut-vertex impact).
- $\Delta \text{Pairs}$: Loss of pairwise reachability across the network.
- $\Delta \text{Core}$: Largest component shrinkage.

---

## 6. Algorithmic Complexity

| Operation | Implementation | Time Complexity | Space Complexity |
|---|---|---|---|
| Graph Copy & Node Removal | `MultiGraph.copy()` + `remove_nodes_from()` | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ |
| Connected Components | BFS/DFS traversal | $\mathcal{O}(V_{\text{rem}} + E_{\text{rem}})$ | $\mathcal{O}(V_{\text{rem}})$ |
| Reachable Pair Aggregation | Combinatorial sum over components | $\mathcal{O}(|\mathcal{C}|)$ | $\mathcal{O}(1)$ |
| Detour Rerouting | Dijkstra / 0-1 BFS on $G_{\text{sim}}$ | $\mathcal{O}(L \cdot (V_{\text{rem}} + E_{\text{rem}}) \log(L \cdot V_{\text{rem}}))$ | $\mathcal{O}(L \cdot V_{\text{rem}})$ |
| All-Station Impact Sweep | $V$ isolated single-station simulations | $\mathcal{O}(V \cdot (V + E))$ | $\mathcal{O}(V + E)$ |

---

## 7. Streamlit Dashboard & Visualizations (`pages/4_Closure_Simulator.py`)
1. **Scenario Controls**: Multiselect station picker, scenario descriptions, run and reset actions.
2. **Network Impact Cards**: Real-time display of closed nodes, active nodes, component changes, and reachability ratios.
3. **Before-and-After Metric Table**: Metric changes with clear interpretation descriptions.
4. **Detour Rerouting Section**: Automated origin-to-destination route recalculation reporting stop, time, and transfer deltas.
5. **Interactive Disruption Map**: Plotly visualizer displaying severed links as dotted crimson tracks, active links as grey tracks, active stations as blue dots, and closed stations as prominent red crosses (`✕`).
6. **Exports**: Full CSV metric table download and structured JSON diagnostic payload export.
