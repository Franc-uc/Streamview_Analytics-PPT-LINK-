"""Barra lateral: logo, filtros globales, reset e información."""
import pandas as pd
import streamlit as st

from . import components as UI
from . import config as C
from . import data, filters


def render_sidebar(full_df: pd.DataFrame, defaults: dict):
    """Dibuja los filtros (los widgets escriben en st.session_state, claves f_*).

    Devuelve un contenedor bajo el logo donde la app muestra el recuento filtrado.
    """
    with st.sidebar:
        UI.sidebar_logo()
        count_slot = st.container()

        UI.sidebar_title("Tipo de contenido")
        st.multiselect("Tipo de contenido", [C.MOVIE, C.SERIES], key="f_types",
                       label_visibility="collapsed", placeholder="Películas y series")

        UI.sidebar_title("Años de lanzamiento")
        low, high = defaults["f_years"]
        if low < high:
            st.slider("Años", low, high, key="f_years", label_visibility="collapsed")
        else:
            st.caption(f"Los datos solo contienen el año {low}.")

        UI.sidebar_title("Género")
        st.multiselect("Género", data.genre_options(full_df), key="f_genres",
                       label_visibility="collapsed", placeholder="Todos los géneros")

        UI.sidebar_title("Buscar título")
        st.text_input("Buscar título", key="f_query", label_visibility="collapsed",
                      placeholder="Ej.: Inception, Dark…")

        UI.sidebar_title("Mínimo de votos")
        max_votes = int(min(full_df["vote_count"].max(), 5000)) or 1
        st.slider("Mínimo de votos", 0, max_votes, key="f_min_votes", label_visibility="collapsed",
                  help="Los títulos con pocos votos distorsionan las valoraciones. 0 = sin filtro.")

        UI.stretch(st.button, "Restablecer filtros", on_click=filters.reset_filters, args=(defaults,))

        with st.expander("Sobre este dashboard"):
            st.markdown(
                "**StreamView Analytics** analiza el catálogo de películas y series de Netflix a partir de dos "
                "CSV. Los filtros son globales y afectan a todas las secciones.\n\n"
                "La popularidad y los votos son métricas del dataset: **no equivalen a espectadores ni a "
                "visualizaciones**. Consulta *Overview → Calidad y alcance de los datos*."
            )
    return count_slot
