"""Results & Export dashboard page for reviewing and downloading saved benchmark runs."""

import pandas as pd
import streamlit as st

from config import BENCHMARKS_DIR
from src.benchmarks.report_export import list_saved_experiments, load_benchmark_experiment
from src.ui.sidebar import render_app_sidebar
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


def results_page() -> None:
    inject_custom_theme()
    render_app_sidebar()
    st.title("Results & Export")
    st.caption("Phase 9 of 12 · Large-Scale Graph Analysis")
    st.info(
        "Inspect historical benchmark manifests, performance summaries, "
        "scaling profiles, and download reproducible CSV datasets."
    )

    experiments = list_saved_experiments(BENCHMARKS_DIR)

    if not experiments:
        st.warning(
            "No saved benchmark experiments found in `results/benchmarks/`. "
            "Execute an experiment in Algorithm Lab or via `python scripts/run_benchmarks.py`."
        )
        return

    exp_options = {e["id"]: e["path"] for e in experiments}
    selected_exp_id = st.selectbox(
        "Select Historical Experiment",
        options=list(exp_options.keys()),
        index=0,
    )

    exp_dir = exp_options[selected_exp_id]
    try:
        data = load_benchmark_experiment(exp_dir)
    except Exception as err:
        st.error(f"Failed to load experiment {selected_exp_id}: {err}")
        return

    manifest = data.get("manifest", {})
    st.subheader(f"Experiment Manifest: {selected_exp_id}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dataset", manifest.get("dataset_id", "N/A"))
    c2.metric("Timestamp", manifest.get("timestamp_utc", "")[:19].replace("T", " "))
    c3.metric("Queries per Config", manifest.get("query_count", 0))
    c4.metric("Repetitions", manifest.get("repetitions", 0))

    summary_df = data.get("summary", pd.DataFrame())
    comp_df = data.get("comparisons", pd.DataFrame())
    raw_df = data.get("raw", pd.DataFrame())
    corr_df = data.get("correctness", pd.DataFrame())

    tab_summary, tab_charts, tab_correctness, tab_downloads = st.tabs(
        ["Statistical Summaries", "Visualizations", "Correctness & Optimality", "Downloads"]
    )

    with tab_summary:
        st.subheader("Algorithm Performance Summaries")
        if not summary_df.empty:
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("No summary data available.")

        if not comp_df.empty:
            st.subheader("Paired Speedup Comparisons")
            st.dataframe(comp_df, use_container_width=True)

    with tab_charts:
        if not summary_df.empty:
            st.plotly_chart(chart_runtime_by_algorithm(summary_df), use_container_width=True)
            st.plotly_chart(chart_runtime_vs_graph_size(summary_df), use_container_width=True)
            st.plotly_chart(chart_explored_nodes(summary_df), use_container_width=True)
            st.plotly_chart(chart_memory_by_algorithm(summary_df), use_container_width=True)
            if not comp_df.empty:
                st.plotly_chart(chart_algorithm_speedup(comp_df), use_container_width=True)
            if not raw_df.empty:
                st.plotly_chart(chart_runtime_distribution(raw_df), use_container_width=True)

    with tab_correctness:
        st.subheader("NetworkX Oracle Optimality Verification")
        if not summary_df.empty:
            st.plotly_chart(chart_correctness_summary(summary_df), use_container_width=True)
        if not corr_df.empty:
            st.dataframe(corr_df.head(100), use_container_width=True)

    with tab_downloads:
        st.subheader("Export CSV Data")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if not raw_df.empty:
                st.download_button(
                    "Download Raw Observations CSV",
                    data=raw_df.to_csv(index=False),
                    file_name=f"{selected_exp_id}_raw.csv",
                    mime="text/csv",
                )
            if not summary_df.empty:
                st.download_button(
                    "Download Summary Statistics CSV",
                    data=summary_df.to_csv(index=False),
                    file_name=f"{selected_exp_id}_summary.csv",
                    mime="text/csv",
                )
        with d_col2:
            if not comp_df.empty:
                st.download_button(
                    "Download Paired Comparisons CSV",
                    data=comp_df.to_csv(index=False),
                    file_name=f"{selected_exp_id}_comparisons.csv",
                    mime="text/csv",
                )
            if not corr_df.empty:
                st.download_button(
                    "Download Correctness CSV",
                    data=corr_df.to_csv(index=False),
                    file_name=f"{selected_exp_id}_correctness.csv",
                    mime="text/csv",
                )


if __name__ == "__main__":
    results_page()
