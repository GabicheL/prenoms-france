"""Tests des fonctions d'analyse (module prenoms.analysis)."""
import pandas as pd
import pytest

from prenoms.analysis import annee_pic, comparer_prenoms, evolution_prenom, palmares


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"prenom": "CAMILLE", "sexe": "M", "annee": 2000, "naissances": 100, "rang": 5},
            {"prenom": "CAMILLE", "sexe": "F", "annee": 2000, "naissances": 300, "rang": 2},
            {"prenom": "CAMILLE", "sexe": "F", "annee": 2001, "naissances": 250, "rang": 3},
            {"prenom": "LÉA", "sexe": "F", "annee": 2000, "naissances": 500, "rang": 1},
            {"prenom": "LÉA", "sexe": "F", "annee": 2001, "naissances": 480, "rang": 1},
            {"prenom": "NOAH", "sexe": "M", "annee": 2000, "naissances": 200, "rang": 3},
            {"prenom": "NOAH", "sexe": "M", "annee": 2001, "naissances": 220, "rang": 2},
        ]
    )


def test_evolution_prenom_sums_both_sexes_by_default(df: pd.DataFrame) -> None:
    evolution = evolution_prenom(df, "camille")  # insensible à la casse
    assert list(evolution.columns) == ["annee", "naissances"]
    an_2000 = evolution.loc[evolution["annee"] == 2000, "naissances"].iloc[0]
    assert an_2000 == 400  # 100 (M) + 300 (F)


def test_evolution_prenom_filters_by_sexe(df: pd.DataFrame) -> None:
    evolution = evolution_prenom(df, "Camille", sexe="F")
    assert list(evolution.columns) == ["annee", "naissances", "rang"]
    assert evolution["naissances"].tolist() == [300, 250]


def test_evolution_prenom_unknown_name_raises(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        evolution_prenom(df, "INEXISTANT")


def test_evolution_prenom_invalid_sexe_raises(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        evolution_prenom(df, "Léa", sexe="X")


def test_annee_pic_returns_year_with_max_naissances(df: pd.DataFrame) -> None:
    annee, naissances = annee_pic(df, "Noah", sexe="M")
    assert (annee, naissances) == (2001, 220)


def test_comparer_prenoms_zero_fills_missing_years(df: pd.DataFrame) -> None:
    combine = comparer_prenoms(df, ["Léa", "Noah"], sexe="M")
    # Léa n'a aucune naissance masculine dans le jeu de test -> 0 partout
    assert (combine["LÉA"] == 0).all()
    assert combine["NOAH"].tolist() == [200, 220]


def test_comparer_prenoms_rejects_empty_list(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        comparer_prenoms(df, [])


def test_palmares_sorted_by_rang(df: pd.DataFrame) -> None:
    top = palmares(df, annee=2000, sexe="F", top=2)
    assert top["prenom"].tolist() == ["LÉA", "CAMILLE"]
    assert top["rang"].tolist() == [1, 2]


def test_palmares_invalid_top_raises(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        palmares(df, annee=2000, sexe="F", top=0)


def test_palmares_no_data_raises(df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        palmares(df, annee=1900, sexe="F")
