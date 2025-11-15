import streamlit as st
import pandas as pd


@st.cache_data(show_spinner="Chargement et nettoyage des données...")
def load_and_clean_data(csv_path):
    """
    Charge les données depuis un CSV et lance le pipeline de nettoyage complet.
    """
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except FileNotFoundError:
        st.error(f"Erreur : Le fichier '{csv_path}' est introuvable.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur inattendue lors du chargement des données : {e}")
        return pd.DataFrame()

    from .prep import clean_data
    return clean_data(df)