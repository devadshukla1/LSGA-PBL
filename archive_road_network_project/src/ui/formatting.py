"""Consistent metric formatting utilities for distances, durations, and memory."""


def format_distance(meters: int | float) -> str:
    """Format road distance in meters or kilometers with unit notation."""
    if meters < 0:
        return "0 m"
    if meters < 1000.0:
        return f"{meters:,.1f} m"
    km = meters / 1000.0
    return f"{km:,.2f} km"


def format_time(seconds: int | float) -> str:
    """Format travel time duration into human-readable seconds or minutes."""
    if seconds < 0:
        return "0 s"
    if seconds < 60.0:
        return f"{seconds:.1f} s"
    minutes = int(seconds // 60)
    rem_sec = seconds % 60
    if minutes < 60:
        return f"{minutes} min {rem_sec:.0f} s" if rem_sec >= 1.0 else f"{minutes} min"
    hours = minutes // 60
    rem_min = minutes % 60
    return f"{hours} h {rem_min} min"


def format_runtime(seconds: int | float) -> str:
    """Format algorithm execution runtime with appropriate scale (us, ms, s)."""
    if seconds < 0:
        return "0.00 ms"
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f} µs"
    if seconds < 1.0:
        return f"{seconds * 1000.0:.2f} ms"
    return f"{seconds:.4f} s"


def format_memory(value_mb: int | float) -> str:
    """Format memory consumption in megabytes or kilobytes."""
    if value_mb < 0:
        return "0.00 MB"
    if value_mb < 0.1:
        return f"{value_mb * 1024.0:.1f} KB"
    return f"{value_mb:.2f} MB"


def format_percentage(ratio: int | float, decimals: int = 1) -> str:
    """Format fractional ratio [0.0, 1.0] as formatted percentage string."""
    pct = max(0.0, float(ratio)) * 100.0
    return f"{pct:.{decimals}f}%"
