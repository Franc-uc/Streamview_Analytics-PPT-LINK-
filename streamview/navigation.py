"""Navegación entre secciones (estado en st.session_state['nav'])."""
import streamlit as st

from . import config as C


def render_nav() -> str:
    """Barra de navegación en píldoras. Solo se renderiza la sección activa."""
    st.session_state.setdefault("nav", C.SECTIONS[0])
    return st.radio(
        "Sección",
        C.SECTIONS,
        key="nav",
        horizontal=True,
        label_visibility="collapsed",
    )
