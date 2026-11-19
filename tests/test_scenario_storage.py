from functools import partial

from streamlit.testing.v1 import AppTest

from src.simulation import scenario_storage


def test_ui_save_load_reset(tmp_path, monkeypatch):
    for name in ("list_scenarios", "load_scenario", "save_scenario"):
        monkeypatch.setattr(
            scenario_storage, name, partial(getattr(scenario_storage, name), directory=tmp_path)
        )
    app = AppTest.from_file("pages/3_Traffic_Simulator.py").run(timeout=30)
    app.selectbox(key="sim_level").set_value("heavy")
    app.button[2].click().run(timeout=30)
    assert not app.exception
    app.button[3].click().run(timeout=30)
    assert not app.exception
    identifiers = scenario_storage.list_scenarios()
    assert len(identifiers) == 1
    app.button[1].click().run(timeout=30)
    assert app.selectbox(key="sim_level").value == "normal"
    app.selectbox[1].select(identifiers[0])
    app.button[0].click().run(timeout=30)
    assert not app.exception
    assert app.selectbox(key="sim_level").value == "heavy"
    app.button[2].click().run(timeout=30)
    assert not app.exception and app.success[0].value == "Simulation complete · ok"
