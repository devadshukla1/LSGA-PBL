# Comprehensive Viva Voce Questions & Answers

**Project Title:** MetroGraph Analytics: Intelligent Metro Route Optimization and Critical Station Analysis Using Graph Algorithms  
**Target Level:** BCA / B.Tech / MCA Capstone Examination  
**Total Questions:** 42 Comprehensive Questions & Answers

---

### Part 1: Graph Theory Fundamentals & Modeling

**Q1: Why is a public transit metro network modeled as a graph?**  
**A:** A graph $G = (V, E)$ provides an intuitive and mathematically rigorous representation where vertices $V$ represent metro stations, and edges $E$ represent contiguous physical track segments connecting adjacent stations. This abstraction allows transit routing, topological connectivity, and network vulnerability to be analyzed using classical and modern graph algorithms.

**Q2: What is a MultiGraph, and why was it chosen over a simple graph for MetroGraph?**  
**A:** In a simple graph, at most one edge can connect any pair of nodes. In real metro systems, multiple distinct transit lines frequently operate concurrently along the same physical track segment between adjacent stations (e.g., Yellow and Airport Express sharing a corridor, or Blue Line branches). A `networkx.MultiGraph` allows parallel edges between the same two stations, preserving the unique identity, line ID, and attributes of each service.

**Q3: How are parallel multi-edges handled when calculating travel times or distances?**  
**A:** When performing single-objective routing on station nodes (like Dijkstra for minimum time), parallel edges between stations $u$ and $v$ are resolved deterministically by selecting the edge key with the minimum weight for that attribute (`min(edges.values(), key=lambda e: e[weight_key])`).

**Q4: What is the difference between a directed and an undirected graph in metro routing?**  
**A:** In standard subway networks, trains typically operate bidirectionally along twin parallel tracks. Unless express or one-way track constraints exist, modeling the network as an undirected graph accurately represents bidirectional travel while maintaining computational simplicity.

---

### Part 2: Routing Algorithms (BFS & Dijkstra)

**Q5: What is the primary objective of Breadth-First Search (BFS) in metro routing?**  
**A:** BFS finds the unweighted shortest path between source and destination, which directly minimizes the total number of intermediate station stops (hops), regardless of travel time or line transfers.

**Q6: What is the time and space complexity of BFS?**  
**A:** Time complexity is $\mathcal{O}(|V| + |E|)$ where $|E|$ counts all multi-edges. Space complexity is $\mathcal{O}(|V|)$ to maintain the FIFO queue, visited set, and predecessor reconstruction mapping.

**Q7: How does Dijkstra's algorithm differ from BFS?**  
**A:** While BFS assumes uniform unit edge weights, Dijkstra's algorithm accommodates non-uniform, non-negative edge weights (such as segment travel time in minutes or physical distance in kilometers), utilizing a min-priority queue (min-heap) to greedily settle nodes in ascending order of cumulative cost.

**Q8: What is the time complexity of Dijkstra's algorithm with a binary min-heap?**  
**A:** $\mathcal{O}((|V| + |E|) \log |V|)$, where extracting the minimum node takes $\mathcal{O}(\log |V|)$ and edge relaxation takes $\mathcal{O}(\log |V|)$.

**Q9: Why can Dijkstra's algorithm fail if negative edge weights are present?**  
**A:** Dijkstra's greedy invariant assumes that once a node is settled, its shortest path distance is finalized. A negative edge weight can retroactively yield a shorter path to an already settled node, violating the greedy invariant. MetroGraph explicitly validates and rejects negative weights during graph construction and routing.

---

### Part 3: Minimum Transfer Optimization (0-1 BFS & State Graphs)

**Q10: Why does minimum-stop routing often fail to provide the best passenger route?**  
**A:** BFS minimizes stops on station nodes without awareness of metro lines. A route with 10 stops requiring 3 line transfers is often far more exhausting and slower in practice than a single-line route with 11 stops, due to platform walking and waiting times.

**Q11: How is the routing state expanded to achieve line-aware routing?**  
**A:** Instead of routing solely over station nodes $u \in V$, the state space is expanded to tuples $(u, \ell) \in V \times L$, representing being physically present at station $u$ on metro line $\ell$. Transitions between adjacent stations on the same line cost 0 transfers, while changing lines at an interchange costs 1 transfer.

