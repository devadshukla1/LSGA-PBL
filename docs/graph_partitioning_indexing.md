# Phase 8: Graph Partitioning, Spatial Indexing & Partition Quality Analysis

**Product:** SmartRoute Analytics  
**Academic Subject:** Large-Scale Graph Analysis  
**Syllabus:** Modules 2 and 3  
**Status:** Implemented & Verified  

---

## 1. Phase 8 Objectives

Phase 8 introduces scalable, reproducible graph partitioning and spatial indexing algorithms for directed road networks. The primary goals are:

1. **Geographic Graph Partitioning:** Recursively divide road networks along alternating geographic axes to produce spatially coherent, balanced clusters.
2. **Graph-Aware Partitioning:** Partition networks using balanced multi-source region growing and bounded boundary refinement to reduce cut edges.
3. **Directed Cut-Edge Analysis:** Rigorously evaluate cut edges across original directed `MultiDiGraph` road edges, including parallel and opposite-direction roads.
4. **Partition Balance Metrics:** Calculate node count distribution, standard deviation, and balance ratio ($\max / \text{mean}$).
5. **Spatial KD-Tree Indexing:** Implement a 3D Earth-centered Cartesian KD-tree over WGS84 coordinates to accelerate nearest-node selection.
6. **Ground-Truth Verification:** Implement an exhaustive $O(V)$ brute-force distance query to establish empirical correctness and deterministic tie-breaking.
7. **Empirical Benchmarking:** Quantify index construction time, query latencies, and partitioning runtimes without confounding preprocessing with query execution.

---

## 2. Geographic Graph Partitioning

### 2.1 Principles and Recursive Bisection
Geographic partitioning divides the network based purely on junction spatial coordinates $(lat, lon)$. It produces compact geometric cells suitable for distributed storage and geographic dispatching.

To prevent distortions caused by comparing raw degree spans, the algorithm scales coordinates using a spherical local metric projection:
$$\Delta Y_m = (\max(lat) - \min(lat)) \times 111\,320$$
$$\Delta X_m = (\max(lon) - \min(lon)) \times 111\,320 \times \cos(\text{radians}(lat_{mid}))$$

The algorithm selects the axis with the larger physical metric spread, sorts nodes along that axis with deterministic tie-breaking (by primary coordinate, secondary coordinate, and canonical node ID string), and splits the nodes into balanced subproblems.

### 2.2 Arbitrary Partition Count ($K \ge 1$)
Unlike simple quad-tree or power-of-two recursive bisection, our implementation supports arbitrary $K \ge 1$:
$$\text{left\_k} = \lfloor K / 2 \rfloor, \quad \text{right\_k} = K - \text{left\_k}$$
$$\text{split\_index} = \max\left(\text{left\_k}, \min\left(|V| - \text{right\_k}, \text{round}\left(|V| \cdot \frac{\text{left\_k}}{K}\right)\right)\right)$$

This ensures that every partition receives at least one node and partition sizes differ by at most 1 node, achieving a balance ratio of approximately 1.0.

### 2.3 Pseudocode: Geographic Recursive Bisection
```text
Algorithm GeographicRecursiveBisection(nodes, K, offset):
    if K == 1:
        for node in nodes:
            assignment[node] = offset
        return

    mid_lat = (min(lat) + max(lat)) / 2
    delta_y = (max(lat) - min(lat)) * 111320
    delta_x = (max(lon) - min(lon)) * 111320 * cos(radians(mid_lat))

    if delta_y >= delta_x:
        sort nodes by (lat, lon, str(node_id))
    else:
        sort nodes by (lon, lat, str(node_id))

    left_k = floor(K / 2)
    right_k = K - left_k
    split = clamp(round(|nodes| * (left_k / K)), left_k, |nodes| - right_k)

    GeographicRecursiveBisection(nodes[0:split], left_k, offset)
    GeographicRecursiveBisection(nodes[split:|nodes|], right_k, offset + left_k)
```

**Complexity:** $O(|V| \log |V| \log K)$ runtime, $O(|V|)$ auxiliary space.

---

## 3. Graph-Aware Partitioning

