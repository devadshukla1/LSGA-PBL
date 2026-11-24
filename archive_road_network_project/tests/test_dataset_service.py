from unittest.mock import Mock

from scripts.generate_sample_graph import build_sample
from src.graph import dataset_service as service


def test_cache_refresh_and_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "PROCESSED_DATA_DIR", tmp_path)
    download = Mock(
        side_effect=[OSError("offline"), build_sample(), OSError("offline"), OSError("offline")]
    )
    monkeypatch.setattr(service.loader, "download", download)
    assert service.acquire().metadata.is_offline_sample
    real = service.acquire()
    assert not real.notice and real.metadata.dataset_id == service.dataset_id()
    assert service.acquire().origin == "Cached OpenStreetMap"
    assert service.acquire(force_refresh=True).origin == "Cached OpenStreetMap"
    (tmp_path / f"{service.dataset_id()}.graphml").write_text("invalid")
    fallback = service.acquire()
    assert fallback.metadata.is_offline_sample and "offline" in fallback.notice
    assert download.call_count == 4
