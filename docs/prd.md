# Product Requirements Document (PRD)

# Smart City Traffic & Emergency Route Optimizer

**Project ID:** SMARTROUTE-LSGA  
**Product Name:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Document Version:** 1.0  
**Project Type:** Academic Graph Analytics Application  
**Development Level:** Professional  
**Primary Focus:** Graph Algorithms, Network Analytics, and Performance Benchmarking  
**Target Platform:** Python-Based Streamlit Web Application  
**Deployment:** Local Windows and Streamlit Community Cloud  
**Primary User:** Student Developer / College Evaluator  
**Authentication / Payments:** None  
**Storage:** GraphML, JSON, CSV  
**Data Source:** OpenStreetMap via OSMnx  
**Traffic:** Deterministic simulation  
**Theme:** Dark professional analytics

## 1. Product Overview

SmartRoute Analytics is an interactive graph-analysis application for optimizing simulated emergency vehicle routes and evaluating the resilience of urban road networks. It models intersections and road endpoints as vertices, permitted road movements as directed edges, and road distance or estimated travel time as edge weights. It uses real OpenStreetMap topology, reproducible congestion scenarios, and road-closure simulations.

The application must answer: What is the shortest or fastest route? How do congestion and closures change it? Which junctions are structurally important? How do partitioning techniques describe large graphs? How do algorithms scale?

This is an educational analysis platform, **not** a live emergency dispatch or navigation service. All travel-time estimates and simulated traffic must be labeled accordingly.

## 2. Real-World Problem Statement

Emergency vehicles navigate roads affected by one-way restrictions, estimated speed, congestion, closures, and network connectivity. The geographically shortest route may not be the fastest, and a closed road may make a route impossible.

Represent the network as `G = (V, E)`, a directed weighted multigraph. Each road edge has `length_m`, `speed_kph`, `travel_time_s`, `congestion_factor`, and `is_closed`. Define:

- `travel_time_s = length_m / (speed_kph / 3.6)`
- `adjusted_time_s = travel_time_s * (1 + congestion_factor)` with nonnegative congestion factor.
- Closed edges are excluded from feasible routes.
- Fastest route minimizes the sum of adjusted traversal times; shortest-distance route minimizes the sum of lengths.

## 3. Target Audience

**Primary:** Student developer demonstrating graph algorithms, reproducible experiments, and real-world applications.  
**Secondary:** Faculty evaluator reviewing syllabus alignment, algorithm correctness, and benchmark evidence.

The application is single-user with no accounts, roles, collaboration, authentication, payments, or personal-data collection.

## 4. Academic Objectives and Syllabus Mapping

| Module | Required implementation | Evidence |
|---|---|---|
| 1. Introduction to Large-Scale Graphs | Directed weighted real road network, graph sizes and density, scalability | Dataset overview and scaling results |
| 2. Graph Representation and Storage | MultiDiGraph, adjacency list, small-subgraph adjacency matrix, GraphML, JSON, CSV | Representation explorer and serialization tests |
| 3. Graph Partitioning and Indexing | Geographic and graph-aware partitioning, edge cuts, balance, nearest-node spatial indexing | Partition maps and metrics |
| 4. Fundamental Graph Algorithms | BFS, DFS, Dijkstra, A*, bidirectional Dijkstra, alternative paths, connectivity, undirected MST | Routing tests and comparisons |
| 5. Graph Analytics | Degree, betweenness, closeness, PageRank, critical junctions, resilience | Rankings and disruption experiments |

Modules 6 (distributed processing), 7 (graph databases), and 8 (graph ML) are explicitly outside required scope. Do not introduce Spark, Giraph, Neo4j, graph embeddings, or GNNs.

BFS, DFS, Dijkstra, A*, and bidirectional Dijkstra must be implemented in project-owned Python code. NetworkX may be used for graph storage, reference validation, centrality, connectivity, MST, and alternative-path implementations. MST is computed only on a documented undirected projection, never presented as a valid directed emergency route. Centrality may be sampled on large graphs; sampling must be disclosed.

## 5. Core Functional Requirements

### FR-01 Road Network Dataset Management

Acquire drivable roads through OSMnx; preserve direction, parallel edges, geometry, length, class, and road attributes. Use documented deterministic speed estimates for missing values, derive traversal times, validate nonnegative finite weights, cache GraphML, and bundle a working offline graph. **Acceptance:** Loaded and restored graphs retain routing-relevant properties; one-way restrictions and unique edge keys survive; invalid data produces clear errors.

