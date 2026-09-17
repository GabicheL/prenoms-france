"""Fonctions d'analyse sur les données nettoyées des prénoms.

Toutes les fonctions prennent en entrée le DataFrame renvoyé par
prenoms.data.load_nat_file (colonnes : prenom, sexe, annee, naissances, rang).
"""
from __future__ import annotations

import pandas as pd

VALID_SEXES = {"M", "F"}


def evolution_prenom(
    df: pd.DataFrame, prenom: str, sexe: str | None = None
) -> pd.DataFrame:
    """Évolution annuelle des naissances pour un prénom (sexe=None -> les deux cumulés)."""
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
    """Année où le prénom a été le plus donné, et le nombre de naissances cette année-là."""
    evolution = evolution_prenom(df, prenom, sexe)
    ligne = evolution.loc[evolution["naissances"].idxmax()]
    return int(ligne["annee"]), int(ligne["naissances"])


def comparer_prenoms(
    df: pd.DataFrame, prenoms: list[str], sexe: str | None = None
) -> pd.DataFrame:
    """Met plusieurs prénoms côte à côte pour comparaison graphique.

    Contrairement à evolution_prenom, un prénom sans donnée pour le sexe
    demandé n'interrompt pas la comparaison : sa colonne est mise à zéro.
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
    """Top prénoms les plus donnés une année donnée, pour un sexe."""
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
