# Traffic congestion simulation

Phase 6 covers Modules 1 and 4 through reproducible disruptions and weighted
rerouting. The baseline remains immutable. Each explicit run builds a deep
scenario copy, costing O(V+E) additional storage plus copied attributes. It
preserves baseline times in base_travel_time_s, exposes effective times in
effective_travel_time_s and binds travel_time_s to that effective value for
the existing routing algorithms and validators.

Normal traffic multiplies time by one. Illustrative ranges are light 1.15–1.35,
moderate 1.40–1.80 and heavy 1.90–2.80. Coverage selects floor(E*coverage) edges
using a local seeded generator and canonical edge ordering. Congestion changes
time while preserving distance and geometry. Exact keyed closures remove only
the selected directed road. Blocked intersections remove the node and every
incident edge. Blocked endpoints return a dedicated status.

Emergency mode requests the simulated travel-time objective. These are assumed
traffic conditions and model estimates. Actual emergency response prediction
and live measurements are outside this simulation.

Comparison records both optimal routes, distance/time differences and edge-set
overlap. It also evaluates the original route under scenario weights when
every road and node remains available. Rerouting benefit subtracts the new
route time from that feasible original-route time. Undefined metrics use null,
including percentages against zero baseline time.

Scenarios persist as JSON with integer road IDs, configuration, seed, schema
and a SHA-256 dataset fingerprint. Stable identity excludes creation time and
display name. Loading against a changed graph is rejected. Atomic writes avoid
partial JSON. Reproduction requires the same dataset and software versions.
Scenario input is independent of Streamlit.

Run python scripts/verify_simulation.py for normal and three congestion levels,
NetworkX cost checks, closure rerouting, blocked endpoints and immutability.
Tests additionally exercise persistence and malformed configurations.

On the offline sample, closing (0,1,7) changes the fastest route from that
10.08-second edge to (0,1,0), which takes 14.4 seconds.

```python
from src.graph.dataset_service import load
from src.simulation.scenario_builder import create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.simulation_engine import simulate

graph = load().graph
scenario = create_scenario(graph, "offline_sample", "heavy", seed=42)
result = simulate(graph, scenario, SimulationRequest(0, 1))
```
