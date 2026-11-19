# Shortest path routing

Phase 4 addresses Module 4 through weighted, directed road routing. Dijkstra
uses the lowest accumulated cost first. A* uses accumulated cost plus a
conservative geographic lower bound. Both operate on each directed edge
individually, retaining its original parallel-edge key. Routing never assumes
a reverse road exists.

```text
best[source] = 0; push (priority, serial, source)
while heap:
    pop minimum; skip stale accumulated costs
    if target: finish
    for each keyed outgoing road:
        candidate = best[current] + edge weight
        if candidate improves best[neighbor]:
            save (current, exact edge key) as predecessor
            push candidate + heuristic(neighbor)
reconstruct predecessor records from target to source
```

Dijkstra sets every heuristic to zero. A* calculates haversine metres from
longitude and latitude, transforming projected CRS coordinates first. It
multiplies the distance by the minimum edge cost divided by the geographic
distance across all directed edges. For distance, the factor is clamped at one.
For estimated time, the factor has seconds per metre. A small conservative
reduction handles floating-point rounding. The triangle inequality makes
these factors consistent under geographic coordinates. Missing or uncertain
CRS and coordinates use zero. An overestimating heuristic could let A* finish
with a nonoptimal path. A consistent lower bound keeps both algorithms'
optimal costs equal on valid nonnegative weights.

Relaxation uses heapq with a monotonic serial counter, so mixed node IDs never
need direct comparison. Stale heap records are skipped. Exact predecessor
records reconstruct both node and keyed edge paths. Metrics sum the selected
edge weights. Distance uses metres. Time uses static, estimated seconds from
Phase 2 speed assumptions. They are not live traffic conditions.

Build adjacency in O(V+E). Heap search uses O((V+E) log(V+E)) time with
duplicate entries and O(V+E) auxiliary storage in the worst case. Geographic
heuristic preprocessing scans all nodes and edges. The dashboard performs
routing only after button submission and caps map context at 500 roads.
Unavailable routes return an explicit unreachable state with no cost.

```python
from src.graph.dataset_service import load
from src.routing.routing_service import find_route

graph = load().graph
route = find_route(graph, 0, 1, "astar", "travel_time")
assert route.edge_path == ((0, 1, 7),)
```

Offline tests compare both objectives with NetworkX across deterministic
directed multigraphs and verify exact edge-key metrics. Run
`python scripts/verify_routing.py` for the bundled sample.