### FR-02 Graph Representation Explorer

Show node/edge counts, directedness, density, component statistics, adjacency-list samples, and a small-subgraph adjacency matrix. **Acceptance:** Values agree with the loaded graph, parallel edges and direction are correctly represented, and inspection does not mutate the dataset.

### FR-03 Emergency Route Optimization

Offer Dijkstra, A*, and bidirectional Dijkstra; choose source, destination, and objective (distance/time). Display route geometry, edge IDs, distance, estimated time, execution time, expanded/settled nodes, and validation. **Acceptance:** Routes respect one-way roads, closures, and parallel edges; edge-weight sums match reported cost; all three methods agree on optimal cost within tolerance; unreachable and same-node requests work.

### FR-04 Traversal and Reachability

Implement BFS and DFS manually, show bounded traversal output, evaluate directed reachability and strong/weak components. **Acceptance:** Results agree with reference methods; disconnected cases work; BFS is not described as a minimum-weight travel-time solver.

### FR-05 Traffic Congestion Simulation

Provide baseline, light, moderate, heavy, and heavy-with-closures scenarios with configurable severity and random seed. Apply nonnegative deterministic penalties only to scenario state. **Acceptance:** Same seed and parameters reproduce edge penalties, zero penalty reproduces baseline, original graph remains unchanged, and before/after route metrics are shown with simulation labels.

### FR-06 Road Closure and Rerouting

Allow edge and junction closures, predefined closure scenarios, restore-baseline action, rerouting, reachability reporting, and travel-time penalty. **Acceptance:** Closed roads and junctions cannot be traversed; baseline restore is exact; unreachable destinations are reported without failure.

### FR-07 Advanced Routing and Alternative Paths

Implement bidirectional Dijkstra and up to three K-shortest loopless route alternatives, ranked by chosen objective. **Acceptance:** Paths are valid, loopless, distinct, direction-aware, closure-aware, and edge-key-aware; no-route cases are handled.

### FR-08 Graph Analytics and Resilience

Compute degree, betweenness, closeness, and PageRank; visualize critical intersections; analyze strong/weak connectivity; compare equal-budget targeted and random junction failures; analyze MST on an undirected projection. **Acceptance:** Graph interpretation and sampling are documented, rankings reproduce, and disruption statistics are correct.

### FR-09 Partitioning and Spatial Indexing

Implement geographic and graph-aware partitioning, configurable partition count, node assignments, crossing-edge counts, cut ratios, imbalance, preprocessing time, map visualization, and nearest-node spatial indexing. **Acceptance:** Each node has exactly one partition, metrics match assignments, invalid inputs are rejected, and lookup yields a valid node. Do not claim partitioning speeds up routing without implementing and testing partition-aware routing.

### FR-10 Algorithm Benchmarking

Benchmark Dijkstra, A*, bidirectional Dijkstra, minimum-hop BFS separately, partitioning methods, and selected analytics. Measure runtime, mean/median/stddev/p95, peak memory, expanded nodes, route cost, correctness, speedup, and graph size. Run routing correctness, scalability, congestion sensitivity, closure resilience, and partition comparisons. **Acceptance:** Identical graph snapshots and source/destination pairs, fixed seeds, repeated trials, reference checks, CSV export, and clear failed-run records. Support at least 30 pairs per dataset and at least three timing repetitions; separate graph load and preprocessing from query timing. Never fabricate metrics.

## 6. Seven Dashboard Pages

1. **Overview:** Product intro, active dataset, graph statistics, road map, syllabus mapping.
2. **Route Optimizer:** Source/destination, algorithm and objective, route map, costs and runtime.
3. **Traffic Simulator:** Congestion scenario/severity/seed, road closures, before/after routing.
4. **Graph Analytics:** Centrality rankings, connectivity, targeted/random failures, MST experiment.
5. **Partitioning:** Method and partition count, colored map, edge-cut and balance metrics.
6. **Algorithm Lab:** Dataset/algorithm/seed/trials, experiment execution, runtime/memory/scalability/correctness charts.
7. **Results & Export:** Experiment tables, metadata, downloadable CSV and PNG charts.

No additional primary pages are authorized. Detailed navigation belongs in `app_flow.md`.