### 3.1 Region Growing and Undirected View
Graph-aware partitioning considers road connectivity rather than geographic coordinates alone. 
1. **Adjacency View:** A temporary undirected adjacency representation is constructed. Directed edges $(u, v)$ and $(v, u)$, as well as parallel multi-edges, are collapsed into undirected neighbor sets for traversal while the original `MultiDiGraph` is preserved intact.
2. **Seed Selection:** $K$ seed nodes are chosen deterministically. The initial seed is the node with maximum degree. Subsequent seeds are chosen via farthest-point selection: maximizing the minimum distance (hop distance or geographic fallback) to all previously selected seeds.
3. **Multi-Source BFS Expansion:** Each seed initializes a FIFO queue for its partition. Partitions expand concurrently in round-robin order up to their target capacities ($\lfloor |V| / K \rfloor$ or $\lceil |V| / K \rceil$).
4. **Disconnected Graph Handling:** Stranded components or isolates are assigned deterministically to the smallest partition or adjacent components.

### 3.2 Bounded Boundary Refinement
After initial region growing, a Fiduccia-Mattheyses style boundary refinement pass evaluates moving boundary nodes:
$$\text{gain}(u, P') = E(u, P') - E(u, P(u))$$
where $E(u, P)$ is the count of edges from $u$ to nodes in partition $P$. If moving $u$ to $P'$ strictly reduces cut edges ($\text{gain} > 0$) without violating the balance tolerance:
$$|\text{new\_size} - \text{target}| \le \text{max\_imbalance}$$
the move is accepted. The pass is bounded to at most 3 iterations to prevent cycling.

### 3.3 Pseudocode: Graph-Aware Region Growing
```text
Algorithm GraphAwarePartitioning(G, K, balance_tolerance):
    neighbors = build_undirected_view(G)
    seeds = select_k_farthest_seeds(neighbors, K)
    
    queues = {p: Queue([seeds[p]]) for p in 0..K-1}
    assignment = {seeds[p]: p for p in 0..K-1}
    target_sizes = compute_balanced_targets(|V|, K)
    
    while unassigned nodes exist:
        for p in 0..K-1:
            if size(p) < target_sizes[p] and not queues[p].empty():
                u = queues[p].pop()
                for v in sorted(neighbors[u]):
                    if v not in assignment and size(p) < target_sizes[p]:
                        assignment[v] = p
                        queues[p].push(v)
                        
    for pass in 1..max_passes:
        for u in boundary_nodes(G, assignment):
            evaluate gain and balance constraint;
            if beneficial: move u;
            
    return assignment
```

**Complexity:** $O(|V| + |E|)$ for region growing; $O(\text{passes} \cdot |V_{boundary}| \cdot \text{deg}_{avg})$ for refinement.

---

## 4. Directed Cut-Edge and Balance Analysis

### 4.1 Directed MultiDiGraph Cut-Edge Definition
A cut edge is an original directed edge $(u, v, key)$ where $\text{partition}(u) \ne \text{partition}(v)$.
- Each direction is counted individually: if roads exist in both directions between $u$ and $v$ across a partition boundary, both $u \to v$ and $v \to u$ are cut edges.
- Parallel roads between $u$ and $v$ are counted individually.
- Cut-Edge Ratio:
  $$\text{Cut-Edge Ratio} = \frac{\text{Total Cut Edges}}{|E|}$$
  For zero-edge graphs, the ratio is defined as 0.0.

### 4.2 Partition Balance Metrics
Balance is quantified via:
- Mean partition size: $\mu = |V| / K$
- Standard deviation: $\sigma = \sqrt{\frac{1}{K} \sum_{p=0}^{K-1} (|V_p| - \mu)^2}$
- Maximum-to-mean balance ratio:
  $$\text{Balance Ratio} = \frac{\max_{p} |V_p|}{\mu}$$
  An ideal partition has a balance ratio of 1.0.

---

## 5. Spatial Nearest-Node Indexing

### 5.1 3D Earth-Centered Cartesian Projection
A 2D Euclidean KD-tree over raw latitude and longitude degrees produces severe distortion at non-equatorial latitudes. To achieve exact geographic distance ordering, coordinates are transformed into 3D Cartesian coordinates on a sphere ($R = 6\,371\,008.8$ m):
$$x = R \cos(\phi) \cos(\lambda), \quad y = R \cos(\phi) \sin(\lambda), \quad z = R \sin(\phi)$$
where $\phi = \text{radians}(lat)$ and $\lambda = \text{radians}(lon)$.

