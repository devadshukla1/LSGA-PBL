"""Before-and-after costs and feasibility of keeping the original route."""


def compare_simulation(baseline, scenario, effective) -> dict:
    before = baseline.total_travel_time_s
    after = scenario.total_travel_time_s if scenario else None
    bd = baseline.total_distance_m
    sd = scenario.total_distance_m if scenario else None
    feasible = (
        baseline.is_reachable
        and all(n in effective for n in baseline.node_path)
        and all(effective.has_edge(*edge) for edge in baseline.edge_path)
    )
    original_adjusted = (
        sum(effective.edges[e]["travel_time_s"] for e in baseline.edge_path) if feasible else None
    )
    union = set(baseline.edge_path) | set(scenario.edge_path if scenario else ())
    overlap = (
        (len(set(baseline.edge_path) & set(scenario.edge_path)) / len(union) if union else 1.0)
        if baseline.is_reachable and scenario and scenario.is_reachable
        else None
    )
    return dict(
        baseline_distance_m=bd,
        baseline_travel_time_s=before,
        scenario_distance_m=sd,
        scenario_travel_time_s=after,
        distance_difference_m=sd - bd if sd is not None and bd is not None else None,
        travel_time_difference_s=after - before
        if after is not None and before is not None
        else None,
        travel_time_change_percent=(after - before) / before * 100
        if before and after is not None
        else None,
        route_changed=baseline.edge_path != scenario.edge_path
        if scenario and baseline.is_reachable and scenario.is_reachable
        else None,
        baseline_reachable=baseline.is_reachable,
        scenario_reachable=bool(scenario and scenario.is_reachable),
        shared_edge_ratio=overlap,
        baseline_route_original_time=before,
        baseline_route_scenario_time=original_adjusted,
        rerouted_scenario_time=after,
        rerouting_time_saved=original_adjusted - after
        if original_adjusted is not None and after is not None
        else None,
    )
