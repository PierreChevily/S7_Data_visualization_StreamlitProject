import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px


def get_pydeck_map(df, map_style='mapbox://styles/mapbox/navigation-day-v1'):
    """
    Crée une carte Pydeck centrée sur la France avec les points des bornes.
    Utilise la clé API Mapbox des secrets Streamlit.
    """
    if df.empty:
        st.warning("Aucune donnée à afficher sur la carte pour les filtres sélectionnés.")
        return

    # Récupère la clé API
    mapbox_api_key = st.secrets.get("MAPBOX_API_KEY")

    view_state = pdk.ViewState(
        latitude=46.71109,
        longitude=1.71910,
        zoom=5,
        pitch=50,
        min_zoom=4,
        max_zoom=12
    )

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df[['lon', 'lat', 'nom_station']],
        get_position='[lon, lat]',
        get_color='[255, 0, 0, 180]',
        get_radius=250,
        stroked=True,
        get_line_color=[255, 255, 255, 100],
        get_line_width=3,
        auto_highlight=True,
        pickable=True
    )

    tooltip = {
        "html": "<b>{nom_station}</b><br/>Lat: {lat}<br/>Lon: {lon}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    deck = pdk.Deck(
        map_style=map_style,
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip,
        api_keys={'mapbox': mapbox_api_key}
    )
    st.pydeck_chart(deck, width='stretch')


def get_plotly_bar_chart(df, column, title):
    if df.empty or column not in df:
        st.warning(f"Aucune donnée à afficher pour : {title}")
        return

    # Compter les valeurs
    data_counts = df[column].value_counts().head(10).reset_index()
    data_counts.columns = [column, 'count']

    fig = px.bar(
        data_counts,
        x=column,
        y='count',
        title=title,
        labels={column: column, 'count': 'Nombre de bornes'}
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig, width='stretch')


def get_plotly_hist(df, column, title):
    if df.empty or df[column].isnull().all():
        st.warning(f"Aucune donnée de puissance à afficher pour : {title}")
        return

    max_val = df[column].max()
    if pd.isna(max_val) or max_val == 0:
        max_val = 10

    # Création de l'histogramme avec Plotly
    fig = px.histogram(
        df,
        x=column,
        nbins=20,  # Nombre de "bacs"
        title=title,
        labels={column: 'Puissance (kW)'}
    )
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, width='stretch')