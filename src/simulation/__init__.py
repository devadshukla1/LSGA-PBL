"""Simulation package exports for Phase 6."""

from src.simulation.closure_engine import StationClosureError, simulate_station_closure
from src.simulation.connectivity_impact import compute_connectivity_metrics
from src.simulation.critical_station_impact import (
    compute_all_stations_impact_ranking,
    evaluate_single_station_impact,
)
from src.simulation.impact_comparison import build_impact_comparison_table
from src.simulation.models import (
    ClosureSimulationResult,
    ConnectivityMetrics,
    RouteRerouteResult,
)
from src.simulation.route_rerouting import calculate_route_with_objective, compare_routes_across_closure

__all__ = [
    "StationClosureError",
    "simulate_station_closure",
    "compute_connectivity_metrics",
    "build_impact_comparison_table",
    "calculate_route_with_objective",
    "compare_routes_across_closure",
    "evaluate_single_station_impact",
    "compute_all_stations_impact_ranking",
    "ClosureSimulationResult",
    "ConnectivityMetrics",
    "RouteRerouteResult",
]
