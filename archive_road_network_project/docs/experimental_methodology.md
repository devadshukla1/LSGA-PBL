# Experimental Methodology & Benchmarking Protocol

**Product:** SmartRoute Analytics  
**Academic Title:** Intelligent Emergency Vehicle Routing and Urban Road Network Resilience Analysis Using Large-Scale Graph Algorithms  
**Project Root:** `LSGA PBL`  

---

## 1. Experimental Objectives

The benchmarking framework implemented in SmartRoute Analytics provides a rigorous, statistically sound, and completely reproducible experimental testbed to evaluate the computational efficiency and path optimality of graph routing algorithms on urban street topologies.

The experiments address four central research questions:
1. **Computational Speedup:** What is the empirical runtime speedup achieved by goal-directed heuristic search (A*) and dual-frontier search (Bidirectional Dijkstra) compared to classic single-source Dijkstra?
2. **Search Space Reduction:** How effectively does the admissible Haversine heuristic reduce the number of explored vertices and examined edges during traversal?
3. **Optimality Invariance:** Do all three algorithms yield bit-for-bit identical path costs across arbitrary origin-destination pairs?
4. **Graph Scale Sensitivity:** How do runtime, peak memory footprint, and exploration frontiers scale as graph size expands from small synthetic grids ($N=10, 16$) to realistic urban metropolitan subnetworks ($N=500+$)?

---

## 2. Experimental Environment & System Specifications

All benchmark trials were executed under controlled local execution conditions:
- **Operating System:** Microsoft Windows 11 Home / Pro (64-bit)
- **Processor Architecture:** x86_64 Multi-Core CPU
- **Python Runtime:** Python 3.11.16 (`.venv`)
- **Core Libraries:** NetworkX 3.2.1, SciPy 1.12.0, NumPy 1.26.4
- **Execution Mode:** 100% Offline, Single-Threaded synchronous isolation (preventing OS multi-threading scheduling jitter).

---

## 3. Dataset Configurations & Graph Scales

Experiments evaluated both structured planar synthetic networks and real-world urban street networks:
1. **`offline_sample_n10`:** Synthetic $N=10$ planar directed grid.
2. **`offline_sample_full`:** Synthetic $N=16$ directed $4 \times 4$ grid ($|V|=16, |E|=34$).
3. **`synthetic_n100`:** $N=100$ planar street network ($|V|=100, |E|=260$).
4. **`chandigarh_core`:** Extracted OpenStreetMap drivable road network of Chandigarh, India.

---

## 4. Query Generation & Seed-Locked Determinism

To ensure fair comparisons across algorithms, test query sets are generated systematically:
1. **Deterministic Pseudorandom Generation:** Source-target pairs $(s, t)$ are generated using `numpy.random.default_rng(seed=42)`.
2. **Directed Reachability Filter:** Only pairs $(s, t)$ with confirmed directed reachability in the network's giant strongly connected component are included ($s \ne t$).
3. **Fixed Seed Protocol:** The exact same sequence of queries is supplied to all competing algorithms in identical order.

---

## 5. Measurement Instrumentation Protocol

### 5.1 Runtime Latency
- Measured using `time.perf_counter_ns()` with nanosecond precision, converted to milliseconds (ms).
- **Warmup Phase:** A preliminary query is executed before timing to prime Python's JIT bytecode caches, CPU branch predictors, and heap structures.
- **Trial Repetition:** Each query is executed across 3 repeated runs. The mean, median, min, max, and $95^{\text{th}}$ percentile (p95) runtimes are computed.

### 5.2 Memory Tracking
- Instrumented using Python's native `tracemalloc` library.
- Measures the **peak allocation delta** ($\Delta \text{RAM}$ in megabytes) consumed by search queues, distance maps, and frontier sets during the execution lifecycle.

### 5.3 Algorithmic Exploration Counters
- **Nodes Expanded / Settled:** The exact number of vertices popped from the priority queue and permanently labeled.
- **Edges Examined / Relaxed:** The total number of directed incident out-edges $(u, v, k)$ evaluated for possible distance relaxation.

### 5.4 Correctness & Optimality Verification
- For every query, the computed path cost $C_{\text{algo}}$ is compared directly against the reference cost computed by `networkx.shortest_path_length`:
  $$\text{Optimality Verification Rate} = \frac{\sum \mathbb{I}(|C_{\text{algo}} - C_{\text{NX}}| < 10^{-6})}{N_{\text{queries}}}$$
  A trial is valid if and only if:
  1. The returned path is continuous and loopless: $\forall i, (v_i, v_{i+1}, k_i) \in E$.
  2. The sum of edge attributes matches the reported total cost.
  3. The cost matches NetworkX ground truth (100% verification rate required).

---

## 6. Statistical Aggregation Metrics

The benchmark pipeline computes the following summary statistics:
- **Mean ($\mu$):** Arithmetic average runtime.
- **Median ($M$):** $50^{\text{th}}$ percentile, robust against OS background interruptions.
- **Standard Deviation ($\sigma$):** Dispersion of execution times across repetitions.
- **$95^{\text{th}}$ Percentile (p95):** Worst-case upper bound latency for mission-critical emergency routing SLAs.
- **Speedup Factor:** Ratio of baseline Dijkstra runtime to the candidate algorithm runtime:
  $$S_{\text{algo}} = \frac{\text{Runtime}_{\text{Dijkstra}}}{\text{Runtime}_{\text{algo}}}$$
