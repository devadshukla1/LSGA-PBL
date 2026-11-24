"""Tests verifying reproducibility of benchmark configurations, queries, and sampling."""

from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.dataset_sampler import prepare_benchmark_datasets
from src.benchmarks.query_generator import generate_benchmark_queries
from src.graph.dataset_service import load


def test_sampling_reproducibility():
    info = load()
    graph = info.graph
    target = 10
    seed = 12345

    ds1 = prepare_benchmark_datasets(graph, "offline", target_sizes=[target], seed=seed)
    ds2 = prepare_benchmark_datasets(graph, "offline", target_sizes=[target], seed=seed)

    assert len(ds1) == len(ds2)
    assert set(ds1[0].graph.nodes) == set(ds2[0].graph.nodes)
    assert set(ds1[0].graph.edges(keys=True)) == set(ds2[0].graph.edges(keys=True))


def test_query_generation_reproducibility():
    info = load()
    graph = info.graph
    seed = 9999

    q1 = generate_benchmark_queries(graph, count=8, seed=seed)
    q2 = generate_benchmark_queries(graph, count=8, seed=seed)

    assert [(q.source, q.target) for q in q1] == [(q.source, q.target) for q in q2]


def test_config_defaults_reproducible():
    cfg1 = BenchmarkConfig()
    cfg2 = BenchmarkConfig()
    assert cfg1.random_seed == cfg2.random_seed
    assert cfg1.query_count == cfg2.query_count
    assert cfg1.repetitions == cfg2.repetitions
