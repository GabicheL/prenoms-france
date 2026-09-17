"""Application Streamlit — évolution des prénoms en France depuis 1900.

Lancement local :
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from prenoms.analysis import annee_pic, comparer_prenoms, evolution_prenom, palmares
from prenoms.data import load_nat_file

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "prenoms-2025-nat.csv"
SEXE_LABELS = {"Cumulé (M + F)": None, "Masculin": "M", "Féminin": "F"}


@st.cache_data(show_spinner="Chargement du fichier INSEE...")
def get_data() -> "pd.DataFrame":  # noqa: F821 - import différé pour le typage
    return load_nat_file(DATA_PATH)


def main() -> None:
    st.set_page_config(
        page_title="Prénoms en France",
        page_icon="🇫🇷",
        layout="wide",
    )
    st.title("Évolution des prénoms en France depuis 1900")
    st.caption(
        "Source : [Fichier des prénoms — INSEE]"
        "(https://www.insee.fr/fr/statistiques/8595130), édition 2025."
    )

    if not DATA_PATH.exists():
        st.error(
            f"Fichier introuvable : `{DATA_PATH}`.\n\n"
            "Télécharge le fichier national sur "
            "https://www.insee.fr/fr/statistiques/8595130 et place-le dans `data/raw/`."
        )
        st.stop()

    df = get_data()

    onglet_evolution, onglet_comparaison, onglet_palmares = st.tabs(
        ["Évolution d'un prénom", "Comparer plusieurs prénoms", "Palmarès d'une année"]
    )

    with onglet_evolution:
        afficher_evolution(df)

    with onglet_comparaison:
        afficher_comparaison(df)

    with onglet_palmares:
        afficher_palmares(df)


def afficher_evolution(df) -> None:
    col_saisie, col_options = st.columns([2, 1])
    prenom = col_saisie.text_input("Prénom", value="Gabriel", key="evolution_prenom")
    sexe_label = col_options.selectbox(
        "Sexe", list(SEXE_LABELS), key="evolution_sexe"
    )
    sexe = SEXE_LABELS[sexe_label]

    if not prenom.strip():
        st.info("Entre un prénom pour voir son évolution.")
        return

    try:
        evolution = evolution_prenom(df, prenom, sexe)
        pic_annee, pic_valeur = annee_pic(df, prenom, sexe)
    except ValueError as erreur:
        st.warning(str(erreur))
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Naissances au total", f"{evolution['naissances'].sum():,}".replace(",", " "))
    col2.metric("Année du pic", pic_annee)
    col3.metric("Naissances cette année-là", f"{pic_valeur:,}".replace(",", " "))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=evolution["annee"],
            y=evolution["naissances"],
            mode="lines",
            name=prenom.strip().upper(),
            line=dict(color="#2563eb", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[pic_annee],
            y=[pic_valeur],
            mode="markers",
            name="Pic",
            marker=dict(color="#dc2626", size=10),
            hovertemplate="Pic en %{x} : %{y} naissances<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Évolution du prénom {prenom.strip().upper()}",
        xaxis_title="Année",
        yaxis_title="Naissances",
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")


def afficher_comparaison(df) -> None:
    saisie = st.text_input(
        "Prénoms à comparer (séparés par des virgules)",
        value="Gabriel, Noah, Léo",
        key="comparaison_prenoms",
    )
    sexe_label = st.selectbox("Sexe", list(SEXE_LABELS), key="comparaison_sexe")
    sexe = SEXE_LABELS[sexe_label]

    prenoms = [p.strip() for p in saisie.split(",") if p.strip()]
    if not prenoms:
        st.info("Entre au moins un prénom.")
        return

    try:
        comparaison = comparer_prenoms(df, prenoms, sexe)
    except ValueError as erreur:
        st.warning(str(erreur))
        return

    fig = go.Figure()
    for colonne in comparaison.columns:
        if colonne == "annee":
            continue
        fig.add_trace(
            go.Scatter(
                x=comparaison["annee"],
                y=comparaison[colonne],
                mode="lines",
                name=colonne,
                line=dict(width=2),
            )
        )
    fig.update_layout(
        title="Comparaison de prénoms",
        xaxis_title="Année",
        yaxis_title="Naissances",
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")


def afficher_palmares(df) -> None:
    annees_disponibles = sorted(df["annee"].unique(), reverse=True)

    col_annee, col_sexe, col_top = st.columns(3)
    annee = col_annee.selectbox("Année", annees_disponibles, key="palmares_annee")
    sexe_label = col_sexe.selectbox("Sexe", ["Masculin", "Féminin"], key="palmares_sexe")
    top = col_top.slider("Nombre de prénoms", min_value=3, max_value=30, value=10, key="palmares_top")

    sexe = "M" if sexe_label == "Masculin" else "F"

    try:
        classement = palmares(df, annee, sexe, top=top)
    except ValueError as erreur:
        st.warning(str(erreur))
        return

    fig = go.Figure(
        go.Bar(
            x=classement["naissances"],
            y=classement["prenom"],
            orientation="h",
            marker=dict(color="#2563eb" if sexe == "M" else "#db2777"),
        )
    )
    fig.update_layout(
        title=f"Top {top} prénoms {sexe_label.lower()}s — {annee}",
        xaxis_title="Naissances",
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, width="stretch")
    st.dataframe(classement, width="stretch", hide_index=True)


if __name__ == "__main__":
    main()
