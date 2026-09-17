"""Chargement et nettoyage du fichier national des prénoms (INSEE).

Source : https://www.insee.fr/fr/statistiques/8595130
Colonnes du fichier (édition 2025), séparateur ';' : sexe;prenom;periode;valeur;rang
- sexe : 1 (masculin) ou 2 (féminin)
- prenom, periode (année), valeur (naissances cette année-là), rang (classement)

Les éditions précédentes du fichier INSEE utilisaient un autre schéma
(sexe;preusuel;annais;nombre) - je m'étais basé dessus au départ avant de
regarder le vrai fichier téléchargé, d'où l'ajustement (voir l'historique
de commits).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

SEX_LABELS = {1: "M", 2: "F"}
EXPECTED_COLUMNS = {"sexe", "prenom", "periode", "valeur", "rang"}


def load_nat_file(csv_path: str | Path) -> pd.DataFrame:
    """Charge et nettoie le fichier national des prénoms INSEE."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {csv_path}. Télécharge le fichier "
            "national sur https://www.insee.fr/fr/statistiques/8595130 "
            "et place-le dans data/raw/."
        )

    df = _read_with_encoding_fallback(csv_path)

    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans {csv_path.name} : {sorted(missing)}. "
            f"Colonnes trouvées : {list(df.columns)}"
        )

    df = df.dropna(subset=["prenom"]).copy()

    cleaned = pd.DataFrame(
        {
            "prenom": df["prenom"].astype(str).str.strip().str.upper(),
            "sexe": df["sexe"].astype(int).map(SEX_LABELS),
            "annee": df["periode"].astype(int),
            "naissances": df["valeur"].astype(int),
            "rang": df["rang"].astype(int),
        }
    )
    return cleaned.sort_values(["prenom", "annee"]).reset_index(drop=True)


def _read_with_encoding_fallback(csv_path: Path) -> pd.DataFrame:
    # le fichier INSEE n'est pas toujours en utf-8 selon l'édition téléchargée
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(csv_path, sep=";", encoding=encoding, dtype=str)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error  # pragma: no cover
