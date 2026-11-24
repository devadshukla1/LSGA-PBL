"""Transfer detection, counting, instruction generation, and line-sequence validation utilities."""

from typing import Dict, List, Optional

from src.algorithms.routing_models import RouteSegment


def count_transfers(line_sequence: List[str]) -> int:
    """Computes the number of line transfers from an ordered sequence of line IDs.

    Rules:
    - If the sequence has 0 or 1 edge, transfers = 0 (first boarding is NOT a transfer).
    - A transfer occurs each time line_sequence[i] != line_sequence[i - 1].
    """
    if len(line_sequence) <= 1:
        return 0

    transfers = 0
    for i in range(1, len(line_sequence)):
        if line_sequence[i] != line_sequence[i - 1]:
            transfers += 1
    return transfers


def extract_transfer_stations(segments: List[RouteSegment]) -> List[Dict[str, str]]:
    """Extracts the interchange stations where a line change occurs.

    Returns a list of dicts:
    [
        {
            "station_id": "NDLS",
            "from_line_id": "YELLOW",
            "from_line_name": "Yellow Line",
            "to_line_id": "AIRPORT",
            "to_line_name": "Airport Express",
            "step_index": 3,
        },
        ...
    ]
    """
    if len(segments) <= 1:
        return []

    interchanges: List[Dict[str, str]] = []
    for i in range(1, len(segments)):
        prev_seg = segments[i - 1]
        curr_seg = segments[i]
        if curr_seg.line_id != prev_seg.line_id:
            interchanges.append({
                "station_id": curr_seg.source_station_id,
                "from_line_id": prev_seg.line_id,
                "from_line_name": prev_seg.line_name,
                "to_line_id": curr_seg.line_id,
                "to_line_name": curr_seg.line_name,
                "step_index": i,
            })
    return interchanges


def build_transfer_instructions(
    station_path: List[str],
    segments: List[RouteSegment],
    station_names: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Generates clear, passenger-facing step-by-step transit instructions.

    Example output:
    1. Board Yellow Line at Kashmere Gate towards Rajiv Chowk (5 stops).
    2. At Rajiv Chowk, transfer to Blue Line.
    3. Ride Blue Line towards Dwarka Sector 21 (12 stops).
    4. Alight at destination: Dwarka Sector 21.
    """
    if not station_path:
        return ["No route available."]

    station_names = station_names or {}

    def get_name(sid: str) -> str:
        return station_names.get(sid, sid)

    if len(station_path) == 1:
        sname = get_name(station_path[0])
        return [f"Origin and destination are the same station: {sname} ({station_path[0]}). No travel needed."]

    if not segments:
        return ["Direct route with no segments recorded."]

    instructions: List[str] = []

    # Group segments into contiguous line rides
    rides: List[Dict[str, any]] = []
    current_ride: Optional[Dict[str, any]] = None

    for seg in segments:
        if current_ride is None or current_ride["line_id"] != seg.line_id:
            if current_ride is not None:
                rides.append(current_ride)
            current_ride = {
                "line_id": seg.line_id,
                "line_name": seg.line_name,
                "board_station": seg.source_station_id,
                "alight_station": seg.destination_station_id,
                "stops": 1,
                "distance_km": seg.distance_km,
                "time_min": seg.estimated_time_min,
            }
        else:
            current_ride["alight_station"] = seg.destination_station_id
            current_ride["stops"] += 1
            current_ride["distance_km"] += seg.distance_km
            current_ride["time_min"] += seg.estimated_time_min

    if current_ride is not None:
        rides.append(current_ride)

    step_number = 1
    for idx, ride in enumerate(rides):
        board_name = get_name(ride["board_station"])
        alight_name = get_name(ride["alight_station"])
        line_name = ride["line_name"]
        stops = ride["stops"]
        stops_str = "1 stop" if stops == 1 else f"{stops} stops"
        time_str = f"{ride['time_min']:.1f} min"
        dist_str = f"{ride['distance_km']:.2f} km"

        if idx == 0:
            # First boarding
            instructions.append(
                f"{step_number}. Board **{line_name}** at **{board_name}** (`{ride['board_station']}`). "
                f"Ride {stops_str} ({dist_str}, ~{time_str}) to **{alight_name}**."
            )
            step_number += 1
        else:
            # Transfer
            prev_line = rides[idx - 1]["line_name"]
            instructions.append(
                f"{step_number}. At **{board_name}** (`{ride['board_station']}`), transfer from "
                f"**{prev_line}** to **{line_name}**."
            )
            step_number += 1
            instructions.append(
                f"{step_number}. Ride **{line_name}** {stops_str} ({dist_str}, ~{time_str}) to **{alight_name}**."
            )
            step_number += 1

    final_dest = get_name(station_path[-1])
    instructions.append(f"{step_number}. Alight at final destination: **{final_dest}** (`{station_path[-1]}`).")

    return instructions


def validate_line_sequence(segments: List[RouteSegment]) -> bool:
    """Verifies that consecutive segments form a topologically continuous path.

    Each segment's destination must match the next segment's source.
    """
    if len(segments) <= 1:
        return True

    for i in range(len(segments) - 1):
        if segments[i].destination_station_id != segments[i + 1].source_station_id:
            return False
    return True
