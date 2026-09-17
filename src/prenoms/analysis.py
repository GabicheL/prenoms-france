"""Fonctions d'analyse sur les données nettoyées des prénoms.

Toutes les fonctions attendent en entrée le DataFrame renvoyé par
``prenoms.data.load_nat_file`` (colonnes : prenom, sexe, annee,
naissances, rang).
"""
from __future__ import annotations

import pandas as pd

VALID_SEXES = {"M", "F"}


def evolution_prenom(
    df: pd.DataFrame, prenom: str, sexe: str | None = None
) -> pd.DataFrame:
    """Évolution annuelle du nombre de naissances pour un prénom.

    Args:
        df: DataFrame nettoyé (voir ``prenoms.data.load_nat_file``).
        prenom: Prénom recherché (insensible à la casse).
        sexe: "M", "F", ou None pour cumuler les deux sexes.

    Returns:
        DataFrame trié par année. Colonnes ``annee`` et ``naissances``
        si ``sexe`` est None (les deux sexes sont alors cumulés par
        année) ; colonnes ``annee``, ``naissances`` et ``rang`` si un
        sexe est précisé.

    Raises:
        ValueError: si le prénom (éventuellement filtré par sexe) est
            absent du fichier, ou si ``sexe`` n'est ni "M" ni "F".
    """
    prenom_norm = prenom.strip().upper()
    subset = df[df["prenom"] == prenom_norm]

    if sexe is not None:
        sexe = _validate_sexe(sexe)
        subset = subset[subset["sexe"] == sexe]

    if subset.empty:
        cible = f"{prenom_norm} ({sexe})" if sexe else prenom_norm
        raise ValueError(f"Aucune donnée pour le prénom {cible!r}.")

    if sexe is not None:
        return (
            subset[["annee", "naissances", "rang"]]
            .sort_values("annee")
            .reset_index(drop=True)
        )

    return (
        subset.groupby("annee", as_index=False)["naissances"]
        .sum()
        .sort_values("annee")
        .reset_index(drop=True)
    )


def annee_pic(df: pd.DataFrame, prenom: str, sexe: str | None = None) -> tuple[int, int]:
    """Année où le prénom a été le plus donné, et le nombre de naissances.

    Returns:
        Un tuple ``(annee, naissances)``.
    """
    evolution = evolution_prenom(df, prenom, sexe)
    ligne = evolution.loc[evolution["naissances"].idxmax()]
    return int(ligne["annee"]), int(ligne["naissances"])


def comparer_prenoms(
    df: pd.DataFrame, prenoms: list[str], sexe: str | None = None
) -> pd.DataFrame:
    """Met plusieurs prénoms côte à côte pour comparaison graphique.

    Contrairement à ``evolution_prenom``, un prénom sans aucune donnée
    pour le sexe demandé n'interrompt pas la comparaison : sa colonne
    est simplement remplie de zéros (utile par ex. pour comparer un
    prénom mixte à un prénom très genré sur un seul sexe).

    Args:
        df: DataFrame nettoyé.
        prenoms: Liste de prénoms à comparer.
        sexe: "M", "F", ou None pour cumuler les deux sexes.

    Returns:
        DataFrame large : une colonne ``annee`` puis une colonne par
        prénom (nombre de naissances cette année-là, 0 si le prénom
        n'a pas été donné cette année-là).

    Raises:
        ValueError: si ``prenoms`` est vide, si ``sexe`` est invalide,
            ou si aucun des prénoms demandés n'a la moindre donnée.
    """
    if not prenoms:
        raise ValueError("La liste de prénoms à comparer est vide.")
    if sexe is not None:
        sexe = _validate_sexe(sexe)

    colonnes = []
    for prenom in prenoms:
        nom_colonne = prenom.strip().upper()
        subset = df[df["prenom"] == nom_colonne]
        if sexe is not None:
            subset = subset[subset["sexe"] == sexe]
        colonnes.append(subset.groupby("annee")["naissances"].sum().rename(nom_colonne))

    combine = pd.concat(colonnes, axis=1)
    if combine.empty:
        noms = ", ".join(p.strip().upper() for p in prenoms)
        raise ValueError(f"Aucune donnée pour les prénoms demandés : {noms}.")

    return combine.fillna(0).astype(int).sort_index().reset_index()


def palmares(df: pd.DataFrame, annee: int, sexe: str, top: int = 10) -> pd.DataFrame:
    """Classement des prénoms les plus donnés une année donnée.

    Args:
        df: DataFrame nettoyé.
        annee: Année du palmarès.
        sexe: "M" ou "F".
        top: Nombre de prénoms à retourner (par défaut 10).

    Returns:
        DataFrame avec les colonnes ``rang``, ``prenom`` et
        ``naissances``, trié par rang croissant.

    Raises:
        ValueError: si ``sexe`` est invalide, ``top`` n'est pas positif,
            ou qu'aucune donnée n'existe pour cette année/ce sexe.
    """
    sexe = _validate_sexe(sexe)
    if top <= 0:
        raise ValueError("`top` doit être un entier strictement positif.")

    subset = df[(df["annee"] == annee) & (df["sexe"] == sexe) & (df["rang"] <= top)]
    if subset.empty:
        raise ValueError(f"Aucune donnée pour l'année {annee} et le sexe {sexe!r}.")

    return (
        subset[["rang", "prenom", "naissances"]]
        .sort_values("rang")
        .reset_index(drop=True)
    )


def _validate_sexe(sexe: str) -> str:
    sexe = sexe.strip().upper()
    if sexe not in VALID_SEXES:
        raise ValueError(f"`sexe` doit valoir 'M' ou 'F', reçu {sexe!r}.")
    return sexe
