# System Architecture & Technical Specification

## 1. High-Level Architecture Overview

**MetroGraph Analytics** is built on a modular, decoupled Python architecture where graph-theoretic calculation engines operate independently of the presentation and visualization layers.

```mermaid
flowchart TD
    subgraph Data Layer
        A1[data/sample: 12 Stations] --> B[Data Loader & Schema Validator]
        A2[data/metro: 260 Delhi Stations] --> B
        B --> C[Graph Builder: NetworkX MultiGraph]
    end

    subgraph Core Algorithm Layer
        C --> D1[BFS Router: Min Stops]
        C --> D2[Dijkstra Router: Min Time/Dist]
        C --> D3[Line-Aware 0-1 BFS: Min Transfers]
        C --> D4[Lexicographic Dijkstra]
        C --> D5[Transfer-Aware Dijkstra: Friction Penalty]
        C --> E[Graph Projector: Simple Weighted Graph]
        E --> F1[Degree Centrality Engine]
        E --> F2[Betweenness Centrality: Brandes]
        E --> F3[Tarjan DFS Cut-Vertices: Articulation Points]
    end

    subgraph Resilience Layer
        C --> G[Station Closure Simulator: Isolated Graph Copy]
        G --> H1[Node & Edge Excision Engine]
        G --> H2[Pairwise Reachability: Sum n_i*n_i-1/2]
        G --> H3[Commuter Detour Rerouting Engine]
    end

    subgraph Presentation & UI Layer
        D1 & D2 & D3 & D4 & D5 --> UI[Streamlit Multipage Interface: app.py & pages/]
        F1 & F2 & F3 --> UI
        H1 & H2 & H3 --> UI
        UI --> V1[Offline Plotly Schematic Network Maps]
        UI --> V2[Artifact Exporters: CSV & JSON]
    end
```

---

## 2. Component Descriptions

### A. Data Layer (`src/data/`, `src/graph/`)
- **Loader & Validator:** Verifies CSV relational integrity across stations, lines, connections, and memberships.
- **Metro Builder:** Generates an undirected `networkx.MultiGraph` preserving parallel line operations along shared physical track corridors.

### B. Routing Engines (`src/algorithms/`)
- **BFS:** Explores station nodes level-by-level in $\mathcal{O}(|V| + |E|)$.
- **Dijkstra:** Priority-queue based path cost minimization in $\mathcal{O}((|V| + |E|) \log |V|)$.
- **Line-Aware State Graph:** Expands states to $(u, \ell) \in V \times L$ where track hops cost 0 and line switches cost 1. Solved via deque-based 0-1 BFS in $\mathcal{O}(|L| \cdot (|V| + |E|))$.

### C. Structural Analytics (`src/analytics/`)
- Projects the MultiGraph onto a simple graph where parallel edges collapse into minimum physical travel times.
- Evaluates degree centrality, Brandes unweighted betweenness centrality ($\mathcal{O}(|V||E|)$), and Tarjan DFS cut-vertices ($\mathcal{O}(|V| + |E|)$).

### D. Simulation Engine (`src/simulation/`)
- Guarantees complete immutability via `graph.copy()`.
- Calculates post-outage connected component partitions and computes global reachable pairs $\sum \frac{n_i(n_i-1)}{2}$.
