import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Data Storytelling IRVE",
    layout="wide"
)

# On utilise st.cache_data pour la performance
@st.cache_data(show_spinner="Chargement des données...")
def load_data(csv_path):
    # Charger les données
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error(f"Erreur : Le fichier '{csv_path}' est introuvable. Assurez-vous qu'il est dans le bon dossier.")
        return pd.DataFrame()

    clean_data(df)
    return df

def clean_location(df):
    df.rename(columns={
        'consolidated_latitude': 'lat',
        'consolidated_longitude': 'lon'
    }, inplace=True)

    # On supprime les lignes où la géolocalisation est manquante
    df.dropna(subset=['lat', 'lon'], inplace=True)
    return df

def clean_numerical_data(df):
    df['puissance_nominale'] = pd.to_numeric(df['puissance_nominale'], errors='coerce')
    df['nbre_pdc'] = pd.to_numeric(df['nbre_pdc'], errors='coerce')
    return df

def clean_data(df):
    clean_location(df)
    clean_numerical_data(df)

    # Clean boolean data
    df['gratuit'] = df['gratuit'].map({True: 'Oui', False: 'Non', np.nan: 'Inconnu'})

    # Clean date data
    df['date_mise_en_service'] = pd.to_datetime(df['date_mise_en_service'], errors='coerce')
    return df

data = load_data('consolidation-etalab-schema-irve-statique-v-2.3.1-20251110.csv')

if data.empty:
    st.stop()  # Arrêter l'exécution si les données n'ont pas chargé

st.title("Data Storytelling : Le réseau de bornes de recharge (IRVE) en France")
st.caption("Source : data.gouv.fr (https://www.data.gouv.fr/datasets/base-nationale-des-irve-infrastructures-de-recharge-pour-vehicules-electriques)")

# --- BARRE LATÉRALE (SIDEBAR)
with st.sidebar:
    st.header("Filtres")

    # Filtre 1 : Opérateur (Multi-sélection)
    all_operators = sorted(data['nom_operateur'].dropna().unique())
    selected_operators = st.multiselect(
        "Opérateur(s)",
        options=all_operators,
        default=all_operators
    )

    # Filtre 2 : Puissance (Slider)
    min_power = int(data['puissance_nominale'].min())
    max_power = int(data['puissance_nominale'].max())

    selected_power = st.slider(
        "Puissance nominale (kW)",
        min_value=min_power,
        max_value=max_power,
        value=(min_power, max_power)  # range slider
    )

    # Filtre 3 : Gratuité (Boutons radio)
    all_gratuite_options = ['Tous'] + list(data['gratuit'].unique())
    selected_gratuite = st.radio(
        "Borne gratuite ?",
        options=all_gratuite_options,
        index=0  # 'Tous' est sélectionné par défaut
    )

# --- FILTRAGE DES DONNÉES ---
# 1. Filtre Opérateur
df_filtered = data[data['nom_operateur'].isin(selected_operators)]

# 2. Filtre Puissance
df_filtered = df_filtered[
    (df_filtered['puissance_nominale'] >= selected_power[0]) &
    (df_filtered['puissance_nominale'] <= selected_power[1])
]

# 3. Filtre Gratuité
if selected_gratuite != 'Tous':
    df_filtered = df_filtered[df_filtered['gratuit'] == selected_gratuite]

# --- CORPS DE L'APPLICATION ---

# Section 1 : Indicateurs Clés (KPIs)
st.header("📈 L'état du réseau en un coup d'œil")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        label="Nombre de Stations",
        value=f"{len(df_filtered):,}".replace(',', ' '),  # Formate le nombre
        help="Nombre de stations uniques correspondant aux filtres."
    )

with kpi2:
    st.metric(
        label="Nombre total de Points de Charge (PDC)",
        value=f"{int(df_filtered['nbre_pdc'].sum()):,}".replace(',', ' '),
        help="Nombre total de points de charge (une station peut avoir plusieurs PDC)."
    )

with kpi3:
    st.metric(
        label="Puissance Moyenne (kW)",
        value=f"{df_filtered['puissance_nominale'].mean():.1f} kW",
        help="Puissance nominale moyenne des PDC."
    )

# Séparateur visuel
st.divider()

# Section 2 : Visuels (Carte + Graphiques)
st.header("🗺️ Analyse détaillée")

# On divise l'espace en 2 colonnes pour mettre la carte et un graphique côte à côte
col1, col2 = st.columns([2, 1])  # La colonne 1 est 2x plus large

with col1:
    st.subheader("Où sont les bornes ?")
    if df_filtered.empty:
        st.warning("Aucune donnée à afficher sur la carte pour les filtres sélectionnés.")
    else:
        st.map(df_filtered[['lat', 'lon']], zoom=5)

with col2:
    st.subheader("Top 5 Opérateurs")
    if df_filtered.empty:
        st.warning("Aucune donnée à afficher.")
    else:
        top_operators = df_filtered['nom_operateur'].value_counts().head(5)
        st.bar_chart(top_operators)

# Un autre graphique sur la pleine largeur
st.subheader("Distribution des puissances (kW)")
if df_filtered.empty:
    st.warning("Aucune donnée à afficher.")
else:
    power_counts = df_filtered['puissance_nominale'].value_counts().sort_index()
    st.bar_chart(power_counts)

# Section 3 : Qualité des données
st.divider()
st.header("🔍 Qualité des données & Limites")
st.markdown("### Aperçu des données filtrées")
st.dataframe(df_filtered.head(10))

with st.expander("Limitations et Biais (Exemple)"):
    st.info("""
        - **Nettoyage :** Les données ont été nettoyées au minimum. Les lignes sans coordonnées GPS ont été supprimées.
        - **Puissance :** Les 'puissances nominales' non valides ont été ignorées.
    """)

# Section 4 : Conclusion et Étapes Suivantes
# st.header("💡 Conclusions (à venir)")
# st.success("""
#     **Premiers Insights (à développer) :**
#     1. Le réseau semble...
#     2. Les opérateurs dominants sont...
#     3. La puissance moyenne indique une tendance vers...
# """)