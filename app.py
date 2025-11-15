import streamlit as st
import pandas as pd
from utils.io import load_and_clean_data
from utils.viz import get_pydeck_map, get_plotly_bar_chart, get_plotly_hist

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Data Storytelling IRVE",
    layout="wide"
)

# --- CHARGEMENT DES DONNÉES ---
data = load_and_clean_data('consolidation-etalab-schema-irve-statique-v-2.3.1-20251110.csv')

if data.empty:
    st.error("Impossible de charger les données. Vérifiez le fichier source.")
    st.stop()

# --- TITRE ET SOURCE ---
st.title("Data Storytelling : Le réseau de bornes derecharge (IRVE) en France")
st.caption("Source : data.gouv.fr (https://www.data.gouv.fr/datasets/base-nationale-des-irve-infrastructures-de-recharge-pour-vehicules-electriques)")

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.header("Filtres")

    # Filtre 1 : Opérateur
    all_operators = sorted(data['nom_operateur'].dropna().unique())
    select_all_operators = st.checkbox("Sélectionner tous les opérateurs", value=True)
    default_ops = all_operators if select_all_operators else []
    selected_operators = st.multiselect(
        "Opérateur(s)",
        options=all_operators,
        default=default_ops
    )

    # Filtre 2 : Puissance
    min_power = int(data['puissance_nominale'].min())
    max_power = int(data['puissance_nominale'].max())
    selected_power = st.slider(
        "Puissance nominale (kW)",
        min_value=min_power,
        max_value=max_power,
        value=(min_power, max_power)
    )

    # Filtre 3 : Gratuité
    all_gratuite_options = ['Tous'] + list(data['gratuit'].unique())
    selected_gratuite = st.radio(
        "Borne gratuite ?",
        options=all_gratuite_options,
        index=0
    )

    st.divider()
    st.subheader("Options de la carte")
    use_dark_mode = st.toggle("Activer le mode nuit 🌙", value=False)
    map_style_to_use = 'mapbox://styles/mapbox/navigation-night-v1' if use_dark_mode else 'mapbox://styles/mapbox/navigation-day-v1'

# --- FILTRAGE DES DONNÉES ---
df_filtered = data[
    (data['nom_operateur'].isin(selected_operators)) &
    (data['puissance_nominale'] >= selected_power[0]) &
    (data['puissance_nominale'] <= selected_power[1])
]

if selected_gratuite != 'Tous':
    df_filtered = df_filtered[df_filtered['gratuit'] == selected_gratuite]

# --- CORPS DE L'APPLICATION ---

# Section 1 : Indicateurs Clés (KPIs)
st.header("📈 L'état du réseau en un coup d'œil")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        label="Nombre de Stations",
        value=f"{len(df_filtered):,}".replace(',', ' '),
        help="Nombre de stations uniques correspondant aux filtres."
    )

with kpi2:
    st.metric(
        label="Nombre total de Points de Charge (PDC)",
        value=f"{int(df_filtered['nbre_pdc'].sum()):,}".replace(',', ' '),
        help="Nombre total de points de charge (une station peut avoir plusieurs PDC)."
    )

with kpi3:
    mean_power = df_filtered['puissance_nominale'].mean()
    st.metric(
        label="Puissance Moyenne (kW)",
        value=f"{mean_power:.1f} kW" if not pd.isna(mean_power) else "N/A",
        help="Puissance nominale moyenne des PDC."
    )

st.divider()

# Section 2 : Visuels (Carte + Graphiques)
st.header("🗺️ Analyse détaillée")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Où sont les bornes ?")
    get_pydeck_map(df_filtered, map_style=map_style_to_use)

with col2:
    st.subheader("Top 10 Opérateurs")
    get_plotly_bar_chart(
        df_filtered,
        'nom_operateur',
        "Top 10 des opérateurs (par nbre de bornes)"
    )

st.subheader("Distribution des puissances (kW)")
get_plotly_hist(
    df_filtered,
    'puissance_nominale',
    "Histogramme des puissances nominales"
)

# Section 3 : Qualité des données
st.divider()
st.header("🔍 Qualité des données & Limites")
st.markdown("### Aperçu des données filtrées")
st.dataframe(df_filtered.head(10))

with st.expander("Limitations et Biais (Mis à jour)"):
    st.info("""
        - **Nettoyage :** Les données ont été nettoyées...
        - **Puissance :** Les outliers (au-dessus du 99.9e percentile) ont été exclus.
        - **Opérateurs :** Les noms ont été normalisés.
    """)
