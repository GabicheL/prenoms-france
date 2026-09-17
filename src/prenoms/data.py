"""Chargement et nettoyage du fichier national des prénoms (INSEE).

Source : https://www.insee.fr/fr/statistiques/8595130
Format attendu du fichier national (ex. prenoms-2025-nat_csv.zip),
séparateur ';' :

    sexe;preusuel;annais;nombre

- sexe     : 1 (masculin) ou 2 (féminin)
- preusuel : prénom usuel en majuscules ; "_PRENOMS_RARES" regroupe les
             prénoms trop peu donnés une année pour être publiés
             individuellement
- annais   : année de naissance (AAAA) ; "XXXX" = année inconnue
- nombre   : nombre de naissances pour cette ligne
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

SEX_LABELS = {1: "M", 2: "F"}
UNKNOWN_YEAR_CODE = "XXXX"
EXPECTED_COLUMNS = {"sexe", "preusuel", "annais", "nombre"}


def load_nat_file(csv_path: str | Path) -> pd.DataFrame:
    """Charge le fichier national des prénoms INSEE et le nettoie.

    Args:
        csv_path: Chemin vers le fichier CSV brut (séparateur ';').

    Returns:
        Un DataFrame avec les colonnes ``prenom`` (str), ``sexe``
        (str, "M"/"F"), ``annee`` (int) et ``naissances`` (int), trié
        par prénom puis année. Les lignes à l'année inconnue ("XXXX")
        sont écartées car elles ne peuvent pas être placées sur une
        frise temporelle.

    Raises:
        FileNotFoundError: si ``csv_path`` n'existe pas.
        ValueError: si les colonnes attendues sont absentes du fichier.
    """
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

    df = df[df["annais"] != UNKNOWN_YEAR_CODE].copy()

    cleaned = pd.DataFrame(
        {
            "prenom": df["preusuel"].astype(str).str.strip().str.upper(),
            "sexe": df["sexe"].astype(int).map(SEX_LABELS),
            "annee": df["annais"].astype(int),
            "naissances": df["nombre"].astype(int),
        }
    )
    return cleaned.sort_values(["prenom", "annee"]).reset_index(drop=True)


def _read_with_encoding_fallback(csv_path: Path) -> pd.DataFrame:
    """Lit le CSV INSEE en gérant les deux encodages historiquement utilisés."""
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(csv_path, sep=";", encoding=encoding, dtype=str)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error  # pragma: no cover - filet de sécurité
