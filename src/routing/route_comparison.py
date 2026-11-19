"""Cost differences and exact edge-set Jaccard overlap."""


def compare_routes(routes) -> list[dict]:
    if not routes:
        return []
    best = routes[0]
    base = set(best.edge_path)
    rows = []
    for index, route in enumerate(routes, 1):
        edges = set(route.edge_path)
        union = base | edges
        overlap = len(base & edges) / len(union) if union else 1.0
        delta = route.optimized_cost - best.optimized_cost
        rows.append(
            {
                "Rank": index,
                "Distance (km)": route.total_distance_m / 1000,
                "Estimated Time (min)": route.total_travel_time_s / 60,
                "Optimized Cost": route.optimized_cost,
                "Cost Difference": delta,
                "Cost Increase (%)": delta / best.optimized_cost * 100
                if best.optimized_cost
                else None,
                "Hop Count": len(route.edge_path),
                "Shared-Edge Ratio": overlap,
                "Diversity": 1 - overlap,
            }
        )
    return rows
