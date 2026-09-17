"""Tests du chargement des données (module prenoms.data)."""
from pathlib import Path

import pytest

from prenoms.data import load_nat_file

CSV_CONTENT = (
    "sexe;prenom;periode;valeur;rang\n"
    "1;Jean;1950;120;5\n"
    "1;Jean;1951;110;7\n"
    "2;Marie;1950;95;3\n"
    "1;;1950;10;999\n"
)


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "nat_sample.csv"
    csv_path.write_text(CSV_CONTENT, encoding="utf-8")
    return csv_path


def test_returns_expected_columns(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert list(df.columns) == ["prenom", "sexe", "annee", "naissances", "rang"]


def test_drops_rows_without_prenom(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert len(df) == 3  # la ligne sans prénom est écartée
    assert df["prenom"].isna().sum() == 0


def test_maps_sex_codes_to_letters(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert set(df.loc[df["prenom"] == "JEAN", "sexe"]) == {"M"}
    assert set(df.loc[df["prenom"] == "MARIE", "sexe"]) == {"F"}


def test_uppercases_first_names(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert "JEAN" in df["prenom"].values
    assert "Jean" not in df["prenom"].values


def test_keeps_rang_column(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    marie_rang = df.loc[df["prenom"] == "MARIE", "rang"].iloc[0]
    assert marie_rang == 3


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_nat_file(tmp_path / "does_not_exist.csv")


def test_missing_columns_raises(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("a;b;c\n1;2;3\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_nat_file(bad_csv)
