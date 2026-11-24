# Directed road traversal

Phase 3 covers Module 4 through reachability and component analysis. From synthetic
junction 0, both parallel roads to junction 1 are examined. BFS discovers 1 once,
at depth one, recording the smaller key. From 1 the reverse hop to 0 requires
an actual outgoing edge. BFS minimizes directed hop count. Road metres and
estimated seconds play no part in selecting a traversal tree.

## Algorithms

```text
BFS: mark and enqueue source at depth zero
while queue has nodes:
    remove oldest node u
    for each outgoing keyed road to v:
        if unseen: record parent u, edge key and depth[u]+1, mark and enqueue v

DFS: mark source and push its outgoing iterator
while frames remain:
    consume next edge of top frame
    if unseen child: record discovery, parent, tree depth and push child frame
    if frame exhausted: record finish and pop

Kosaraju: run the DFS frame procedure from every unvisited root
record each reversed edge and append each node when its frame finishes
in reverse finishing order, flood unseen roots using reversed edges
each flood yields one strongly connected component
```

BFS and DFS run to exhaustion. The source counts as reachable. Every examined
parallel edge and self-loop contributes to the edge counter. DFS tree depth
depends on the exploration order. For a hop-minimal path, follow BFS parents
from target to source and reverse the sequence. An absent target in the tree
returns an empty path and no hop count. A broken or cyclic parent chain raises
ValueError. Public searches reject unknown junction IDs.

Weak components flood a temporary bidirectional view. Strong components group
junctions that can reach each other in both directions. IDs start at zero in
flood order, using canonical roots for weak components and decreasing finish
order for strong components. Canonical order compares scalar type names, then
values within type. Tuples compare recursively. Equal-target roads use the
canonical edge key as a tiebreaker. Persistent road IDs are integers.

## Cost and verification

With ordered adjacency already available, BFS and iterative DFS take O(V+E)
time and O(V) auxiliary space, including their trees. Weak discovery and both
Kosaraju passes take O(V+E) time and O(V+E) space for temporary neighbor views.
Preparing canonical adjacency adds O(V log V + sum d log d) time and O(V+E)
storage. Prepare once when running several analyses. The page caps map layers
at 150 items. Full graph counts are independent of the display limit.

```python
from src.graph.dataset_service import load
from src.algorithms.reachability import find_unweighted_path

sample = load().graph
assert find_unweighted_path(sample, 0, 1).hop_count == 1
```

Offline tests compare BFS hop distances and component memberships with NetworkX,
inspect DFS finishing order, and exercise a chain beyond Python's recursion limit.
Use Graph Analytics to inspect a traversal tree or a hop-minimal path.