## 7. Key User Stories

- **US-01 Load network:** As a student, load cached real OSM roads or bundled offline data and inspect graph metadata.
- **US-02 Optimize route:** As a student, select source/destination and algorithm, then see a valid mapped route and cost metrics.
- **US-03 Compare algorithms:** As an evaluator, compare identical queries with reference-validated optimal costs and timing.
- **US-04 Simulate congestion:** As a student, modify scenario weights reproducibly and compare route changes.
- **US-05 Close roads:** As an evaluator, close edges/junctions and observe valid rerouting or an unreachable result.
- **US-06 Find critical junctions:** As a student, rank and visualize nodes, then test targeted failures.
- **US-07 Analyze partitions:** As a student, compare partition maps, balance, and edge cuts.
- **US-08 Reproduce benchmarks:** As an evaluator, run fixed-seed experiments and export documented measurements.
- **US-09 Demo offline:** As a student, demonstrate algorithms, simulations, and small-network analytics without internet.

Each story is accepted only when its corresponding FR acceptance criteria pass.

## 8. Data Requirements

Initial study area: Connaught Place and surrounding roads, New Delhi, India. The user can replace the dataset with another OSMnx-compatible road graph. Experimental targets: approximately 1K, 5K–10K, and 20K–50K vertices, dependent on available data and resources. Use GraphML for graph datasets, JSON for scenario and experiment configurations, CSV for measured results, and PNG for figures. Validate required attributes and edge identity; keep the base graph immutable during simulations.

## 9. Algorithm and Performance Requirements

Custom BFS, DFS, Dijkstra, A*, and bidirectional Dijkstra must not be wrappers around NetworkX path solvers. A* must use an admissible heuristic: geographic straight-line distance for distance optimization; distance divided by a valid maximum possible speed for time optimization; use zero heuristic when a safe bound is unavailable. Validate paths against trusted reference methods. Report algorithm runtime independently of data acquisition, graph loading, preprocessing, visualization, and export.

## 10. Non-Functional Requirements

- **Correctness:** Test edge cases, one-way rules, parallel edges, disconnected graphs, finite nonnegative weights, and numeric tolerances.
- **Reproducibility:** Record seeds, dataset metadata, graph snapshots, software versions, parameters, and hardware where available. Timing variation is expected.
- **Performance:** Cache read-only data; bound expensive analytics and visual rendering; run expensive tasks only on explicit action.
- **Reliability:** Handle absent files, offline operation, invalid graphs, unreachable routes, and failed experiments without corrupting saved results.
- **Usability:** Clear actions, progress indicators, helpful empty/error states, understandable charts.
- **Visual quality:** Dark professional analytics interface with accessible contrast, consistent layout, and clear baseline/simulation distinction. Exact tokens belong in `design_brief.md`.
- **Maintainability:** Separate graph, routing, analytics, simulation, benchmarks, and UI; use type hints, documented interfaces, pytest, and avoid circular imports.
- **Portability:** Local Windows and Streamlit Community Cloud; bundled offline sample works in cloud, with workload caps for constrained environments. No hard-coded absolute paths.
- **Security:** No credential collection, unrestricted filesystem operations, arbitrary code execution, or personal-data storage; validate imports and constrain file access.

## 11. Product Navigation

Exactly seven pages: Overview, Route Optimizer, Traffic Simulator, Graph Analytics, Partitioning, Algorithm Lab, Results & Export. Their exact paths and UI behavior must be specified consistently in `app_flow.md` and `trd.md`.

## 12. Success Metrics

- Seven pages operational and all ten FR groups implemented.
- Real OSM acquisition plus offline dataset work.
- Manual algorithms pass correctness and edge-case tests.
- Dijkstra, A*, and bidirectional Dijkstra agree on optimal route costs within tolerance.
- Congestion, closures, centrality, resilience, and partitioning yield reproducible valid results.
- At least three graph scales evaluated where hardware permits; 30 pairs per dataset and three timing repetitions supported.
- Real measured timing/memory/correctness exported with metadata; no invented observations.
- Modules 1–5 demonstrated through code, plots, and reproducible experiments.

## 13. Out of Scope (Do Not Build)

