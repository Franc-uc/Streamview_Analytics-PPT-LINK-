"""Componentes visuales reutilizables (HTML + Streamlit)."""
from __future__ import annotations

import zlib

import pandas as pd
import streamlit as st

from . import config as C
from .utils import esc, fmt_compact, fmt_float, fmt_int, fmt_pct, html_block, safe_div

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}

# Fondos degradados para las tarjetas sin póster (la elección depende del género principal).
_POSTER_BACKGROUNDS = [
    "linear-gradient(160deg,#7A0C14,#1A0A0B 72%)",
    "linear-gradient(160deg,#4A1030,#150A12 72%)",
    "linear-gradient(160deg,#0F3550,#091219 72%)",
    "linear-gradient(160deg,#5A3A0A,#171008 72%)",
    "linear-gradient(160deg,#0F4A35,#08130F 72%)",
    "linear-gradient(160deg,#3A3A3A,#0E0E0E 72%)",
]


def stretch(fn, *args, **kwargs):
    """Llama a un componente a ancho completo, compatible con versiones nuevas y antiguas de Streamlit."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except Exception:
        return fn(*args, use_container_width=True, **kwargs)


def card(name: str):
    """Contenedor con estilo de tarjeta (se estiliza por la clase `st-key-card_<name>`)."""
    return st.container(key=f"card_{name}")


def show_chart(fig, key: str, empty_message: str = "No hay datos con los filtros actuales.") -> None:
    if fig is None:
        empty_state(empty_message)
        return
    stretch(st.plotly_chart, fig, key=key, theme=None, config=PLOT_CONFIG)


def empty_state(message: str = "No hay datos con los filtros actuales.") -> None:
    st.markdown(html_block(f'<div class="sv-empty"><b>Sin resultados</b>{esc(message)}</div>'),
                unsafe_allow_html=True)


def note(text: str) -> None:
    st.markdown(f'<div class="sv-note">{esc(text)}</div>', unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    st.markdown(html_block(f'<div class="sv-section"><h2>{esc(title)}</h2>{sub}</div>'),
                unsafe_allow_html=True)


# --- Cabecera y barra lateral -------------------------------------------------
def render_header(full_df: pd.DataFrame) -> None:
    years = f"{int(full_df['release_year'].min())}–{int(full_df['release_year'].max())}"
    st.markdown(html_block(f"""
    <div class="sv-hero">
      <div>
        <div class="sv-logo"><span class="brand">STREAMVIEW</span><span class="product">ANALYTICS</span></div>
        <div class="tagline">{esc(C.APP_SUBTITLE)}: géneros, geografía, popularidad, valoraciones y rentabilidad cinematográfica.</div>
      </div>
      <div class="side">
        <span class="sv-badge"><span class="dot"></span>Business Intelligence Platform</span>
        <div class="sv-chips">
          <span class="sv-chip">{fmt_int(len(full_df))} títulos</span>
          <span class="sv-chip">{years}</span>
          <span class="sv-chip">Películas y series</span>
        </div>
      </div>
    </div>"""), unsafe_allow_html=True)


def sidebar_logo() -> None:
    st.markdown('<div class="sv-side-logo">STREAMVIEW<span>ANALYTICS</span></div>', unsafe_allow_html=True)


def sidebar_title(text: str) -> None:
    st.markdown(f'<div class="sv-side-title">{esc(text)}</div>', unsafe_allow_html=True)


def sidebar_count(filtered: int, total: int) -> None:
    share = fmt_pct((safe_div(filtered, total, 0) or 0) * 100)
    st.markdown(f'<div class="sv-side-count"><b>{fmt_int(filtered)}</b> de {fmt_int(total)} títulos ({share})</div>',
                unsafe_allow_html=True)


# --- KPIs -------------------------------------------------------------------
def _kpi(label: str, value: str, sub: str = "", delta=None, tag: str = "") -> str:
    delta_html = ""
    if delta is not None:
        pct, ref = delta
        css = "up" if pct >= 0 else "down"
        arrow = "▲" if pct >= 0 else "▼"
        delta_html = f'<div class="delta {css}">{arrow} {fmt_pct(pct, 1, signed=True)} <span>{esc(ref)}</span></div>'
    sub_html = f'<div class="sub">{esc(sub)}</div>' if sub else ""
    tag_html = f'<span class="ktag">{esc(tag)}</span>' if tag else ""
    return (f'<div class="sv-kpi"><div class="top"><span class="label">{esc(label)}</span>'
            f'{tag_html}</div><div class="value">{esc(value)}</div>{sub_html}{delta_html}</div>')


def render_kpis(k: dict, total_full: int) -> None:
    share_of_catalog = (safe_div(k["total"], total_full, 0) or 0) * 100
    top_genre = k["top_genre"]
    cards = [
        _kpi("Total de títulos", fmt_int(k["total"]), f"{fmt_pct(share_of_catalog)} del catálogo completo", tag="CATÁLOGO"),
        _kpi("Películas", fmt_int(k["movies"]), f"{fmt_pct(k['movies_share'])} de la selección", tag="CINE"),
        _kpi("Series", fmt_int(k["series"]), f"{fmt_pct(k['series_share'])} de la selección", tag="TV"),
        _kpi("Popularidad media", fmt_float(k["avg_popularity"]), "Índice TMDB del dataset", k["popularity_delta"], tag="TMDB"),
        _kpi("Total de votos", fmt_compact(k["total_votes"]), f"{fmt_int(k['total_votes'])} votos registrados", k["votes_delta"], tag="VOTOS"),
        _kpi("Género más frecuente", top_genre[0] if top_genre else "—",
             f"{fmt_int(top_genre[1])} títulos ({fmt_pct(top_genre[2])})" if top_genre else "Sin datos", tag="TOP"),
    ]
    st.markdown(f'<div class="sv-kpis">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_stat_grid(items: list[tuple]) -> None:
    """Tarjetas sueltas: cada item es (etiqueta, valor, subtítulo) o (etiqueta, valor, subtítulo, tag)."""
    rendered = []
    for item in items:
        if len(item) == 3:
            label, value, sub = item
            rendered.append(_kpi(label, value, sub))
        else:
            label, value, sub, tag = item
            rendered.append(_kpi(label, value, sub, tag=tag))
    st.markdown(f'<div class="sv-kpis">{"".join(rendered)}</div>', unsafe_allow_html=True)


def gap(px: int = 14) -> None:
    st.markdown(f'<div style="height:{px}px"></div>', unsafe_allow_html=True)


def render_insights(items: list[dict]) -> None:
    if not items:
        return
    blocks = "".join(
        f'<div class="sv-insight"><div><b>{esc(it["title"])}</b><span>{esc(it["text"])}</span></div></div>'
        for it in items
    )
    st.markdown(f'<div class="sv-insights">{blocks}</div>', unsafe_allow_html=True)


def render_summary_table(summary: pd.DataFrame) -> None:
    """Tabla HTML comparativa películas vs series."""
    if summary.empty:
        empty_state()
        return
    formats = {"Títulos": fmt_int, "Votos totales": fmt_compact, "Votos (mediana)": fmt_int,
               "% con votos": lambda v: fmt_pct(v, 1), "Valoración media": lambda v: fmt_float(v, 2)}
    head = "".join(f"<th>{esc(t)}</th>" for t in ["Tipo", *summary.columns])
    rows = ""
    for label, row in summary.iterrows():
        cells = "".join(f"<td>{esc(formats.get(col, fmt_float)(row[col]))}</td>" for col in summary.columns)
        rows += f"<tr><td>{esc(label)}</td>{cells}</tr>"
    st.markdown(f'<div class="sv-table-wrap"><table class="sv-table"><tr>{head}</tr>{rows}</table></div>',
                unsafe_allow_html=True)


# --- Tarjetas de póster -------------------------------------------------------
def _background_for(genre: str) -> str:
    return _POSTER_BACKGROUNDS[zlib.crc32(str(genre).encode("utf-8")) % len(_POSTER_BACKGROUNDS)]


def _format_score(score: float, metric: str) -> str:
    if metric == "vote_count":
        return fmt_int(score)
    return fmt_float(score, 2 if metric == "weighted_rating" else 1)


def _bar_width(score: float, max_score: float, metric: str) -> float:
    ratio = score / 10 if metric == "weighted_rating" else safe_div(score, max_score, 0)
    return max(4.0, min(100.0, (ratio or 0) * 100))


def poster_card(row: pd.Series, rank: int, metric: str, max_score: float) -> str:
    chips = "".join(f"<i>{esc(g)}</i>" for g in list(row["genres_list"])[:2])
    meta = f'{int(row["release_year"])} · {esc(row["primary_country"])}'
    stats = f'<b>{_format_score(row["score"], metric)}</b> · {fmt_int(row["vote_count"])} votos'
    return (f'<div class="sv-poster" style="background:{_background_for(row["primary_genre"])}" title="{esc(row["title"])}">'
            f'<span class="rank">{rank}</span><span class="badge">{esc(row["type_label"])}</span>'
            f'<div class="body"><div class="title">{esc(row["title"])}</div><div class="meta">{meta}</div>'
            f'<div class="chips">{chips}</div>'
            f'<div class="sv-bar"><span style="width:{_bar_width(row["score"], max_score, metric):.0f}%"></span></div>'
            f'<div class="stats">{stats}</div></div></div>')


def render_poster_grid(ranked: pd.DataFrame, metric: str) -> None:
    if ranked.empty:
        empty_state()
        return
    max_score = ranked["score"].max()
    cards = "".join(poster_card(row, i, metric, max_score) for i, (_, row) in enumerate(ranked.iterrows(), 1))
    st.markdown(f'<div class="sv-grid">{cards}</div>', unsafe_allow_html=True)


def render_feature(row: pd.Series, metric: str, metric_label: str, kicker: str = "Título destacado") -> None:
    desc = row.get("description")
    desc = (str(desc)[:320] + "…") if isinstance(desc, str) and len(str(desc)) > 320 else desc
    desc_html = f'<div class="desc">{esc(desc)}</div>' if isinstance(desc, str) and desc else ""
    chips = "".join(f"<i>{esc(g)}</i>" for g in list(row["genres_list"])[:4])
    director = row.get("director")
    facts = [
        (metric_label, _format_score(row["score"], metric)),
        ("Votos", fmt_int(row["vote_count"])),
        ("Año", str(int(row["release_year"]))),
        ("Tipo", str(row["type_label"])),
    ]
    facts_html = "".join(f"<div><b>{esc(v)}</b>{esc(k)}</div>" for k, v in facts)
    director_html = (f'<div class="meta" style="color:#B5B5B5;font-size:.85rem">Dirección: {esc(director)}</div>'
                     if isinstance(director, str) and director else "")
    st.markdown(html_block(f"""
    <div class="sv-feature">
      <div class="sv-poster" style="background:{_background_for(row['primary_genre'])}">
        <span class="rank">1</span>
        <div class="body"><div class="chips">{chips}</div></div>
      </div>
      <div class="info">
        <div class="kicker">{esc(kicker)}</div>
        <h3>{esc(row['title'])}</h3>
        <div class="facts">{facts_html}</div>
        {desc_html}{director_html}
      </div>
    </div>"""), unsafe_allow_html=True)
