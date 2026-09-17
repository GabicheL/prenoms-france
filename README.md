# Évolution des prénoms en France (1900–2025)

![Tests](https://github.com/GabicheL/prenoms-france/actions/workflows/tests.yml/badge.svg)

Projet perso pour mon portfolio, fait en marge de mon M1 Informatique pour la
Décision et la Donnée à Dauphine. Je voulais un jeu de données réel plutôt
qu'un dataset jouet pour pratiquer pandas et Streamlit : le [fichier des
prénoms de l'INSEE](https://www.insee.fr/fr/statistiques/8595130), qui
recense tous les prénoms donnés en France depuis 1900, s'y prêtait bien (et
regarder l'évolution de son propre prénom est un bon test, cf capture
ci-dessous). J'ai commencé par un notebook d'exploration, puis j'ai eu envie
d'en faire une version interactive avec Streamlit.

## Aperçu

| Évolution d'un prénom | Comparaison de plusieurs prénoms | Palmarès d'une année |
|---|---|---|
| ![Évolution du prénom Gabriel](docs/img/evolution_gabriel.png) | ![Comparaison du podium 2025](docs/img/comparaison_podium_2025.png) | ![Palmarès 2025](docs/img/palmares_2025.png) |

Ces trois graphiques viennent du notebook d'exploration ; l'application
Streamlit permet de faire la même chose de façon interactive, pour n'importe
quel prénom.

## Stack technique

- **pandas** — chargement et agrégation des ~725 000 lignes du fichier INSEE
- **Jupyter** — exploration initiale, visualisations statiques (matplotlib)
- **Streamlit + Plotly** — application interactive, graphiques avec info-bulles
- **pytest** (+ `streamlit.testing.v1.AppTest`) — tests unitaires et
  d'intégration, y compris sur l'application Streamlit elle-même
- **GitHub Actions** — tests exécutés automatiquement à chaque push

## Structure du projet

```
prenoms-france/
├── app/
│   └── streamlit_app.py      # application interactive
├── notebooks/
│   └── 01_exploration.ipynb  # exploration initiale, visualisations
├── src/prenoms/
│   ├── data.py                # chargement et nettoyage du fichier INSEE
│   └── analysis.py            # évolution, comparaison, palmarès
├── tests/                     # tests unitaires (data, analysis) et
│                               # d'intégration (app)
├── data/raw/                  # fichier INSEE (non versionné, voir ci-dessous)
└── docs/img/                  # captures utilisées dans ce README
```

Le code d'analyse vit dans `src/prenoms/`, indépendant du notebook et de
l'application : les deux le réutilisent tel quel plutôt que de dupliquer la
logique de chargement/agrégation à deux endroits.

## Installation

```bash
git clone https://github.com/GabicheL/prenoms-france.git
cd prenoms-france
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Télécharge ensuite le fichier national des prénoms sur
[insee.fr/fr/statistiques/8595130](https://www.insee.fr/fr/statistiques/8595130)
(fichier `prenoms-2025-nat_csv.zip`), dézippe-le, et place le `.csv` obtenu
dans `data/raw/`. Il n'est pas versionné (fichier assez lourd, régulièrement
mis à jour par l'INSEE), donc le README indique juste où le trouver.

## Utilisation

**Notebook d'exploration :**

```bash
jupyter lab notebooks/01_exploration.ipynb
```

**Application interactive :**

```bash
streamlit run app/streamlit_app.py
```

**Tests :**

```bash
pytest -v
```

Les tests sur `data.py` et `analysis.py` utilisent des données synthétiques et
tournent sans le fichier INSEE. Ceux sur `app/streamlit_app.py` ont besoin du
vrai fichier dans `data/raw/` et sont automatiquement ignorés sinon — c'est
pourquoi la CI GitHub Actions (qui n'a pas ce fichier) passe quand même, en
couvrant le cœur logique du projet.

## Choix techniques

- Séparer `src/prenoms` de Jupyter et de Streamlit pour pouvoir le tester
  seul et le réutiliser aux deux endroits sans dupliquer la logique.
- Le format du fichier INSEE n'est pas celui que la doc publique laissait
  penser (voir l'historique de commits) : j'ai préféré adapter le code au
  vrai fichier plutôt qu'à ce qui était documenté.
- Le rang du palmarès est repris tel quel depuis la colonne fournie par
  l'INSEE plutôt que recalculé, pour rester fidèle à leur méthodologie.
- `comparer_prenoms` met une courbe à zéro plutôt que de planter si un des
  prénoms comparés n'a pas de données pour le sexe demandé.

## Pistes d'amélioration

Si je continue ce projet à l'occasion :

- Ajouter le fichier par département pour une vue géographique
- Cache sur les agrégations les plus fréquentes si le volume de recherches augmente
- Déployer l'app sur Streamlit Community Cloud
- Recherche tolérante aux fautes de frappe / accents sur le champ prénom

## Licence

MIT — voir [LICENSE](LICENSE).
