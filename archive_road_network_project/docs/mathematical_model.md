# Mathematical Graph Model

**Product:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Project Root:** `LSGA PBL`  

---

## 1. Formal Network Definition

An urban street network is mathematically modeled as a directed, weighted multigraph:

$$G = (V, E)$$

Where:
- $V = \{v_1, v_2, \dots, v_n\}$ is the finite set of road intersections, endpoints, and dead-ends. Each node $v \in V$ is geographically positioned by geodetic coordinates $(\phi_v, \lambda_v)$ representing latitude and longitude in decimal degrees (WGS 84 datum).
- $E \subseteq V \times V \times \mathbb{N}_0$ is the finite multiset of directed road segments.
- Each directed edge $e \in E$ is represented as an ordered 3-tuple:
  $$e = (u, v, k)$$
  where $u \in V$ is the source intersection, $v \in V$ is the destination intersection, and $k \in \mathbb{N}_0 = \{0, 1, 2, \dots\}$ is the distinct edge key that differentiates parallel edges between identical intersection pairs (e.g., dual carriageways, service lanes, or multi-level ramps).

---

## 2. Edge Attributes & Metrics

Every directed edge $e = (u, v, k) \in E$ is characterized by non-negative, finite physical and kinematic attributes:

1. **Physical Arc Length:**
   $$L(e) \in \mathbb{R}^+, \quad [L(e)] = \text{meters (m)}$$
   representing the true curve geometry length along the road centerline.

2. **Legal Speed Limit:**
   $$S(e) \in \mathbb{R}^+, \quad [S(e)] = \text{km/h}$$
   converted to SI units as $v(e) = \frac{S(e)}{3.6}\text{ m/s}$.

3. **Free-Flow Baseline Travel Time:**
   $$T(e) = \frac{L(e)}{v(e)} = \frac{L(e) \cdot 3.6}{S(e)} \in \mathbb{R}^+, \quad [T(e)] = \text{seconds (s)}$$

4. **Directed Non-Negativity Invariant:**
   $$\forall e \in E: \quad L(e) > 0, \quad T(e) > 0$$
   This strictly satisfies the prerequisite condition for greedy label-setting algorithms (Dijkstra).

---

## 3. Dynamic Traffic Simulation & Road Closure Formulation

Urban traffic dynamics and unexpected physical disruptions modify edge traversal costs and network topology without mutating the baseline graph $G$:

### 3.1 Simulated Congestion Model
Let $M_s: E \to [1.0, \infty)$ denote the scenario-specific congestion multiplier function. For any scenario $s$, the effective travel time $T_s(e)$ is given by:

$$T_s(e) = T(e) \cdot M_s(e) = T(e) \cdot \Big(1 + C_s(e)\Big)$$

Where $C_s(e) \ge 0$ is the non-negative congestion factor assigned based on traffic severity:
- **Free Flow:** $C_s(e) = 0.0 \implies M_s(e) = 1.0$ (Baseline travel time)
- **Light Congestion:** $C_s(e) = 0.2 \implies M_s(e) = 1.2$ (+20% delay)
- **Moderate Congestion:** $C_s(e) = 0.5 \implies M_s(e) = 1.5$ (+50% delay)
- **Heavy Congestion:** $C_s(e) = 1.0 \implies M_s(e) = 2.0$ (+100% delay)
- **Severe Congestion:** $C_s(e) = 1.5 \implies M_s(e) = 2.5$ (+150% delay)

### 3.2 Road Closures and Incident Inaccessibility
Let $E_{\text{closed}} \subset E$ represent the set of completely closed road links (e.g., severe flooding, construction, structural collapse), and let $V_{\text{blocked}} \subset V$ represent blocked intersections (e.g., active multi-vehicle accidents).

The active traversable routing graph for scenario $s$ is the induced subgraph:

$$G_s = (V_s, E_s)$$

Where:
$$V_s = V \setminus V_{\text{blocked}}$$
$$E_s = \Big\{ (u, v, k) \in E \;\Big|\; u \in V_s \;\land\; v \in V_s \;\land\; (u, v, k) \notin E_{\text{closed}} \Big\}$$

**Crucial Invariant:** Closed edges are completely excluded from the feasible path set ($e \notin E_s$). They are **not** represented by setting $T_s(e) = \infty$, thereby preventing numerical overflow and false traversals in floating-point priority queues.

