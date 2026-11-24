# Metro Routing Engine: Graph Models, Algorithms & Complexity

## 1. Graph Model Foundations
MetroGraph Analytics models public transit networks using an undirected `networkx.MultiGraph` $G = (V, E)$:
- **Vertices $V$**: Physical metro stations.
- **Edges $E$**: Track links connecting adjacent stations. Parallel edges connecting the same vertex pair $(u, v)$ represent separate line services running along the corridor (e.g. Red Line and Yellow Line sharing a junction corridor).
- **Edge Identity**: Stored with a deterministic key `(u, v, key)` where `key = line_id` to prevent multi-edge collapsing.

---

## 2. Algorithms Implemented

### A. Breadth-First Search (BFS) — Minimum Stops
BFS explores the network level-by-level using a FIFO queue (`collections.deque`), guaranteeing that the first time the destination node is encountered, the path contains the minimum possible number of station-to-station segments (stops).

#### Pseudocode
```text
function find_route_bfs(G, source, destination):
    if source == destination:
        return ZeroHopRoute
    queue = deque([source])
    visited = {source}
    predecessors = {}
    
    while queue is not empty:
        curr = queue.popleft()
        if curr == destination:
            break
        for neighbor in sorted(G.neighbors(curr)):
            if neighbor not in visited:
                visited.add(neighbor)
                predecessors[neighbor] = curr
                queue.append(neighbor)
                if neighbor == destination:
                    break
    return reconstruct_route(G, source, destination, predecessors)
```

#### Parallel Edge Tie-Breaking Policy
When traversing between consecutive stations $u$ and $v$ with parallel edges, BFS breaks ties deterministically:
1. Smallest positive `estimated_time_min`.
2. Smallest positive `distance_km`.
3. Alphabetical `line_id` and `edge_key`.

---

### B. Dijkstra's Algorithm — Weighted Shortest Path
Dijkstra's algorithm uses a binary priority queue (`heapq`) to find paths minimizing either:
1. **Minimum Travel Time**: $w(e) = \text{estimated\_time\_min}$
2. **Minimum Modeled Distance**: $w(e) = \text{distance\_km}$

#### Monotonic Heap Tie-Breaking
To prevent runtime type errors when comparing heap tuples containing heterogeneous node types (e.g. ints and strings), entries are stored as:
$$\text{heap\_entry} = (\text{cost}, \text{entry\_counter}, \text{node\_id})$$
where `entry_counter` is an incrementing integer.

#### Pseudocode
```text
function find_route_dijkstra(G, source, destination, weight_attr):
    if source == destination:
        return ZeroHopRoute
    pq = [(0.0, 0, source)]
    distances = {source: 0.0}
    predecessors = {} # node -> (parent, edge_key)
    settled = set()
    counter = 0

    while pq is not empty:
        curr_cost, _, u = heappop(pq)
        if u in settled:
            continue
        settled.add(u)
        if u == destination:
            break
        for v in sorted(G.neighbors(u)):
            if v in settled:
                continue
            for edge_key, attrs in G[u][v].items():
                w = attrs[weight_attr] # must be finite and >= 0
                new_cost = curr_cost + w
                if new_cost < distances.get(v, infinity):
                    distances[v] = new_cost
                    predecessors[v] = (u, edge_key)
                    counter += 1
                    heappush(pq, (new_cost, counter, v))
    return reconstruct_route(G, source, destination, predecessors)
```

---

## 3. Complexity Analysis

| Algorithm | Objective | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| **BFS** | Minimum Station Stops | $\mathcal{O}(\|V\| + \|E\|)$ | $\mathcal{O}(\|V\|)$ |
| **Dijkstra (Binary Heap)** | Min Time / Min Distance | $\mathcal{O}((\|V\| + \|E\|) \log \|V\|)$ | $\mathcal{O}(\|V\| + \|E\|)$ |

*Note*: In a `MultiGraph`, $\|E\|$ denotes the total number of parallel line links (for Delhi Metro, $\|V\|=260, \|E\|=273$).

---

## 4. Route Metrics & Output Specifications
Algorithm execution records:
- `runtime_ms`: High-precision timer (`time.perf_counter_ns()`).
- `explored_nodes`: Total vertices popped from the queue/min-heap.
- `examined_edges`: Total multi-edges evaluated during adjacency traversal.
- `total_stops`: Number of transit segments ($\text{len}(\text{path}) - 1$).
- `total_distance_km`: Cumulative track distance.
- `total_estimated_time_min`: Cumulative modeled travel time.
- `segments`: List of `RouteSegment` dataclass instances preserving `(source, destination, edge_key, line_id, distance_km, estimated_time_min)`.

---

## 5. Missing Weight & Edge Case Policy
- Negative weights ($\le 0$ when expected positive) raise `DijkstraExecutionError`.
- Non-finite or NaN weights raise `DijkstraExecutionError`.
- Disconnected queries return `reachable=False` with a human-readable notice.
- Zero-hop queries ($u = v$) immediately return $0\text{ stops}$ and $0.0\text{ cost}$.
- Mixed-type station identifiers (e.g. ints and strings) are resolved deterministically without crashing heap comparisons.
