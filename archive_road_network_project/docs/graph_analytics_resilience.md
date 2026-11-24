# Graph analytics and resilience

Phase 7 addresses Modules 4 and 5 through directed structural analytics and
simulated junction removal. These metrics describe structural importance.
Traffic demand, physical road safety and emergency performance require
additional evidence.

Degree counts directed edge incidences, including parallel edges and loops
(a loop contributes to both in- and out-degree). Normalized values divide by
max(1,n−1), so multigraph scores can exceed one. Unique-neighbor count is also
available.

Betweenness uses strictly positive distance or time costs. Zero costs are
rejected. Graphs over 500 nodes default to 100 seeded sampled sources.
Explicit exact override is available in the API. Closeness uses inward
accessibility by default, optionally the reversed graph for outward
accessibility, with Wasserman–Faust disconnected normalization. PageRank is
unweighted directed structural importance with damping .85, bounded iteration
and a clear nonconvergence error.

Criticality min-max normalizes each available metric, assigning zero for
constant distributions. Weights are betweenness .40, degree .25, closeness .20
and PageRank .15. These are heuristic screening assumptions. Missing metrics
cause transparent renormalization over available weights. Equal scores break
ties using canonical scalar identifiers.

Connectivity summaries reuse the manual Phase 3 weak/strong component passes.
Failure rankings remain fixed from the intact baseline. Removal uses read-only
node-filtered views. Random selection is seeded and without replacement.
Failure percentage becomes floor(n*fraction), identical for both strategies.
Experiments report random population standard deviation, mean, minimum and
maximum over at least two repetitions. The default is ten and the cap is thirty.

Fragmentation is one minus the largest weak component fraction among survivors.
An empty remaining graph has fragmentation one and component fractions zero.
Retention uses original node count as denominator. Both denominators are
reported. Directed reachability counts ordered distinct survivor pairs.
At most 100 survivors use exact source BFS; larger graphs estimate from 200
seeded ordered pairs sampled with replacement. Results disclose sampling.
No statistical-significance claim is made.

The undirected projection chooses the lowest-cost original keyed edge for
each unordered endpoint pair, across both directions and all parallel edges.
Self-loops are excluded and isolates retained. This explicitly ignores
one-way restrictions. NetworkX computes the minimum spanning forest. For V
nodes and C components the invariant is V−C forest edges. This structural
projection has no directed emergency-route interpretation.

Weighted betweenness can require one shortest-path search per source.
Closeness also requires many shortest-path searches. PageRank is iterative.
Failure experiments repeat component and reachability work. The dashboard
runs only explicit actions and retains results in session state. Map layers
are limited to 300 items independently of algorithm sampling.

Offline tests cover directed orientation, multigraph degrees, seeded sampling,
component denominators, exact directed reachability, forest provenance and
baseline immutability. Use python scripts/verify_analytics.py for a sample report.

```python
from src.graph.dataset_service import load
from src.analytics.centrality import centrality
from src.analytics.mst import minimum_spanning_forest

graph = load().graph
importance = centrality(graph, "betweenness")
forest = minimum_spanning_forest(graph)
```