- Authentication, OAuth, accounts, roles, subscriptions, payments, billing, profiles.
- Live GPS, emergency dispatch, ambulance fleet management, traffic cameras, live traffic APIs, government service integration, signal control.
- GNNs, deep learning, LLM chatbots, reinforcement learning, computer vision, incident detection.
- Spark, GraphX, Giraph, Pregel deployment, Kubernetes, microservices, distributed databases.
- Mobile/native desktop apps, social features, notifications, messaging, admin portals, multi-tenancy, tracking, job queues, commercial navigation APIs.
- PostgreSQL, MySQL, MongoDB, Neo4j, Firebase, Supabase, Redis, or other database servers.

## 14. Mandatory Technology Constraints

Python, Streamlit, NetworkX, OSMnx, Plotly, Folium with streamlit-folium; GraphML/JSON/CSV storage; dark theme; local Windows plus Streamlit Community Cloud; no auth/payments/database server; manual core algorithms; verified measurements; syllabus Modules 1–5. Exact versions, paths, interfaces, and deployment config belong in `trd.md`.

## 15. Approved 12-Phase Roadmap

1. Project Foundation & Architecture
2. Real-World Road Network Acquisition
3. Fundamental Graph Traversal
4. Shortest Path Routing Engine
5. Advanced Routing Algorithms
6. Traffic Congestion & Emergency Simulation
7. Graph Analytics & Network Resilience
8. Graph Partitioning & Indexing
9. Benchmarking & Performance Analysis
10. Professional Streamlit Dashboard
11. Testing, Optimization & Quality Assurance
12. Documentation, Report & Final Demonstration

Exact small tasks and verification gates belong in `implementation_plan.md`.

## 16. Final Demonstration Scenario

1. Load a cached New Delhi road network and inspect statistics.
2. Select simulated ambulance source and emergency destination.
3. Compare Dijkstra and A* optimal costs, runtime, and explored nodes.
4. Apply seeded heavy congestion and compare estimated route times.
5. Close a road and demonstrate valid rerouting or unreachable handling.
6. Highlight centrality-ranked junctions and compare targeted/random disruptions.
7. Partition the graph, visualize regions, and compare cut/balance metrics.
8. Show measured, reproducible runtime, memory, correctness, and scalability results.
9. Export CSV results with experiment configuration and dataset metadata.

## 17. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| OSM download failure | Cached GraphML and bundled offline graph |
| Missing speed tags | Documented deterministic speed estimates |
| Expensive centrality | Sampling and bounded subgraph analysis |
| Incorrect A* heuristic | Admissibility tests and Dijkstra reference |
| Parallel-edge errors | Preserve edge keys end-to-end |
| Disconnected closures | Explicit unreachable state |
| Cloud resource limits | Small default dataset and bounded jobs |
| Variable timing | Environment metadata and repeated trials |
| UI freezes | Cache read-only data and explicit execution |
| Agent scope creep | Enforce PRD out-of-scope restrictions |

## 18. Definition of Done

All required features and seven pages function; real and offline data work; manual algorithms pass tests; simulations preserve the base graph; analytics and partitioning produce valid reproducible outputs; benchmarks contain genuine measurements and export correctly; Windows and Streamlit Community Cloud deployments are verified; README, syllabus mapping, project report, and viva demonstration are complete.

## 19. Rules for AI Coding Agents

1. Read this PRD and the other approved `/docs` specifications before editing code.
2. Follow `trd.md` for architecture, `app_flow.md` for navigation, `design_brief.md` for visual rules, `schema.md` for data contracts, and `implementation_plan.md` for task order.
3. Do not invent features or dependencies, replace required custom algorithms with wrappers, fabricate measurements, silently change objectives, or remove failing tests.
4. Inspect existing code before edits, preserve working modules, run relevant tests, and report changed files, test results, and limitations.
5. Stop at the assigned phase boundary and request clarification if approved documents conflict.

## 20. Product Acceptance Summary

**Product:** SmartRoute Analytics. **Purpose:** Real-world graph-analysis demonstration for emergency routing and network resilience. **Stack:** Python, Streamlit, NetworkX, OSMnx, Plotly, Folium. **Storage:** GraphML, JSON, CSV. **Audience:** Student and faculty evaluator. **Syllabus:** Modules 1–5. **Deployment:** Local Windows and Streamlit Community Cloud. **Acceptance:** Correct algorithms, reproducible measured experiments, usable visualizations, documented methodology, and a successful academic demo.

---

**End of PRD — Version 1.0**