**Q12: How does 0-1 BFS work for transfer minimization?**  
**A:** In a graph where edge weights are restricted to $\{0, 1\}$, a double-ended queue (`collections.deque`) replaces the standard priority queue. When exploring neighbors:
- Edges of weight 0 (same line continuation) are pushed to the **front** of the deque.
- Edges of weight 1 (line change transfer) are pushed to the **back** of the deque.
This maintains monotonic cost ordering and achieves transfer minimization in linear time $\mathcal{O}(|L| \cdot (|V| + |E|))$.

**Q13: Why does the initial boarding cost zero transfers?**  
**A:** Boarding the first train at the origin station is a necessary trip prerequisite, not a transfer. Transfers are only counted when switching between distinct lines during the journey.

**Q14: What is Lexicographic Dijkstra?**  
**A:** Lexicographic Dijkstra optimizes multiple objectives sequentially using ordered tuples: $(\text{Transfers}, \text{Travel Time})$. The priority queue orders states primarily by minimum transfers; ties in transfer count are strictly broken by minimum travel time.

**Q15: What is Transfer-Aware Dijkstra?**  
**A:** Transfer-Aware Dijkstra models platform walking and waiting friction by adding an explicit penalty (e.g., 5.0 minutes) to the edge cost whenever a line change occurs. The objective minimizes:
$$\text{Total Cost} = \sum \text{Segment In-Transit Time} + (\text{Transfer Count} \times \text{Transfer Penalty})$$

---

### Part 4: Station Importance & Network Centrality

**Q16: What is Degree Centrality in transit networks?**  
**A:** Degree centrality measures the number of direct adjacent stations connected to a given station node, normalized by $|V| - 1$:
$$C_D(v) = \frac{\text{deg}(v)}{|V| - 1}$$
It identifies stations serving as local physical convergence points.

**Q17: Why must MultiGraphs be projected onto simple graphs before computing centrality?**  
**A:** Standard centrality formulas (like degree and betweenness) assume simple graph topologies. If two stations share 3 parallel lines, treating them as degree 3 would distort neighborhood connectivity. MetroGraph projects the MultiGraph onto an analytical simple graph where adjacent stations share exactly one edge.

**Q18: What is Betweenness Centrality, and what does it measure?**  
**A:** Betweenness centrality quantifies the fraction of all topological shortest paths in the network that pass through a given station:
$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
Stations with high betweenness act as crucial bridges connecting disparate sectors of the city.

**Q19: What algorithm is used to compute betweenness centrality?**  
**A:** Brandes' algorithm, which computes unweighted betweenness centrality across all node pairs in $\mathcal{O}(|V| \cdot |E|)$ time and $\mathcal{O}(|V| + |E|)$ space.

**Q20: What is an Articulation Point (Cut-Vertex)?**  
**A:** An articulation point is a vertex whose hypothetical removal strictly increases the number of connected components in the graph. In a transit system, an articulation station represents a single point of failure that splits the network into disconnected islands.

**Q21: Which algorithm detects articulation points?**  
**A:** Tarjan's Depth-First Search (DFS) algorithm using discovery times and low-link values in linear time $\mathcal{O}(|V| + |E|)$.

---

### Part 5: Station Closure & Network Resilience Simulation

**Q22: How does MetroGraph ensure that closure simulations do not corrupt the original graph?**  
**A:** All simulations strictly execute on a deep copy of the graph (`sim_graph = original_graph.copy()`). Node deletions and edge excisions occur exclusively on the isolated copy.

**Q23: What happens to track connections when a station is closed?**  
**A:** When station $v$ is excised (`sim_graph.remove_node(v)`), NetworkX automatically removes all multi-edges incident to $v$. Remaining tracks across the rest of the network remain completely intact.

**Q24: How is global network reachability quantified before and after a closure?**  
**A:** For a network segmented into $k$ connected components of sizes $n_1, n_2, \dots, n_k$, the total reachable station pairs is calculated using the combinatorial formula:
$$\text{Reachable Station Pairs} = \sum_{i=1}^k \frac{n_i(n_i - 1)}{2}$$
The reachability ratio is the reachable pairs divided by the maximum possible pairs $\frac{N(N-1)}{2}$ among the $N$ remaining active nodes.

