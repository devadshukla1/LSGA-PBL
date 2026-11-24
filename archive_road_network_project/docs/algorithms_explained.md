# Graph Algorithms: Design, Mechanics & Implementation

**Product:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Project Root:** `LSGA PBL`  

---

## 1. Fundamental Graph Traversals: BFS and DFS

### 1.1 Breadth-First Search (BFS)
- **Mathematical Purpose:** Computes unweighted topological hop-distance from source vertex $v_s$ to all reachable vertices, producing a minimal-hop spanning tree.
- **Data Structure:** FIFO Queue (`collections.deque`), Visited Set (`set`), Distance Map (`dict`), Parent Map (`dict`).
- **Mechanics:** Explores nodes layer-by-layer (frontier expansion). Node $u$ is enqueued once. When $u$ is dequeued, all unvisited out-neighbors $v$ along directed edges $(u, v, k)$ are marked visited and enqueued at hop level $d(v) = d(u) + 1$.
- **Pseudocode:**
  ```text
  Algorithm BreadthFirstSearch(G, source)
      Input: Directed Graph G = (V, E), source node s
      Output: Distances d, Parent map pi, Traversal order
      
      queue <- FIFOQueue()
      visited <- {s}
      d[s] <- 0
      pi[s] <- None
      order <- []
      queue.push(s)
      
      while queue is not empty do
          u <- queue.pop()
          order.append(u)
          for each neighbor v in G.neighbors(u) do
              if v not in visited then
                  visited.add(v)
                  d[v] <- d[u] + 1
                  pi[v] <- u
                  queue.push(v)
      return (d, pi, order)
  ```
- **Application in Project:** Reachability verification, topological layer analysis, and seeding balanced regions in graph-aware partitioning.

---

### 1.2 Depth-First Search (DFS)
- **Mathematical Purpose:** Explores graph connectivity deeply along each branch before backtracking; records discovery time $d[u]$ and finish time $f[u]$; detects directed cycle back-edges.
- **Data Structure:** LIFO Stack (explicit or recursive call stack), Visited State Map (`UNVISITED`, `VISITING`, `VISITED`), Predecessor Map (`dict`).
- **Mechanics:** An edge $(u, v, k)$ encountering a node in `VISITING` state represents a directed cycle (back-edge), crucial for detecting circular routes in urban traffic.
- **Pseudocode:**
  ```text
  Algorithm DepthFirstSearch(G, source)
      Input: Directed Graph G = (V, E), source node s
      Output: Discovery times d, Finish times f, Predecessor map pi, Cycles
      
      time <- 0
      state <- {v: UNVISITED for v in V}
      d <- {}, f <- {}, pi <- {s: None}
      cycles <- []
      
      function DFSVisit(u)
          time <- time + 1
          d[u] <- time
          state[u] <- VISITING
          for each neighbor v in G.neighbors(u) do
              if state[v] == UNVISITED then
                  pi[v] <- u
                  DFSVisit(v)
              else if state[v] == VISITING then
                  cycles.append((u, v))  // Back-edge detected
          state[u] <- VISITED
          time <- time + 1
          f[u] <- time
          
      DFSVisit(s)
      return (d, f, pi, cycles)
  ```
- **Application in Project:** Path component depth exploration, topology structure analysis, and cycle detection.

---

## 2. Shortest Path Routing Algorithms

### 2.1 Dijkstra's Algorithm
- **Mathematical Principle:** Greedy label-setting algorithm computing exact single-source shortest paths on graphs with strictly non-negative edge weights $w(e) \ge 0$.
- **Data Structures:** Min-Heap Priority Queue (`heapq`), Distance Map $d[v]$, Predecessor Map $\pi[v]$, Visited/Settled Set $S$.
- **Mechanics:** 
  Maintains invariant: For every settled vertex $u \in S$, $d[u]$ is the absolute shortest path distance from $s$. Relaxes outgoing directed edges $(u, v, k)$:
  $$\text{if } d[u] + w(u, v, k) < d[v] \implies d[v] \leftarrow d[u] + w(u, v, k), \quad \pi[v] \leftarrow (u, k)$$
- **Pseudocode:**
  ```text
  Algorithm Dijkstra(G, source, target, weight_attr)
      Input: MultiDiGraph G = (V, E), source s, target t, edge weight function w
      Output: Shortest distance, node path, edge keys, explored count
      
      dist <- {v: infinity for v in V}
      dist[s] <- 0
      pi <- {}
      pq <- MinHeap([(0, s)])
      settled <- set()
      explored_count <- 0
      
      while pq is not empty do
          (cost, u) <- pq.pop()
          if u in settled then continue
          settled.add(u)
          explored_count <- explored_count + 1
          
          if u == target then break
          
          for each edge (u, v, k) in G.out_edges(u, keys=True) do
              weight <- G[u][v][k][weight_attr]
              new_cost <- cost + weight
              if new_cost < dist[v] then
                  dist[v] <- new_cost
                  pi[v] <- (u, k)
                  pq.push((new_cost, v))
                  
      reconstruct path from pi ending at target
      return (dist[t], path, edge_keys, explored_count)
  ```

---

