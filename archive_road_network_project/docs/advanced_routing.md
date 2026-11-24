# Advanced directed routing

Phase 5 covers Module 4 through manual bidirectional Dijkstra and Yen's loopless
route enumeration. Forward search follows outgoing roads. Backward search follows
original incoming roads, retaining the original key and orientation.

```text
initialize source and target heaps and distance maps
clean stale heap minima
while both frontiers exist and forward_min + backward_min < best_complete_cost:
    settle a minimum frontier node
    relax original outgoing or incoming keyed edges
    update complete cost where tentative distance maps meet
join forward predecessors with backward successors

Yen:
accept the first manual Dijkstra route
for each spur of the last accepted route:
    exclude earlier root nodes
    exclude exact next edges of accepted routes sharing the edge prefix
    run manual Dijkstra on a read-only filtered view
    combine root and spur, reject repeated nodes and duplicate edge sequences
    push into persistent candidate heap
accept the minimum candidate until K or heap exhaustion
```

Frontier intersection alone never terminates bidirectional search. Selected edge
keys survive both trees and every result passes the Phase 4 validator. Search
work can differ by graph, and bidirectional search has no universal speedup.

Routes are node-loopless and unique by their entire directed keyed edge sequence.
Parallel roads can therefore produce alternatives with identical junction lists.
K is an integer from 1 through a configurable maximum, default five. Booleans
and out-of-range requests raise errors. Fewer available routes yield fewer results.

Candidates sort by exact objective cost, distance, hop count, then a canonical
type-tagged edge signature. Scalar IDs and recursive tuples follow the Phase 3
canonical order. Search adjacency is canonical and equal-cost relaxation keeps
the first discovery. Numerical tolerances are reserved for checking calculated
costs. Edge Jaccard overlap uses intersection divided by union. Two empty paths
have overlap one. Diversity is one minus overlap. Zero baseline percentages
are undefined. These metrics measure edge identity, not shared geographic length.

Bidirectional heap work is O((V+E) log(V+E)) with duplicate heap entries.
Yen can perform up to K(V−1) Dijkstra searches. Candidate branching increases
memory and time, so interactive K is bounded. Alternative routes may share
most road segments.

Tests compare primary costs with NetworkX and an independent exhaustive
edge-distinct loopless enumerator on tiny multigraphs. Existing routing and
traversal tests remain regression gates.

```python
from src.graph.dataset_service import load
from src.routing.route_alternatives import find_alternative_routes

result = find_alternative_routes(load().graph, 0, 1, 3, "travel_time")
```
