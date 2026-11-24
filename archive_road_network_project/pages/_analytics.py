"""Explicit-run structural analytics controls."""

from dataclasses import asdict

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.analytics.centrality import centrality
from src.analytics.connectivity import connectivity_summary
from src.analytics.critical_nodes import critical_nodes
from src.analytics.failure_scenarios import failure_scenario
from src.analytics.mst import minimum_spanning_forest
from src.analytics.resilience import resilience_experiment
from src.graph.dataset_service import list_datasets, load
from src.visualization.analytics_maps import analytics_map


def structural_analytics():
    st.subheader("Network Analytics & Resilience")
    with st.form("structural"):
        dataset = st.selectbox("Analytics dataset", list_datasets())
        task = st.selectbox(
            "Analysis",
            ["Centrality", "Critical intersections", "Network resilience", "Spanning forest"],
        )
        metric = st.selectbox(
            "Centrality metric",
            ["degree", "in_degree", "out_degree", "betweenness", "closeness", "pagerank"],
        )
        objective = st.selectbox("Analytics objective", ["distance", "travel_time"])
        direction = st.selectbox("Closeness direction", ["incoming", "outgoing"])
        strategy = st.selectbox("Targeted failure strategy", ["degree", "betweenness", "combined"])
        percentage = st.slider("Maximum failed junctions (%)", 0, 100, 20)
        repetitions = st.number_input("Random repetitions", 2, 30, 10)
        seed = st.number_input("Analytics seed", value=42, step=1)
        run = st.form_submit_button("Run Analysis")
    if run:
        st.session_state.pop("structural_output", None)
        try:
            with st.spinner("Analyzing road structure"):
                graph = load(dataset).graph
                summary = asdict(connectivity_summary(graph))
                details = {}
                scores = {}
                failed = ()
                forest_edges = ()
                chart = None
                if task == "Centrality":
                    result = centrality(graph, metric, objective, direction, seed=int(seed))
                    scores = result.scores
                    table = [{"node": n, "score": scores[n]} for n in result.top_nodes[:30]]
                    details = {
                        "approximate": result.approximate,
                        "parameters": result.parameters,
                        "runtime_seconds": result.runtime_seconds,
                    }
                elif task == "Critical intersections" or (
                    task == "Network resilience" and strategy == "combined"
                ):
                    metrics = {
                        name: centrality(graph, name, objective, direction, seed=int(seed))
                        for name in ("degree", "betweenness", "closeness", "pagerank")
                    }
                    table = critical_nodes(graph, metrics, top_k=len(graph))
                    scores = {row["node_id"]: row["combined_score"] for row in table}
                    details = {
                        "combined_weights": dict(
                            betweenness=0.4, degree=0.25, closeness=0.2, pagerank=0.15
                        ),
                        "betweenness_approximate": metrics["betweenness"].approximate,
                    }
                    table = table[:10]
                if task == "Network resilience":
                    if strategy != "combined":
                        result = centrality(graph, strategy, objective, seed=int(seed))
                        scores = result.scores
                    table = resilience_experiment(
                        graph,
                        scores,
                        strategy,
                        levels=tuple(percentage / 100 * i / 4 for i in range(5)),
                        seed=int(seed),
                        repetitions=int(repetitions),
                    )
                    failed = failure_scenario(
                        graph, int(len(graph) * percentage / 100), strategy, scores
                    ).removed_nodes
                    chart = pd.DataFrame(table).set_index("Failure percentage")[
                        ["Targeted retention", "Random mean retention"]
                    ]
                if task == "Spanning forest":
                    forest = minimum_spanning_forest(
                        graph, "length_m" if objective == "distance" else "travel_time_s"
                    )
                    details = asdict(forest)
                    forest_edges = forest.forest_edges
                    table = [{"original_edge": str(edge)} for edge in forest_edges[:30]]
                view = analytics_map(graph, scores, failed, forest_edges)
                st.session_state["structural_output"] = (summary, details, table, chart, view)
        except (ValueError, OSError, KeyError) as error:
            st.error(str(error))
    if "structural_output" in st.session_state:
        summary, details, table, chart, view = st.session_state["structural_output"]
        st.success("Analytics complete")
        st.write(summary)
        st.write(details)
        st.dataframe(table)
        if chart is not None:
            st.line_chart(chart)
        st.caption(
            "Structural screening uses heuristic weights. Forest projection ignores one-way roads. "
            "Orange importance · cyan largest surviving component · red X failures · green forest. "
            "Map layers show at most 300 items; analytics use the full graph."
        )
        st_folium(view, returned_objects=[], height=400, key="structural_map")