---

## 4. Single-Objective Optimization Formulations

A route $P$ from origin $v_s \in V_s$ to destination $v_t \in V_s$ is a sequence of alternating vertices and directed edge keys:

$$P = \Big(v_0, (v_0, v_1, k_0), v_1, (v_1, v_2, k_1), v_2, \dots, (v_{m-1}, v_m, k_{m-1}), v_m\Big)$$
where $v_0 = v_s$ and $v_m = v_t$.

### 4.1 Shortest Distance Objective
Find a feasible path $P^*$ that minimizes the total physical distance traversed:

$$\min_{P \in \mathcal{P}(v_s, v_t)} \sum_{i=0}^{m-1} L(v_i, v_{i+1}, k_i)$$

### 4.2 Fastest Travel Time Objective (Emergency Route)
Find a feasible path $P^*$ that minimizes total expected travel time under scenario conditions $s$:

$$\min_{P \in \mathcal{P}(v_s, v_t)} \sum_{i=0}^{m-1} T_s(v_i, v_{i+1}, k_i)$$

---

## 5. Admissible & Consistent Heuristic Function for A*

For A* search targeting vertex $v_t$, let $h(u)$ denote the heuristic lower-bound estimate from intermediate node $u = (\phi_u, \lambda_u)$ to target $v_t = (\phi_t, \lambda_t)$.

### 5.1 Haversine Great-Circle Distance
The physical spatial distance $D_{\text{hav}}(u, v_t)$ over the Earth's spherical surface (mean radius $R = 6,371,000\text{ m}$) is computed via the Haversine formula:

$$\Delta \phi = \phi_t - \phi_u, \quad \Delta \lambda = \lambda_t - \lambda_u$$
$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_u)\cos(\phi_t)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$
$$D_{\text{hav}}(u, v_t) = 2 R \cdot \arcsin\left(\min(1.0, \sqrt{a})\right)$$

### 5.2 Heuristic Formulation by Objective
1. **For Distance Objective:**
   $$h_{\text{dist}}(u) = D_{\text{hav}}(u, v_t)$$
   Since the great-circle arc is the absolute shortest geodesic distance between two points on a sphere:
   $$\forall (u, v, k) \in E: \quad D_{\text{hav}}(u, v_t) \le L(u, v, k) + D_{\text{hav}}(v, v_t)$$
   Hence, $h_{\text{dist}}(u)$ is strictly **admissible** ($h(u) \le d^*(u, v_t)$) and **consistent / monotonic**.

2. **For Travel Time Objective:**
   $$h_{\text{time}}(u) = \frac{D_{\text{hav}}(u, v_t)}{v_{\max}}$$
   where $v_{\max} = \frac{120\text{ km/h}}{3.6} \approx 33.333\text{ m/s}$ is the global maximum permissible speed bound.
   Because no vehicle can exceed $v_{\max}$:
   $$\frac{D_{\text{hav}}(u, v_t)}{v_{\max}} \le \frac{L(u, v, k)}{v(u, v, k)} + \frac{D_{\text{hav}}(v, v_t)}{v_{\max}} \le T(u, v, k) + h_{\text{time}}(v)$$
   Hence, $h_{\text{time}}(u)$ is guaranteed to be **admissible** and **consistent**, ensuring A* never overestimates remaining cost and guarantees optimal shortest-path discovery.

---

## 6. Undirected Projection for Spanning Forest Analysis

Because Minimum Spanning Tree (MST) algorithms operate strictly on undirected connected graphs, directed road networks must be projected symmetrically:

$$G_{\text{undirected}} = (V, E_{\text{sym}})$$

For each pair $u, v \in V$ with directed edges between them:
$$W_{\text{sym}}(u, v) = \min \Big\{ L(u, v, k) \;\Big|\; (u, v, k) \in E \Big\} \cup \Big\{ L(v, u, k') \;\Big|\; (v, u, k') \in E \Big\}$$

The Minimum Spanning Forest (MSF) solves:
$$\min_{F \subseteq E_{\text{sym}}} \sum_{e \in F} W_{\text{sym}}(e) \quad \text{s.t. } F \text{ spans all connected components without cycles.}$$

For a network partitioned into $C$ connected components, the total edge count in the forest is precisely:
$$|E_{\text{MSF}}| = |V| - C$$
