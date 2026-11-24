# Delhi Metro Graph Model & Topological Invariants

## 1. Graph Theoretical Representation
- **Graph Class**: `networkx.MultiGraph` (Undirected Multigraph)
- **Mathematical Definition**: $G = (V, E)$ where:
  - $V$: Set of physical metro stations.
  - $E$: Set of adjacent track connections, where multiple edges $e_1, e_2 \in E$ may connect the same node pair $(u, v)$ under distinct line services (`line_id`).

### Why `MultiGraph`?
In metropolitan transit networks, multiple lines frequently share stations or parallel track corridors. For example, Kashmere Gate serves the Red, Yellow, and Violet lines simultaneously, and certain suburban segments run dual line services. A standard simple `Graph` would collapse these into a single edge, losing line attributes, frequency, and transfer boundaries.

---

## 2. Invariants & Structural Diagnostics

### Node Attributes
- `station_name` / `name` (str): Station name.
- `lat` (float): Latitude coordinate $[-90.0, 90.0]$.
- `lon` (float): Longitude coordinate $[-180.0, 180.0]$.
- `lines` (set[str]): Set of unique line IDs serving this station.
- `station_line_count` (int): Number of distinct lines $\ge 1$.
- `is_interchange` (bool): `True` if `station_line_count >= 2`.

### Edge Attributes
- `key` (str): Line identifier ensuring stable MultiGraph keying.
- `line_id` (str): Unique line ID.
- `line_name` (str): Human-readable line name.
- `line_color` (str): Hex color code.
- `distance_km` (float): Positive segment distance ($d > 0$).
- `estimated_time_min` (float): Positive estimated traversal time ($t > 0$).
- `weight_provenance` (str): Provenance tracking (`published`, `derived`, `geodesic_distance_km`).

---

## 3. Structural Interchange Detection
Implemented in `src/graph/interchanges.py`:
A station is structurally an interchange if:
$$\text{deg}_{\text{lines}}(v) = |\text{lines}(v)| \ge 2$$
In the verified Delhi Metro dataset:
- Total Stations $|V| = 260$
- Total Lines $|L| = 13$
- Interchange Hubs: 25 stations (e.g. Kashmere Gate, Rajiv Chowk, Central Secretariat, Hauz Khas, Botanical Garden, Welcome).
- Connected Components: 1 (after pedestrian walkway corridor linking Noida Sector 51 and 52).
- Average Degree: 2.10.

---

## 4. GraphML Serialization & Cache Architecture
Processed graphs are cached in `data/processed/metro_network.graphml` alongside sidecar metadata (`metro_network.json`):
- Node sets are serialized into comma-separated strings for GraphML compatibility.
- Type restoration parses numeric coordinates and restores Python sets upon cache reload.
