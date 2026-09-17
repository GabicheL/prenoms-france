"""Chargement et nettoyage du fichier national des prénoms (INSEE).

Source : https://www.insee.fr/fr/statistiques/8595130
Colonnes du fichier national (édition 2025, ex. prenoms-2025-nat_csv.zip),
séparateur ';' :

    sexe;prenom;periode;valeur;rang

- sexe    : 1 (masculin) ou 2 (féminin)
- prenom  : prénom usuel
- periode : année de naissance (AAAA)
- valeur  : nombre de naissances pour ce prénom, ce sexe, cette année
- rang    : rang du prénom cette année-là, au sein de son sexe
            (1 = prénom le plus donné)

Remarque : des éditions plus anciennes de ce fichier utilisaient un autre
schéma (sexe;preusuel;annais;nombre, avec un code "XXXX" pour les années
inconnues et un prénom "_PRENOMS_RARES" regroupant les prénoms peu donnés).
Ce module cible le schéma de l'édition 2025, vérifié sur le fichier réel.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

SEX_LABELS = {1: "M", 2: "F"}
EXPECTED_COLUMNS = {"sexe", "prenom", "periode", "valeur", "rang"}


def load_nat_file(csv_path: str | Path) -> pd.DataFrame:
    """Charge le fichier national des prénoms INSEE et le nettoie.

    Args:
        csv_path: Chemin vers le fichier CSV brut (séparateur ';').

    Returns:
        Un DataFrame avec les colonnes ``prenom`` (str), ``sexe``
        (str, "M"/"F"), ``annee`` (int), ``naissances`` (int) et
        ``rang`` (int), trié par prénom puis année. Les rares lignes
        sans prénom renseigné sont écartées.

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
    """Lit le CSV INSEE en gérant les deux encodages historiquement utilisés."""
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(csv_path, sep=";", encoding=encoding, dtype=str)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise last_error  # pragma: no cover - filet de sécurité
