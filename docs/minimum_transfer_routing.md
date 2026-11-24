# Minimum-Transfer Optimization & Line-Aware Routing (Phase 4)

## 1. Overview & Theoretical Principles

In passenger transit networks, physical distance and pure station stop counts do not fully account for passenger friction. Transfers between different lines introduce walking time between platforms, waiting times for the next train, and general cognitive fatigue.

MetroGraph Analytics Phase 4 introduces **Line-Aware State Space Modeling**:
Instead of searching on station nodes $V$ alone, the routing graph state is expanded to:
$$S = (v, \ell)$$
where $v \in V$ is the current station node, and $\ell \in \mathcal{L} \cup \{\text{None}\}$ is the active metro line on which the passenger arrived at station $v$.

### First Boarding Rule
At the origin station $v_{\text{source}}$, the initial state is:
$$S_0 = (v_{\text{source}}, \text{None})$$
Boarding the first metro line edge $(v_{\text{source}}, u, \ell)$ incurs **0 transfers** and **0 transfer penalty**.

### Transfer Invariant
When traversing an edge from $(u, \ell_u)$ to $(v, \ell_v)$ along a multi-edge with line $\ell_v$:
- If $\ell_u = \text{None}$ or $\ell_u = \ell_v$, transfer count $\Delta T = 0$, transfer penalty $\Delta P = 0$.
- If $\ell_u \neq \text{None}$ and $\ell_u \neq \ell_v$, transfer count $\Delta T = 1$, transfer penalty $\Delta P = \text{transfer\_penalty\_min}$.

---

## 2. Algorithms Implemented

### A. 0-1 Breadth-First Search (Pure Minimum Transfers)
- **Module**: `src/algorithms/minimum_transfers.py` -> `find_route_minimum_transfers`
- **Mechanism**: Utilizes `collections.deque`.
  - Zero-cost transitions ($\ell_u = \ell_v$) are pushed to the front (`appendleft`).
  - Unit-cost transitions ($\ell_u \neq \ell_v$) are pushed to the back (`append`).
- **Tie-Breaking**: Tracks `(transfers, hops)` so that among equal transfer paths, the path with the fewest physical stations is selected.
- **Complexity**: Time $\mathcal{O}(L \cdot (|V| + |E|))$, Space $\mathcal{O}(L \cdot |V|)$.

### B. Lexicographic Dijkstra (Min Transfers, then Shortest Travel Time)
- **Module**: `src/algorithms/minimum_transfers.py` -> `find_route_min_transfers_then_fastest`
- **Cost Vector**: $(T, \tau, h)$ where:
  - $T$: Total line transfers (integer).
  - $\tau$: Cumulative in-transit travel time in minutes (float).
  - $h$: Station hops (integer).
- **Behavior**: Strictly guarantees the absolute fewest transfers, resolving any ties by fastest travel time.

### C. Transfer-Penalty-Aware Dijkstra (Fastest with Transfer Friction)
- **Module**: `src/algorithms/transfer_aware_dijkstra.py` -> `find_route_transfer_aware_dijkstra`
- **Objective Function**:
  $$\text{Modeled Journey Time} = \sum_{e \in E_{\text{path}}} t_e + (T_{\text{route}} \times P_{\text{transfer}})$$
- **Parameter**: $P_{\text{transfer}} \in [0.0, 15.0]$ minutes (default: 5.0 min).
- **Trade-off Dynamics**: Enables modeling realistic commuter choices (e.g., choosing a slightly longer single-line ride over a fast 2-transfer path when transfer penalty is high).

---

## 3. Human-Readable Transfer Instructions
- **Module**: `src/algorithms/transfer_utils.py` -> `build_transfer_instructions`
- Generates natural, step-by-step passenger guidance:
  1. Boarding instruction at origin with starting line and station.
  2. Intermediate transfer instructions at interchange stations specifying which line to disembark and which line to board.
  3. Final destination arrival notice with exact stops and distances.

---

## 4. Multi-Objective Comparison Suite
The unified engine `compare_routing_algorithms` evaluates all 6 objectives simultaneously:
1. `BFS (Min Stops)`
2. `Dijkstra (Min Time)`
3. `Dijkstra (Min Distance)`
4. `0-1 BFS (Min Transfers)`
5. `Lexicographic (Transfers then Fastest)`
6. `Transfer-Aware (Configurable Penalty)`

Integrated directly into `pages/2_Route_Planner.py` and `pages/5_Algorithm_Lab.py`.

---

## 5. Verification & Testing
- Unit and property tests: `tests/test_minimum_transfers.py`, `tests/test_lexicographic_routing.py`, `tests/test_transfer_penalties.py`, `tests/test_transfer_instructions.py`, `tests/test_transfer_edge_cases.py`.
- Automated script: `scripts/verify_transfers.py`.
- Invariant check: Consecutive segments strictly satisfy destination-to-source continuity and non-negative transfer penalties.