**Q25: What disruption statuses can occur during detour rerouting?**  
**A:**
1. `ENDPOINT_CLOSED`: Origin or destination station was closed.
2. `ALREADY_UNREACHABLE`: Stations were disconnected prior to the outage.
3. `UNREACHABLE`: A route existed before, but closure severed all possible connections.
4. `UNCHANGED`: Optimal route did not traverse the closed station.
5. `REROUTED`: Original route intersected the closed station; a valid alternative detour was found.

---

### Part 6: System Design, Testing & Benchmarking

**Q26: Why does MetroGraph use Streamlit?**  
**A:** Streamlit enables rapid development of reactive, Python-native interactive web applications with built-in caching, session state management, and seamless Plotly integration without requiring JavaScript frameworks.

**Q27: How does Streamlit caching work in MetroGraph?**  
**A:** `@st.cache_data` caches serializable tabular data and analytics calculations, while `@st.cache_resource` caches the in-memory NetworkX MultiGraph keyed by dataset fingerprint.

**Q28: How does the application prevent stale results when the dataset is changed?**  
**A:** In `src/ui/session_state.py`, `invalidate_stale_results()` checks the active dataset fingerprint. If the fingerprint changes, all dependent session state variables (active route results, closure scenarios, comparisons) are reset to `None`.

**Q29: Why is Plotly used without OpenStreetMap (OSM) or Mapbox?**  
**A:** Plotly enables complete offline visualization using schematic coordinate systems. This eliminates dependencies on external tile servers, API rate limits, and internet connectivity, guaranteeing 100% offline reproducibility.

**Q30: How were benchmark measurements collected?**  
**A:** Using high-resolution Python timers (`time.perf_counter_ns()`) isolated strictly around algorithmic execution, utilizing 3 warm-up runs followed by 15–20 measured iterations to compute median, mean, and standard deviation.

---

### Part 7: Quick-Fire Technical Questions

**Q31: What is the average degree of a metro graph?**  
**A:** Typically between 2.0 and 2.5, characteristic of planar, sparse topological networks.

**Q32: Can degree centrality identify network bottlenecks?**  
**A:** No. A station can have degree 2 (two incident tracks) but bridge two huge suburban regions, giving it massive betweenness centrality despite low degree centrality.

**Q33: What is the Python version constraint for this project?**  
**A:** Python >= 3.11, < 3.13.

**Q34: What data formats are supported for exporting results?**  
**A:** CSV (tabular itineraries, metrics, rankings), JSON (structured route and simulation payloads), and GraphML (serialized graphs).

**Q35: What is GraphML?**  
**A:** An XML-based file format designed for serializing graphs along with node and edge attributes.

**Q36: What is the difference between travel time and modeled journey time?**  
**A:** Travel time represents pure in-transit physical movement between stations; modeled journey time includes transfer walking and platform waiting penalties.

**Q37: Why does closing Rajiv Chowk not partition the Delhi Metro into disjoint components?**  
**A:** The Delhi Metro features orbital ring lines (such as the Pink Line and Magenta Line) that provide topological mesh redundancy, allowing trains to route around the central core.

**Q38: What is an isolated station?**  
**A:** A vertex with degree 0 that has no surviving track connections to any other station.

**Q39: What testing frameworks were used?**  
**A:** `pytest` for unit, invariant, and integration testing, and `streamlit.testing.v1.AppTest` for headless UI testing.

**Q40: How many unit and integration tests are in the test suite?**  
**A:** Over 120 automated tests passing with 100% success rate.

**Q41: What tool is used for code formatting and static analysis?**  
**A:** Ruff, executing zero-error linting and formatting.

**Q42: What is the primary academic takeaway from this project?**  
**A:** Graph algorithms bridge theoretical computer science and urban infrastructure, demonstrating that line-aware state expansion and structural centrality modeling provide actionable commuter detours and vulnerability insights that unweighted station-hop models fail to capture.
