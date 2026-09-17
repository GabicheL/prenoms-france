"""Tests d'intégration de l'application Streamlit (app/streamlit_app.py).

Utilise le framework de test officiel de Streamlit (AppTest) : le script est
exécuté en mémoire, sans navigateur, ce qui permet de vérifier qu'il ne lève
aucune exception et se comporte correctement sur les cas limites.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "prenoms-2025-nat.csv"

pytestmark = pytest.mark.skipif(
    not DATA_FILE.exists(),
    reason="nécessite le fichier de données INSEE (non versionné, voir README)",
)


def test_app_loads_without_exception() -> None:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=60)
    assert not at.exception
    assert [t.label for t in at.tabs] == [
        "Évolution d'un prénom",
        "Comparer plusieurs prénoms",
        "Palmarès d'une année",
    ]


def test_unknown_first_name_shows_warning_not_crash() -> None:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=60)
    at.text_input(key="evolution_prenom").set_value("Zzzinexistant")
    at.run(timeout=60)
    assert not at.exception
    assert any("Aucune donnée" in w.value for w in at.warning)


def test_comparison_tolerates_one_unknown_name() -> None:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=60)
    at.text_input(key="comparaison_prenoms").set_value("Gabriel, Zzzinexistant")
    at.run(timeout=60)
    assert not at.exception


def test_palmares_top_slider_changes_result_size() -> None:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=60)
    at.slider(key="palmares_top").set_value(5)
    at.run(timeout=60)
    assert not at.exception
    assert len(at.dataframe[0].value) == 5
