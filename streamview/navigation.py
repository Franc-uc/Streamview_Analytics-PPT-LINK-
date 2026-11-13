"""Navegación entre secciones (estado en st.session_state['nav'])."""
import streamlit as st

from . import config as C

_ICONS = {
    "Overview": "◈ Overview",
    "Content Analytics": "▤ Content Analytics",
    "Temporal Analytics": "◷ Temporal Analytics",
    "Engagement Analytics": "◎ Engagement Analytics",
    "Content Explorer": "⌕ Content Explorer",
    "Top Content": "★ Top Content",
}


def render_nav() -> str:
    """Barra de navegación en píldoras. Solo se renderiza la sección activa."""
    st.session_state.setdefault("nav", C.SECTIONS[0])
    return st.radio("Sección", C.SECTIONS, key="nav", horizontal=True,
                    format_func=lambda s: _ICONS.get(s, s), label_visibility="collapsed")