### 2.2 A* Search Algorithm
- **Mathematical Principle:** Heuristic-driven shortest-path search that guides search frontier expansion toward target $t$ by minimizing the evaluation function:
  $$f(u) = g(u) + h(u)$$
  where $g(u)$ is the exact known cost from $s$ to $u$, and $h(u)$ is an admissible, monotonic lower-bound heuristic to $t$.
- **Heuristic Choice:** Spherical Haversine distance $D_{\text{hav}}(u, t)$ for distance minimization; $D_{\text{hav}}(u, t) / v_{\max}$ for travel time minimization.
- **Mechanics:** Prioritizes nodes in the open set by $f(u)$. Consistency guarantees that vertices are settled at most once and the first settlement of target $t$ is optimal.
- **Pseudocode:**
  ```text
  Algorithm AStar(G, source, target, weight_attr, heuristic_fn)
      Input: MultiDiGraph G, source s, target t, weight attr w, heuristic h
      Output: Optimal cost, path, edge keys, explored count
      
      g_score <- {v: infinity for v in V}; g_score[s] <- 0
      f_score <- {v: infinity for v in V}; f_score[s] <- h(s, t)
      pi <- {}
      pq <- MinHeap([(f_score[s], 0, s)])
      closed_set <- set()
      explored_count <- 0
      
      while pq is not empty do
          (f, g, u) <- pq.pop()
          if u in closed_set then continue
          closed_set.add(u)
          explored_count <- explored_count + 1
          
          if u == target then break
          
          for each edge (u, v, k) in G.out_edges(u, keys=True) do
              weight <- G[u][v][k][weight_attr]
              tentative_g <- g + weight
              if tentative_g < g_score[v] then
                  g_score[v] <- tentative_g
                  f_score[v] <- tentative_g + h(v, t)
                  pi[v] <- (u, k)
                  pq.push((f_score[v], tentative_g, v))
                  
      reconstruct path from pi
      return (g_score[t], path, edge_keys, explored_count)
  ```

---

### 2.3 Bidirectional Dijkstra Algorithm
- **Mathematical Principle:** Executes two concurrent searches: a forward Dijkstra search starting at source $s$ on $G$, and a backward Dijkstra search starting at target $t$ on the reversed graph $G^{\text{rev}}$.
- **Meeting & Termination Condition:** 
  Maintains the best path cost $\mu$ discovered so far:
  $$\mu = \min_{u \in V} \Big(d_f[u] + d_b[u]\Big)$$
  Search terminates as soon as the top values of both min-heaps satisfy:
  $$\min(d_f) + \min(d_b) \ge \mu$$
  This condition guarantees that no unexplored path through any frontier can have a cost strictly less than $\mu$.
- **Directed Path Reconstruction:** Reconstructs the forward path segment $s \leadsto u^*$ using $\pi_f$, and the backward segment $u^* \leadsto t$ using $\pi_b$ reversed along correct directed edge keys.

---

## 3. Advanced Alternative Routing: Yen's K-Shortest Paths

- **Mathematical Principle:** Computes the $1^{\text{st}}, 2^{\text{nd}}, \dots, K^{\text{th}}$ shortest simple (loopless) paths between $s$ and $t$.
- **Spur & Root Decomposition:** For $k^{\text{th}}$ path calculation, uses $(k-1)^{\text{th}}$ path $P_{k-1}$. Iterates over all intermediate spur nodes $v_i \in P_{k-1}$:
  1. **Root Path:** $R = P_{k-1}[0 \dots i]$ (fixed prefix).
  2. **Edge Invalidation:** Temporarily removes outgoing edges from $v_i$ that share the same edge key as existing paths $P_1, \dots, P_{k-1}$ sharing root $R$.
  3. **Node Invalidation:** Temporarily excludes intermediate nodes in $R$ (except $v_i$) from $G$ to prevent cycles.
  4. **Spur Path:** Computes shortest path from $v_i$ to $t$ on the modified graph using Dijkstra.
  5. **Candidate Assembly:** Concat $R$ and spur path; insert into candidate min-heap $B$.
  6. **Path Selection:** Select lowest cost candidate from $B$ as $P_k$.
- **Handling MultiDiGraph Edges:** Properly indexes parallel edge keys $k$ during edge exclusion, enabling distinct alternative routes over multi-lane corridors.

---

## 4. Graph Partitioning Mechanics

### 4.1 Recursive Geographic Bisection
- Slices the geographic bounding box of node positions along the coordinate median:
  $$\text{Axis } = \begin{cases} \text{latitude} & \text{if } \text{depth is even} \\ \text{longitude} & \text{if } \text{depth is odd} \end{cases}$$
- Partitions nodes into two balanced subsets at each recursive step until $K$ spatial cells are produced.

### 4.2 Graph-Aware Region Growing
- Selects $K$ geographically dispersed seed vertices $s_1, \dots, s_K$.
- Executes synchronized Breadth-First Search expansions from all $K$ seeds simultaneously.
- Vertices are greedily claimed by the closest expanding cluster frontier, enforcing continuous, topological road neighborhood cohesion.
- Computes **Cut-Edge Ratio** and **Balance Ratio**:
  $$\text{Cut-Edge Ratio} = \frac{\big|\{(u, v, k) \in E \mid \text{part}(u) \ne \text{part}(v)\}\big|}{|E|}$$
  $$\text{Balance Ratio} = \frac{\max_{p} |V_p|}{|V| / K}$$
