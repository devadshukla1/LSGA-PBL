# Station Importance & Critical Interchange Analysis (Phase 5)

## 1. Executive Summary & Problem Formulation
In urban transit analytics, identifying critical stations is vital for vulnerability assessment, infrastructure investment, and operational planning.

**Important Academic Distinction**:
Graph centrality metrics assess **topological and structural network position**, NOT dynamic passenger ridership, passenger counts, or station platform overcrowding. A station with high structural betweenness lies on numerous theoretical shortest-hop routes across the transit network topology, while a suburban station with low centrality might still experience heavy passenger boarding.

---

## 2. MultiGraph Analytical Projection
The routing engine of MetroGraph operates on a NetworkX `MultiGraph` to retain exact parallel services (e.g. Airport Express running parallel to a local line along shared stations).

However, computing centrality directly on a MultiGraph introduces distortions:
1. Parallel edges between the same two stations artificially inflate adjacent degree counts.
2. Parallel edges create redundant duplicate shortest paths between identical pairs of stations, altering betweenness normalization.
3. DFS-based articulation cut-vertex detection operates on station connectivity adjacencies.

### Projection Rules (`src/analytics/graph_projection.py`)
- Input: `nx.MultiGraph` $\to$ Output: `nx.Graph` (simple, undirected).
- Station vertices $V$ and their spatial coordinates are preserved.
- Parallel multi-edges $(u, v, k_1), (u, v, k_2)$ collapse to a single edge $(u, v)$.
- Edge attributes retain minimum physical distance and travel time, plus an aggregated set of connecting lines.
- **Invariance**: The original routing `MultiGraph` is NEVER mutated.

---

## 3. Structural Centrality Metrics

### A. Degree Centrality
For simple undirected graph $G = (V, E)$ with $N = |V|$:
$$C_D(v) = \frac{\deg(v)}{N - 1}$$
where $\deg(v)$ is the count of distinct adjacent neighboring stations connected to $v$.
- **Edge cases**: If $N \le 1$, $C_D(v) = 0.0$.
- **Distinction from Line Count**: A station may serve 3 metro lines but only have 2 physical track directions (degree = 2, lines = 3). Conversely, a terminal junction may branch into 4 physical directions on a single line (degree = 4, lines = 1).

### B. Betweenness Centrality (Brandes' Algorithm)
Measures how often station $v$ acts as a bridge along shortest-hop paths:
$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
Normalized for undirected networks by:
$$\frac{2}{(N - 1)(N - 2)}$$
- Unweighted shortest-hop betweenness is the default primary ranking.
- Optional weighted betweenness uses minimum edge travel times.

### C. Articulation Points (Cut-Vertices)
A vertex $v$ is an articulation point if $G \setminus \{v\}$ strictly increases the count of connected components:
$$\kappa(G \setminus \{v\}) > \kappa(G)$$
- Detected via Tarjan's DFS Low-Link algorithm in $\mathcal{O}(V + E)$ time.
- **Topological Significance**: Failure of an articulation station immediately divides the transit network into isolated sub-networks.
- A high-betweenness station is not necessarily an articulation point (e.g. in redundant mesh cycles).

---

## 4. Algorithmic Complexity

| Algorithm | State Space | Time Complexity | Space Complexity |
|---|---|---|---|
| Graph Projection | MultiGraph $\to$ Simple Graph | $\mathcal{O}(V + E_{\text{multi}})$ | $\mathcal{O}(V + E_{\text{simple}})$ |
| Degree Centrality | Simple Graph | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ |
| Betweenness Centrality (Brandes) | Simple Graph | $\mathcal{O}(V \cdot E)$ | $\mathcal{O}(V + E)$ |
| Articulation Points (Tarjan DFS) | Simple Graph | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ |
| Connected Components (BFS/DFS) | Simple Graph | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ |

---

## 5. Delhi Metro Empirical Findings (Active Dataset)
Computed on the full Delhi Metro dataset (260 stations, 13 lines, 273 connections):
- **Total Interchange Hubs**: 25 stations serving $\ge 2$ metro lines.
- **Top Betweenness Hub**: **Hauz Khas (STN065)** ($C_B \approx 0.441$), acting as the vital southern connector between Yellow and Magenta lines.
- **Top Degree Station**: **Kashmere Gate (STN097)** ($\deg = 6$), converging Red, Yellow, and Violet lines.
- **Articulation Points**: 131 cut-vertices detected, revealing that major branch lines (e.g. outer Green Line, Airport Express, Aqua Line) exhibit tree-like radial topologies where station closures partition the network.

---

## 6. Implementation & UI Modules
- `src/analytics/models.py`: Strongly typed `StationAnalyticsResult` and `NetworkAnalyticsSummary`.
- `src/analytics/graph_projection.py`: MultiGraph to Graph collapse preserving minimum edge attributes.
- `src/analytics/degree_centrality.py` & `betweenness_centrality.py`: Centrality engines matching NetworkX oracles.
- `src/analytics/interchange_analysis.py`: Multi-line intersection identification.
- `src/analytics/articulation_points.py`: Cut-vertex analysis.
- `src/analytics/connectivity.py`: Component decomposition.
- `src/analytics/station_ranking.py`: Multi-metric sorting and CSV export generator.
- `src/analytics/station_comparison.py`: Pairwise attribute contrast.
- `src/visualization/metro_plot.py`:
  - `plot_centrality_network`: Continuous colorscale node heatmap with dual-ring interchange highlights and red cut-vertex diamonds.
  - `plot_top_stations`: Horizontal bar chart for top N stations.
- `pages/3_Station_Importance.py`: Complete Streamlit analytics dashboard.
