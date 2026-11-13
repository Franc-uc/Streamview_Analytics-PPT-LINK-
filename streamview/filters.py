"""Estado de los filtros globales (st.session_state) y su aplicación."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from . import config as C


@dataclass(frozen=True)
class Filters:
    """Filtros inmutables y hashables (necesario para @st.cache_data)."""
    types: tuple
    years: tuple
    genres: tuple
    query: str
    min_votes: int


def default_state(df: pd.DataFrame) -> dict:
    return {
        "f_types": [C.MOVIE, C.SERIES],
        "f_years": (int(df["release_year"].min()), int(df["release_year"].max())),
        "f_genres": [],
        "f_query": "",
        "f_min_votes": 0,
    }


def init_state(defaults: dict) -> None:
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_filters(defaults: dict) -> None:
    """Callback del botón de reset."""
    for key, value in defaults.items():
        st.session_state[key] = value


def current_filters() -> Filters:
    s = st.session_state
    return Filters(
        types=tuple(sorted(s["f_types"])),
        years=tuple(s["f_years"]),
        genres=tuple(sorted(s["f_genres"])),
        query=str(s["f_query"]).strip(),
        min_votes=int(s["f_min_votes"]),
    )


def active_filter_count(filters: Filters, defaults: dict) -> int:
    count = 0
    count += set(filters.types) != set(defaults["f_types"])
    count += tuple(filters.years) != tuple(defaults["f_years"])
    count += bool(filters.genres)
    count += bool(filters.query)
    count += filters.min_votes > 0
    return int(count)


@st.cache_data(show_spinner=False)
def apply_filters(_df: pd.DataFrame, filters: Filters, token: str) -> pd.DataFrame:
    """Aplica los filtros. `_df` no se hashea; `token` invalida la caché si cambian los datos."""
    mask = _df["type_label"].isin(filters.types)
    mask &= _df["release_year"].between(filters.years[0], filters.years[1])
    mask &= _df["vote_count"] >= filters.min_votes
    if filters.genres:
        wanted = set(filters.genres)
        mask &= _df["genres_list"].map(lambda genres: not wanted.isdisjoint(genres))
    if filters.query:
        mask &= _df["title"].str.contains(filters.query, case=False, na=False, regex=False)
    return _df[mask]
