# Known System Limitations & Architectural Disclosures

**Product:** SmartRoute Analytics  
**Academic Subject:** Large-Scale Graph Analysis  
**Phase:** 11 of 12 — Testing, Optimization & Quality Assurance  
**Date:** 2026-11-19  

---

## 1. Real-Time Data & External Integration Disclosures

1. **Synthetic Traffic Assumptions:**
   - Congestion levels (*Normal*, *Light*, *Moderate*, *Heavy*) apply fixed multiplier ranges to speed and travel times ($1.0\times$ to $2.5\times$).
   - The application does not connect to live sensor feeds, inductive loop detectors, or external traffic APIs (e.g., Google Maps Traffic, TomTom).
   - Speed values represent synthetic assumptions derived from OpenStreetMap road highway classifications, not real-time telemetry.

2. **Emergency Dispatch Boundaries:**
   - The system models shortest travel time pathing and road blockages for demonstration and research purposes.
   - It is not an industrial Computer-Aided Dispatch (CAD) system and does not account for traffic signals, turning radius constraints, vehicle dimensions, or dynamic sirens.

---

## 2. Road Network Acquisition & Offline Operation

3. **OpenStreetMap Acquisition & Caching:**
   - Acquiring new geographic road graphs depends on an active internet connection to the OpenStreetMap Overpass API via OSMnx.
   - Offline demonstration relies strictly on pre-validated bundled datasets (`data/samples/offline_sample.graphml`).
   - If internet access is unavailable during a live demonstration, the evaluator must use the offline sample.

4. **Map Tile Rendering Offline:**
   - Interactive Folium web maps render road geometries and marker overlays cleanly offline.
   - However, background raster map tiles (OpenStreetMap tiles) will not render when disconnected from the internet. The dashboard provides a high-contrast vector fallback for offline inspection.

---

## 3. Algorithm Approximations & Computational Complexity

5. **Betweenness Centrality Scaling:**
   - Exact betweenness centrality on directed graphs requires $O(V \cdot E)$ operations using Brandes' algorithm.
   - On graphs where $|V| > 500$, the system automatically switches to random pivot sampling ($k = \min(50, |V|)$) to prevent dashboard freezes. This provides a statistically sound approximation but not exact scores.

6. **Graph-Aware Partitioning Heuristics:**
   - Finding the exact minimum-cut graph partition with balanced sizes is NP-hard.
   - The implemented graph-aware partitioner employs greedy boundary expansion with local refinement. While it significantly reduces cut edges compared to raw coordinate splits, it is not guaranteed to find the globally optimal cut.

7. **Minimum Spanning Forest Undirected Projection:**
   - Minimum spanning trees are mathematically defined on undirected graphs.
   - Road networks are directed multigraphs with one-way streets. The MST module evaluates connectivity via an explicit undirected projection (taking the minimum-cost edge between unordered pairs). A minimum spanning tree is an infrastructure connectivity analysis tool, **not a drivable emergency route**.

---

## 4. Benchmarking & Resource Profiling Disclosures

8. **Runtime Measurement Hardware Dependency:**
   - Algorithm execution times measured via `time.perf_counter_ns` vary across CPU architectures, thermal throttling, and operating system process scheduling.
   - Algorithmic comparison ratios (e.g., A* node expansion speedup over Dijkstra) are algorithmically invariant, but absolute latencies are hardware-specific.

9. **Python Memory Profiling Scope:**
   - Peak memory profiling is measured using Python's standard `tracemalloc` module.
   - `tracemalloc` tracks memory blocks allocated directly by Python's memory manager. It does not measure underlying C-level memory allocated by third-party C-extensions, OS-level page faults, or shared library overhead.