The 3D Euclidean chord distance $d_{3D}$ between points on a sphere is monotonically strictly increasing with the great-circle arc distance $d_{GC}$:
$$d_{GC} = 2 R \arcsin\left(\frac{d_{3D}}{2 R}\right)$$
Consequently, nearest neighbors in 3D Euclidean space are guaranteed to be nearest neighbors in spherical great-circle distance.

### 5.2 Deterministic Tie-Breaking
When multiple nodes are equidistant to a query point (e.g., duplicated coordinates or equidistant grid points), candidate nodes within an $\epsilon$-neighborhood of the minimum chord distance are examined, and ties are broken canonically using `str(node_id)`.

### 5.3 Pseudocode: Spatial KD-Tree Index
```text
Algorithm BuildSpatialIndex(graph):
    coords = extract_node_coordinates(graph)
    node_ids = sorted(coords.keys(), key=str)
    points_3d = []
    for nid in node_ids:
        lat, lon = coords[nid]
        points_3d.append(lat_lon_to_cartesian_3d(lat, lon))
    tree = cKDTree(points_3d)
    return SpatialIndex(tree, node_ids, coords)

Algorithm NearestNode(index, query_lat, query_lon):
    q_3d = lat_lon_to_cartesian_3d(query_lat, query_lon)
    d_min, best_idx = index.tree.query(q_3d, k=1)
    candidates = index.tree.query_ball_point(q_3d, r=d_min * (1 + 1e-9) + 1e-4)
    best_idx = min(candidates, key=lambda i: (haversine(query, coords[node_ids[i]]), str(node_ids[i])))
    node = node_ids[best_idx]
    dist_m = haversine(query, coords[node])
    return NearestNodeResult(node, dist_m, coords[node])
```

---

## 6. Empirical Offline Benchmark Results

Measurements taken on the verified offline synthetic road network (16 junctions, 34 directed roads, $K=4$):

| Metric | Geographic Bisection | Graph-Aware Region Growing |
| :--- | :--- | :--- |
| **Cut Edges (Directed)** | 12 | 12 |
| **Cut-Edge Ratio** | 35.29% | 35.29% |
| **Balance Ratio ($\max / \mu$)** | 1.000 | 1.250 |
| **Partition Size Std Dev** | 0.00 | 0.71 |
| **Cross-Partition Length** | 1,326.0 m | 1,326.0 m |
| **Partitioning Runtime** | 0.28 ms | 0.45 ms |

### Spatial Indexing Performance:
- **Spatial Index Build Time:** 0.376 ms
- **Brute-Force Query Time:** 1.047 ms ($O(V)$ scan)
- **KD-Tree Query Time:** 0.124 ms ($O(\log V)$ tree traversal)
- **Measured Speedup:** **8.44x** (correctness verified: 100% agreement with brute-force)

---

## 7. Syllabus Mapping

| Syllabus Module | Concepts Covered | Implementation File |
| :--- | :--- | :--- |
| **Module 2: Graph Partitioning** | Recursive geographic bisection, physical coordinate scaling | `src/partitioning/geographic.py` |
| **Module 2: Graph-Aware Partitioning** | Multi-source region growing, boundary refinement | `src/partitioning/graph_aware.py` |
| **Module 2: Partition Quality Metrics** | Directed cut-edge ratio, balance ratio, coefficient of variation | `src/partitioning/partition_metrics.py` |
| **Module 3: Spatial Indexing** | Earth-centered 3D Cartesian KD-trees, Haversine spherical distance | `src/indexing/spatial_index.py` |
| **Module 3: Nearest-Neighbor Search** | Indexed vs brute-force query benchmarks, tie-breaking | `src/indexing/nearest_node.py` |
| **Module 3: Performance Analysis** | Preprocessing cost amortization, empirical query speedups | `src/benchmarks/partition_benchmarks.py` |

---

## 8. Known Limitations

1. **Global Optimality:** Graph partitioning is an NP-hard problem. Region growing and geographic bisection are fast heuristics; they do not guarantee globally minimal cut edges.
2. **Spherical Earth Approximation:** Great-circle distance uses a mean spherical radius $R = 6\,371\,008.8$ m, accurate within ~0.5% of the WGS84 ellipsoid for local and regional urban scale.
3. **Small Graph Preprocessing Overhead:** Building a spatial KD-tree introduces upfront preprocessing latency ($O(V \log V)$). For small graphs with fewer than 10 total queries, brute-force lookup may exhibit lower total wall-clock time.
