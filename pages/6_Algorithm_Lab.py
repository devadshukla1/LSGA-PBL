"""Interactive Algorithm Lab for empirical routing benchmarks and scaling evaluation."""

import pandas as pd
import streamlit as st

from config import DEFAULT_BENCHMARK_PAIRS, DEFAULT_BENCHMARK_REPETITIONS, DEFAULT_RANDOM_SEED
from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.report_export import export_benchmark_results
from src.graph.dataset_service import list_datasets, load
from src.ui.sidebar import render_app_sidebar
from src.ui.state import set_active_dataset_id
from src.ui.theme import inject_custom_theme
from src.visualization.benchmark_charts import (
    chart_algorithm_speedup,
    chart_correctness_summary,
    chart_explored_nodes,
    chart_memory_by_algorithm,
    chart_runtime_by_algorithm,
    chart_runtime_distribution,
    chart_runtime_vs_graph_size,
)


def algorithm_lab() -> None:
    inject_custom_theme()
    st.title("Algorithm Lab")
    st.caption("Phase 9 of 12 · Large-Scale Graph Analysis")
    st.info(
        "Empirical evaluation of Dijkstra, A*, and Bidirectional Dijkstra. "
        "High-resolution runtime measurements are isolated from separate memory-profiling runs. "
        "Optimality is verified against the NetworkX oracle."
    )

    # -------------------------------------------------------------
    # SECTION A: Dataset Selection
    # -------------------------------------------------------------
    st.subheader("1. Dataset Selection")
    datasets = list_datasets()
    dataset = st.selectbox("Select Target Road Network", datasets, index=0)

    try:
        info = load(dataset)
        graph = info.graph
        set_active_dataset_id(dataset)
        render_app_sidebar(graph, info.metadata.dataset_name, info.origin)
    except Exception as err:
        render_app_sidebar()
        st.error(f"Failed to load dataset: {err}")
        return

    st.caption(f"{info.origin} · {len(graph)} junctions · {graph.number_of_edges()} directed roads")

    # -------------------------------------------------------------
    # SECTION B: Benchmark Configuration
    # -------------------------------------------------------------
    st.subheader("2. Benchmark Configuration")
    col1, col2 = st.columns(2)
    with col1:
        selected_algos = st.multiselect(
            "Routing Algorithms",
            options=["dijkstra", "astar", "bidirectional_dijkstra"],
            default=["dijkstra", "astar", "bidirectional_dijkstra"],
        )
        selected_objs = st.multiselect(
            "Evaluation Objectives",
            options=["distance", "travel_time"],
            default=["distance", "travel_time"],
        )

    with col2:
        max_valid_size = len(graph)
        default_sizes = [s for s in [10, 50, 100, 500] if s < max_valid_size]
        size_input = st.text_input(
            "Sample Graph Sizes (comma-separated, max: " + str(max_valid_size) + ")",
            value=", ".join(map(str, default_sizes)),
        )
        parsed_sizes = []
        if size_input.strip():
            for part in size_input.split(","):
                try:
                    s_val = int(part.strip())
                    if 0 < s_val <= max_valid_size:
                        parsed_sizes.append(s_val)
                except ValueError:
                    pass

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        query_count = st.number_input(
            "Query Pairs (OD count)",
            min_value=1,
            max_value=100,
            value=min(DEFAULT_BENCHMARK_PAIRS, max(2, len(graph))),
        )
    with col_q2:
        repetitions = st.number_input(
            "Repetitions per Query",
            min_value=1,
            max_value=10,
            value=DEFAULT_BENCHMARK_REPETITIONS,
        )
    with col_q3:
        seed = st.number_input("Random Seed", value=DEFAULT_RANDOM_SEED)

    mem_toggle = st.checkbox("Enable Peak Python Memory Profiling (tracemalloc)", value=True)

    # -------------------------------------------------------------
    # SECTION C: Run Benchmark
    # -------------------------------------------------------------
    st.subheader("3. Benchmark Execution")
    if st.button("Run Benchmark Experiment", key="btn_run_bench"):
        if not selected_algos:
            st.error("Please select at least one algorithm.")
            return
        if not selected_objs:
            st.error("Please select at least one objective.")
            return

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def on_progress(step: int, total: int, msg: str) -> None:
            progress_bar.progress(step / max(1, total))
            status_text.text(msg)

        config = BenchmarkConfig(
            dataset_id=dataset,
            graph_sizes=parsed_sizes,
            algorithms=selected_algos,
            objectives=selected_objs,
            query_count=int(query_count),
            repetitions=int(repetitions),
            random_seed=int(seed),
            warmup_runs=1,
            memory_enabled=mem_toggle,
            correctness_enabled=True,
        )

        with st.spinner("Executing benchmark protocol..."):
            raw, summaries, comparisons, datasets_meta, manifest = run_benchmarks(
                graph,
                config=config,
                progress_callback=on_progress,
            )
            # Auto export results
            out_dir = export_benchmark_results(raw, summaries, comparisons, datasets_meta, manifest)

            st.session_state["active_bench_results"] = (
                raw,
                summaries,
                comparisons,
                datasets_meta,
                manifest,
                out_dir,
            )

        progress_bar.progress(1.0)
        status_text.text("Benchmarking completed.")
        st.success(f"Experiment {manifest.experiment_id} saved to {out_dir.name}")

    # -------------------------------------------------------------
    # SECTION D, E, F: Results Display
    # -------------------------------------------------------------
    if "active_bench_results" in st.session_state:
        raw, summaries, comparisons, datasets_meta, manifest, out_dir = st.session_state[
            "active_bench_results"
        ]

        st.subheader("4. Statistical Summaries")
        summary_df = pd.DataFrame([s.__dict__ for s in summaries])
        st.dataframe(summary_df, use_container_width=True)

        if comparisons:
            st.subheader("5. Paired Speedup Comparisons")
            comp_df = pd.DataFrame([c.__dict__ for c in comparisons])
            st.dataframe(comp_df, use_container_width=True)

        st.subheader("6. Performance Visualizations")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Runtime", "Scaling", "Explored Nodes", "Memory Footprint", "Speedup"]
        )
        with tab1:
            st.plotly_chart(chart_runtime_by_algorithm(summary_df), use_container_width=True)
            raw_df = pd.DataFrame([r.__dict__ for r in raw])
            st.plotly_chart(chart_runtime_distribution(raw_df), use_container_width=True)
        with tab2:
            st.plotly_chart(chart_runtime_vs_graph_size(summary_df), use_container_width=True)
        with tab3:
            st.plotly_chart(chart_explored_nodes(summary_df), use_container_width=True)
        with tab4:
            st.plotly_chart(chart_memory_by_algorithm(summary_df), use_container_width=True)
        with tab5:
            if comparisons:
                st.plotly_chart(chart_algorithm_speedup(comp_df), use_container_width=True)
            st.plotly_chart(chart_correctness_summary(summary_df), use_container_width=True)

        st.subheader("7. CSV Download")
        st.download_button(
            "Download Raw CSV",
            data=pd.DataFrame([r.__dict__ for r in raw]).to_csv(index=False),
            file_name=f"{manifest.experiment_id}_raw.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    algorithm_lab()
