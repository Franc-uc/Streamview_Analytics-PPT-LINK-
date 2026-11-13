"""StreamView Analytics: punto de entrada. Ejecutar con `streamlit run app.py`."""
import streamlit as st

st.set_page_config(page_title="StreamView Analytics", page_icon="🎬", layout="wide",
                   initial_sidebar_state="expanded")

from streamview import components as UI  # noqa: E402  (set_page_config debe ir primero)
from streamview import data, filters, sections  # noqa: E402
from streamview.navigation import render_nav  # noqa: E402
from streamview.sidebar import render_sidebar  # noqa: E402
from streamview.styles import inject_css  # noqa: E402


def main() -> None:
    inject_css()

    try:
        token = data.files_token()
        full_df = data.load_data(token)
    except data.DataError as exc:
        st.error(str(exc))
        st.stop()

    defaults = filters.default_state(full_df)
    filters.init_state(defaults)
    count_slot = render_sidebar(full_df, defaults)

    df = filters.apply_filters(full_df, filters.current_filters(), token)
    with count_slot:
        UI.sidebar_count(len(df), len(full_df))

    UI.render_header(full_df)
    section = render_nav()
    UI.gap(6)

    renderers = {
        "Overview": lambda: sections.render_overview(df, full_df),
        "Content Analytics": lambda: sections.render_content(df),
        "Temporal Analytics": lambda: sections.render_temporal(df, full_df),
        "Engagement Analytics": lambda: sections.render_engagement(df),
        "Content Explorer": lambda: sections.render_explorer(df),
        "Top Content": lambda: sections.render_top(df),
    }
    try:
        renderers[section]()
    except Exception as exc:  # una sección rota no debe tumbar toda la app
        st.error(f"No se pudo mostrar la sección «{section}»: {exc}")
        st.exception(exc)


main()
