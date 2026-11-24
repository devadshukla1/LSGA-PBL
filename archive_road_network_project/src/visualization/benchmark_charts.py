"""Plotly performance visualizations for algorithm benchmarks."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DARK_LAYOUT = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#1f2937",
    font=dict(color="#f3f4f6", family="sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
)

ALGO_COLORS = {
    "dijkstra": "#38bdf8",  # Sky blue
    "astar": "#34d399",  # Emerald green
    "bidirectional_dijkstra": "#f59e0b",  # Amber
}


def chart_runtime_by_algorithm(summary_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart of mean runtime by algorithm across objectives."""
    if summary_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No benchmark data available", **DARK_LAYOUT)
        return fig

    fig = px.bar(
        summary_df,
        x="algorithm",
        y="mean_runtime_ms",
        color="algorithm",
        color_discrete_map=ALGO_COLORS,
        facet_col="objective" if "objective" in summary_df.columns else None,
        barmode="group",
        title="Mean Runtime by Routing Algorithm (ms)",
        labels={
            "mean_runtime_ms": "Mean Runtime (ms)",
            "algorithm": "Algorithm",
            "objective": "Objective",
        },
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def chart_runtime_vs_graph_size(summary_df: pd.DataFrame) -> go.Figure:
    """Generate line chart of runtime scaling vs actual node count."""
    if summary_df.empty or "node_count" not in summary_df.columns:
        fig = go.Figure()
        fig.update_layout(title="No graph scaling data available", **DARK_LAYOUT)
        return fig

    fig = px.line(
        summary_df,
        x="node_count",
        y="mean_runtime_ms",
        color="algorithm",
        color_discrete_map=ALGO_COLORS,
        markers=True,
        line_dash="objective" if "objective" in summary_df.columns else None,
        title="Empirical Runtime Scaling vs Graph Node Count",
        labels={
            "node_count": "Graph Node Count (|V|)",
            "mean_runtime_ms": "Mean Runtime (ms)",
            "algorithm": "Algorithm",
        },
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def chart_explored_nodes(summary_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart comparing mean explored nodes."""
    if summary_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No node expansion data available", **DARK_LAYOUT)
        return fig

    fig = px.bar(
        summary_df,
        x="algorithm",
        y="mean_nodes_expanded",
        color="algorithm",
        color_discrete_map=ALGO_COLORS,
        facet_col="objective" if "objective" in summary_df.columns else None,
        title="Search Space: Mean Explored Nodes",
        labels={
            "mean_nodes_expanded": "Nodes Expanded",
            "algorithm": "Algorithm",
            "objective": "Objective",
        },
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def chart_memory_by_algorithm(summary_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart of peak Python-tracked memory in MB."""
    if summary_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No memory data available", **DARK_LAYOUT)
        return fig

    fig = px.bar(
        summary_df,
        x="algorithm",
        y="mean_peak_memory_mb",
        color="algorithm",
        color_discrete_map=ALGO_COLORS,
        title="Memory Footprint: Peak Python-Tracked Allocations (MB)",
        labels={
            "mean_peak_memory_mb": "Peak Python Memory (MB)",
            "algorithm": "Algorithm",
        },
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def chart_runtime_distribution(raw_df: pd.DataFrame) -> go.Figure:
    """Generate box plot showing runtime distribution and variance."""
    timing_df = (
        raw_df[raw_df["measurement_mode"] == "timing"]
        if "measurement_mode" in raw_df.columns
        else raw_df
    )
    if timing_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No observation data available", **DARK_LAYOUT)
        return fig

    fig = px.box(
        timing_df,
        x="algorithm",
        y="runtime_ms",
        color="algorithm",
        color_discrete_map=ALGO_COLORS,
        points="all",
        title="Runtime Distribution and Dispersion (ms)",
        labels={
            "runtime_ms": "Runtime (ms)",
            "algorithm": "Algorithm",
        },
    )
    fig.update_layout(**DARK_LAYOUT)
    return fig


def chart_algorithm_speedup(comparison_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart of paired algorithm speedups relative to baseline."""
    if comparison_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No comparison data available", **DARK_LAYOUT)
        return fig

    fig = px.bar(
        comparison_df,
        x="candidate_algorithm",
        y="median_speedup",
        color="candidate_algorithm",
        color_discrete_map=ALGO_COLORS,
        facet_col="baseline_algorithm",
        title="Paired Speedup Ratios (Baseline Time / Candidate Time)",
        labels={
            "median_speedup": "Median Speedup (x)",
            "candidate_algorithm": "Candidate Algorithm",
            "baseline_algorithm": "Baseline",
        },
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="#9ca3af", annotation_text="Parity (1.0x)")
    fig.update_layout(**DARK_LAYOUT)
    return fig


def chart_correctness_summary(summary_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart displaying route validity and optimality rates."""
    if summary_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No correctness data available", **DARK_LAYOUT)
        return fig

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Route Validity Rate",
            x=summary_df["algorithm"],
            y=summary_df["route_validity_rate"] * 100,
            marker_color="#22c55e",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Optimality Verification Rate",
            x=summary_df["algorithm"],
            y=summary_df["optimality_verification_rate"] * 100,
            marker_color="#3b82f6",
        )
    )
    fig.update_layout(
        barmode="group",
        title="Correctness Verification: Route Validity & NetworkX Optimality Rate (%)",
        yaxis=dict(title="Percentage (%)", range=[0, 105]),
        **DARK_LAYOUT,
    )
    return fig
