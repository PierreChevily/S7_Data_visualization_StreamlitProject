import pandas as pd


def clean_location(df):
    """Nettoie et valide les données de géolocalisation."""
    df.rename(columns={
        'consolidated_latitude': 'lat',
        'consolidated_longitude': 'lon'
    }, inplace=True)

    df.dropna(subset=['lat', 'lon'], inplace=True)
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df.dropna(subset=['lat', 'lon'], inplace=True)
    return df


def clean_numerical_data(df):
    """Nettoie les colonnes numériques et filtre les outliers."""
    df['puissance_nominale'] = pd.to_numeric(df['puissance_nominale'], errors='coerce')
    df['nbre_pdc'] = pd.to_numeric(df['nbre_pdc'], errors='coerce')

    if not df['puissance_nominale'].empty:
        p_999 = df['puissance_nominale'].quantile(0.999)
        df = df[(df['puissance_nominale'] <= p_999) | (df['puissance_nominale'].isna())].copy()

    return df


def clean_text_data(df):
    """Normalise les colonnes de texte (ex: opérateurs)."""
    df['nom_operateur'] = df['nom_operateur'].fillna('Inconnu')
    df['nom_operateur'] = df['nom_operateur'].astype(str).str.strip().str.upper()
    return df


def clean_categorical_data(df):
    """Nettoie et standardise les colonnes catégorielles."""
    # On convertit tout en string pour éviter les problèmes de type
    df['gratuit'] = df['gratuit'].astype(str).str.strip().str.lower()

    mapping = {
        'true': 'Oui',
        '1': 'Oui',
        'oui': 'Oui',
        'false': 'Non',
        '0': 'Non',
        'non': 'Non'
    }

    df['gratuit'] = df['gratuit'].map(mapping)
    df['gratuit'] = df['gratuit'].fillna('Inconnu')
    return df


def clean_temporal_data(df):
    """Nettoie et convertit les colonnes de date."""
    df['date_mise_en_service'] = pd.to_datetime(df['date_mise_en_service'], errors='coerce')
    return df


def feature_engineer_power(df):
    """Crée des catégories de puissance parlantes."""
    bins = [0, 11, 50, 150, float('inf')]
    labels = ['Charge Lente (<11kW)', 'Charge Accélérée (11-50kW)', 'Charge Rapide (50-150kW)',
              'Charge Ultra-Rapide (>150kW)']

    df['categorie_puissance'] = pd.cut(
        df['puissance_nominale'],
        bins=bins,
        labels=labels,
        right=False  # 11kW est dans [11-50kW)
    )
    df['categorie_puissance'] = df['categorie_puissance'].cat.add_categories('Inconnue').fillna('Inconnue')
    return df


def feature_engineer_time(df):
    """Extrait l'année de mise en service."""
    df['annee_mes'] = df['date_mise_en_service'].dt.year.fillna(0).astype(int)
    df['annee_mes'] = df['annee_mes'].replace(0, pd.NA)
    return df


def feature_engineer_geo(df):
    """Extrait le code département depuis le code INSEE."""
    # Le code INSEE (ex: '75010') doit être un str
    # On s'assure qu'il est sur 5 caractères (ex: '1001' devient '01001')
    # On prend les 2 premiers chiffres (ex: '01' pour l'Ain)
    df['code_departement'] = df['code_insee_commune'].astype(str).str.zfill(5).str[:2]
    # Gérer les codes Corse '2A' et '2B' (qui sont '20' dans le code INSEE)
    df.loc[df['code_departement'] == '20', 'code_departement'] = df['code_insee_commune'].str[:2]
    return df


def clean_data(df):
    """
    Pipeline principal de nettoyage et de préparation.
    """
    df = clean_location(df)
    df = clean_numerical_data(df)
    df = clean_text_data(df)
    df = clean_categorical_data(df)
    df = clean_temporal_data(df)

    df = feature_engineer_power(df)
    df = feature_engineer_time(df)
    df = feature_engineer_geo(df)

    return df