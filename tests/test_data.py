"""Tests du chargement des données (module prenoms.data)."""
from pathlib import Path

import pytest

from prenoms.data import load_nat_file

CSV_CONTENT = (
    "sexe;preusuel;annais;nombre\n"
    "1;Jean;1950;120\n"
    "1;Jean;1951;110\n"
    "2;Marie;1950;95\n"
    "2;Marie;XXXX;3\n"
    "1;_PRENOMS_RARES;1950;42\n"
)


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "nat_sample.csv"
    csv_path.write_text(CSV_CONTENT, encoding="utf-8")
    return csv_path


def test_returns_expected_columns(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert list(df.columns) == ["prenom", "sexe", "annee", "naissances"]


def test_drops_unknown_years(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert (df["annee"] == "XXXX").sum() == 0
    assert len(df) == 4  # la ligne annais=XXXX est écartée


def test_maps_sex_codes_to_letters(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert set(df.loc[df["prenom"] == "JEAN", "sexe"]) == {"M"}
    assert set(df.loc[df["prenom"] == "MARIE", "sexe"]) == {"F"}


def test_uppercases_first_names(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert "JEAN" in df["prenom"].values
    assert "Jean" not in df["prenom"].values


def test_keeps_rare_names_bucket(sample_csv: Path) -> None:
    df = load_nat_file(sample_csv)
    assert "_PRENOMS_RARES" in df["prenom"].values


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_nat_file(tmp_path / "does_not_exist.csv")


def test_missing_columns_raises(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("a;b;c\n1;2;3\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_nat_file(bad_csv)
