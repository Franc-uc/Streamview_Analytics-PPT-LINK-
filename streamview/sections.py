"""Las ocho secciones del dashboard. Cada `render_*` recibe el DataFrame ya filtrado."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from . import charts as G
from . import components as UI
from . import config as C
from . import metrics as M
from .utils import fmt_compact, fmt_float, fmt_int

NO_DATA = "Ajusta los filtros de la barra lateral o pulsa «Restablecer filtros»."


# --- 1. Overview ------------------------------------------------------------
def render_overview(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    UI.section_header(
        "Overview",
        "Resumen ejecutivo del catálogo audiovisual (métricas TMDB; sin telemetría interna de usuarios)",
    )
    if df.empty:
        UI.empty_state(NO_DATA)
    else:
        UI.render_kpis(M.kpis(df), len(full_df))
        UI.gap()
        left, right = st.columns([1.7, 1])
        with left, UI.card("ov_trend"):
            UI.show_chart(G.fig_metric_trend(df, "popularity"), "ov_trend")
        with right, UI.card("ov_donut"):
            UI.show_chart(G.fig_type_donut(df), "ov_donut")
        UI.section_header("Hallazgos clave", "Calculados sobre la selección actual")
        UI.render_insights(M.build_insights(df))

    UI.gap(18)
    with st.expander("Calidad y alcance de los datos"):
        for text in M.data_quality_notes(full_df):
            st.markdown(f"- {text}")


# --- 2. Content analytics ---------------------------------------------------
def render_content(df: pd.DataFrame) -> None:
    UI.section_header("Content Analytics", "Qué hay en el catálogo y cómo se reparte")
    if df.empty:
        return UI.empty_state(NO_DATA)

    left, right = st.columns([1, 1.5])
    with left, UI.card("ct_donut"):
        UI.show_chart(G.fig_type_donut(df), "ct_donut")
    with right, UI.card("ct_genres"):
        UI.show_chart(G.fig_top_genres(df), "ct_genres")

    UI.gap()
    with UI.card("ct_treemap"):
        UI.show_chart(G.fig_genre_treemap(df), "ct_treemap")

    UI.gap()
    with UI.card("ct_rank"):
        metric = st.radio("Ordenar el ranking por", ["popularity", "vote_count", "weighted_rating"],
                          format_func=M.RANK_METRICS.get, horizontal=True, key="content_rank_metric")
        if metric == "weighted_rating":
            UI.note("La valoración ponderada combina la nota y el número de votos para que un título "
                    "con pocos votos no supere a otro con miles.")
        UI.show_chart(G.fig_top_titles(df, metric), "ct_rank")

    UI.gap()
    with UI.card("ct_compare"):
        st.markdown("**Películas frente a series**")
        UI.render_summary_table(M.type_summary(df))

    UI.gap()
    left, right = st.columns([1, 1.4])
    with left, UI.card("ct_box"):
        UI.show_chart(G.fig_popularity_box(df), "ct_box")
    with right, UI.card("ct_genre_pop"):
        UI.show_chart(G.fig_genre_popularity(df), "ct_genre_pop")


# --- 3. Geography & Talent --------------------------------------------------
def render_geography(df: pd.DataFrame) -> None:
    UI.section_header(
        "Geography & Talent",
        "Distribución por países productores, valoración por mercado, idiomas originales, directores y reparto",
    )
    if df.empty:
        return UI.empty_state(NO_DATA)

    n_countries = df["country_list"].explode().dropna().nunique()
    n_langs = df["language"].dropna().nunique()
    dirs_series = df["director"].dropna().astype(str).str.split(",").explode().str.strip()
    n_dirs = dirs_series[dirs_series != ""].nunique()
    stats = [
        ("Países representados", fmt_int(n_countries), "Mercados productores en la selección", "GEO"),
        ("Idiomas originales", fmt_int(n_langs), "Diversidad lingüística del catálogo", "IDIOMA"),
        ("Directores únicos", fmt_int(n_dirs), "Talento de dirección identificado", "TALENTO"),
    ]
    UI.render_stat_grid(stats)
    UI.gap()

    left, right = st.columns(2)
    with left, UI.card("geo_countries"):
        UI.show_chart(G.fig_top_countries(df, 10), "geo_countries")
    with right, UI.card("geo_langs"):
        UI.show_chart(G.fig_top_languages(df, 10), "geo_langs")

    UI.gap()
    with UI.card("geo_quality"):
        q_metric = st.radio(
            "Desempeño por país productor (mín. 100 títulos en catálogo completo)",
            ["rating_mean", "pop_med"],
            format_func={"rating_mean": "Valoración media (0–10)", "pop_med": "Popularidad mediana (TMDB)"}.get,
            horizontal=True,
            key="geo_quality_metric",
        )
        UI.show_chart(G.fig_country_quality(df, metric=q_metric, n=10, min_titles=100), "geo_quality")

    UI.gap()
    left, right = st.columns(2)
    with left, UI.card("geo_directors"):
        UI.show_chart(G.fig_top_people(df, "director", 10), "geo_directors", "Sin datos de dirección.")
    with right, UI.card("geo_cast"):
        UI.show_chart(G.fig_top_people(df, "cast", 10), "geo_cast", "Sin datos de reparto.")


# --- 4. Temporal analytics --------------------------------------------------
def render_temporal(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    UI.section_header("Temporal Analytics", "Evolución del catálogo por año de lanzamiento")
    if df.empty:
        return UI.empty_state(NO_DATA)

    size = M.balanced_yearly_size(full_df)
    if size:
        UI.note(f"Este dataset tiene exactamente {fmt_int(size)} títulos por año y tipo, así que el conteo anual "
                "es plano por construcción y no indica crecimiento real. Las métricas por año (popularidad, "
                "votos, valoración) sí muestran evolución.")

    left, right = st.columns([1.5, 1])
    with left, UI.card("tp_area"):
        UI.show_chart(G.fig_releases_area(df), "tp_area")
    with right, UI.card("tp_years"):
        UI.show_chart(G.fig_top_years(df), "tp_years")

    UI.gap()
    with UI.card("tp_trend"):
        c1, c2 = st.columns([2.2, 1])
        metric = c1.radio("Métrica", list(M.TREND_METRICS), format_func=M.TREND_METRICS.get,
                          horizontal=True, key="trend_metric")
        index100 = c2.toggle("Comparar crecimiento (base 100)", key="trend_index",
                             help="Cada tipo parte de 100 en su primer año para comparar ritmos de cambio.")
        UI.show_chart(G.fig_metric_trend(df, metric, index100), "tp_trend")

    UI.gap()
    with UI.card("tp_heat"):
        UI.show_chart(G.fig_month_heatmap(df), "tp_heat", "No hay fechas de lanzamiento válidas.")


# --- 5. Engagement analytics ------------------------------------------------
def _spearman(df: pd.DataFrame, a: str, b: str):
    sub = df[[a, b]].dropna()
    sub = sub[(sub[a] > 0) & (sub[b] > 0)]
    if len(sub) < 10:
        return None
    return sub.rank().corr().iloc[0, 1]


def render_engagement(df: pd.DataFrame) -> None:
    UI.section_header(
        "Engagement Analytics",
        "Recepción pública (popularidad, votos y valoraciones TMDB). No mide reproducciones ni retención de usuarios",
    )
    if df.empty:
        return UI.empty_state(NO_DATA)

    left, right = st.columns([1.7, 1])
    with left, UI.card("en_scatter"):
        UI.show_chart(G.fig_scatter_engagement(df), "en_scatter", "No hay títulos con votos y popularidad.")
        st.caption(f"Se muestran hasta {fmt_int(C.SCATTER_MAX_POINTS)} títulos con votos (los 200 más populares "
                   "más una muestra aleatoria).")
    with right:
        overall = _spearman(df, "popularity", "vote_count")
        stats = [("Correlación popularidad–votos", fmt_float(overall, 2) if overall is not None else "—",
                  "Spearman, todos los tipos", "GLOBAL")]
        for label in (C.MOVIE, C.SERIES):
            value = _spearman(df[df["type_label"] == label], "popularity", "vote_count")
            if value is not None:
                stats.append((f"{C.TYPE_PLURAL[label]}", fmt_float(value, 2),
                              "Spearman popularidad–votos", "CINE" if label == C.MOVIE else "TV"))
        UI.render_stat_grid(stats)
        if overall is not None and overall < 0:
            UI.note("Paradoja de Simpson detectada: al mezclar películas y series, la correlación global es negativa "
                    "aunque por separado ambas son positivas. Esto confirma la Regla de Negocio 2: las escalas de "
                    "popularidad de películas y series no deben compararse de forma agregada.")
        UI.gap()
        with UI.card("en_table"):
            st.markdown("**Películas frente a series**")
            summary = M.type_summary(df)
            if not summary.empty:
                summary = summary[["Votos totales", "Votos (mediana)", "% con votos", "Valoración media"]]
            UI.render_summary_table(summary)

    UI.gap()
    left, right = st.columns(2)
    with left, UI.card("en_pop_hist"):
        UI.show_chart(G.fig_popularity_hist(df), "en_pop_hist")
    with right, UI.card("en_rating_hist"):
        UI.show_chart(G.fig_rating_hist(df), "en_rating_hist", "No hay títulos con valoración.")

    UI.gap()
    left, right = st.columns(2)
    with left, UI.card("en_corr"):
        scope = st.radio("Ámbito", ["Todo", C.MOVIE, C.SERIES], horizontal=True, key="corr_scope")
        part = df if scope == "Todo" else df[df["type_label"] == scope]
        columns = ["popularity", "vote_count", "rating_clean", "release_year"]
        if scope == C.MOVIE:
            columns += ["budget_clean", "revenue_clean"]
        UI.show_chart(G.fig_corr_heatmap(M.corr_matrix(part, columns)), "en_corr",
                      "No hay suficientes datos para calcular correlaciones.")
    with right, UI.card("en_rank"):
        metric = st.radio("Recepción pública medida por", ["vote_count", "weighted_rating"],
                          format_func=M.RANK_METRICS.get, horizontal=True, key="engagement_metric")
        UI.show_chart(G.fig_top_titles(df, metric), "en_rank")


# --- 6. Financial analytics (Películas) -------------------------------------
def render_financial(df: pd.DataFrame) -> None:
    UI.section_header("Financial Analytics",
                      "Presupuesto, recaudación y retorno sobre inversión (ROI) en el catálogo de películas")
    movies = df[df["type_label"] == C.MOVIE]
    if movies.empty:
        return UI.empty_state("Las variables financieras (presupuesto e ingresos) están disponibles "
                              "exclusivamente para Películas (Regla de Negocio 3). Activa «Película» en el filtro lateral.")

    fk = M.financial_kpis(df)
    UI.note("Conforme a las Reglas de Negocio 3, 6 y 9, los indicadores financieros se calculan únicamente sobre "
            "las películas con registros válidos de presupuesto e ingresos (> 0 USD).")

    stats = [
        ("Películas con datos financieros", fmt_int(fk["count_fin"]), "Con presupuesto e ingresos > 0", "MUESTRA"),
        ("Presupuesto promedio", f"${fmt_compact(fk['avg_budget'])}" if fk["avg_budget"] else "—",
         f"Total: ${fmt_compact(fk['total_budget'])}", "COSTO"),
        ("Ingresos totales (Taquilla)", f"${fmt_compact(fk['total_revenue'])}", "Recaudación acumulada", "TAQUILLA"),
        ("ROI global de cartera", f"{fmt_float(fk['global_roi'], 2)}×" if fk["global_roi"] else "—",
         f"ROI mediano: {fmt_float(fk['median_roi'], 2)}× por película", "RETORNO"),
    ]
    UI.render_stat_grid(stats)
    UI.gap()

    left, right = st.columns([1.3, 1])
    with left, UI.card("fin_scatter"):
        UI.show_chart(G.fig_budget_vs_revenue(df), "fin_scatter", "Sin datos financieros en la selección.")
    with right, UI.card("fin_genre_roi"):
        UI.show_chart(G.fig_genre_roi(df, 10), "fin_genre_roi", "Sin suficientes películas por género para calcular ROI.")

    UI.gap()
    with UI.card("fin_rank"):
        fin_metric = st.radio("Ordenar ranking financiero de películas por",
                              ["revenue_clean", "roi"],
                              format_func=M.FIN_RANK_METRICS.get, horizontal=True, key="fin_rank_metric")
        if fin_metric == "roi":
            UI.note("Para el ranking de ROI se consideran películas con presupuesto ≥ $1,0 M USD, "
                    "evitando distorsiones por registros con micro-presupuestos.")
        UI.show_chart(G.fig_top_titles(movies, fin_metric, 10), "fin_rank")


# --- 7. Content explorer ----------------------------------------------------
_TABLE_COLUMNS = {
    "title": "Título", "type_label": "Tipo", "release_year": "Año", "genres": "Géneros", "country": "País",
    "language": "Idioma", "popularity": "Popularidad", "vote_count": "Votos", "rating_clean": "Valoración",
    "director": "Dirección", "cast": "Reparto", "description": "Descripción",
}
_SORTS = {"Popularidad": "popularity", "Año": "release_year", "Votos": "vote_count",
          "Valoración": "rating_clean", "Título": "title"}
_EXPORT_DROP = ["genres_list", "country_list", "has_votes"]


def render_explorer(df: pd.DataFrame) -> None:
    UI.section_header("Content Explorer", "Busca, ordena y exporta el catálogo filtrado")
    if df.empty:
        return UI.empty_state(NO_DATA)

    with UI.card("ex_controls"):
        c1, c2, c3, c4 = st.columns([1.3, 1.2, 1.1, 1.6])
        kind = c1.radio("Tipo", ["Todos", C.MOVIE, C.SERIES], horizontal=True, key="ex_kind")
        sort_label = c2.selectbox("Ordenar por", list(_SORTS), key="ex_sort")
        order = c3.radio("Orden", ["Descendente", "Ascendente"], horizontal=True, key="ex_order")
        languages = sorted(df["language"].dropna().unique())
        chosen_langs = c4.multiselect("Idioma", languages, key="ex_langs", placeholder="Todos los idiomas")
        only_voted = st.checkbox("Solo títulos con votos", key="ex_voted")

    view = df
    if kind != "Todos":
        view = view[view["type_label"] == kind]
    if chosen_langs:
        view = view[view["language"].isin(chosen_langs)]
    if only_voted:
        view = view[view["has_votes"]]
    if view.empty:
        return UI.empty_state("Ningún título cumple los filtros del explorador.")

    view = view.sort_values(_SORTS[sort_label], ascending=(order == "Ascendente"), na_position="last")
    view = view.reset_index(drop=True)

    top, right = st.columns([3, 1])
    limit = top.select_slider("Filas mostradas en la tabla", [250, 500, 1000, 2000, 5000], value=1000,
                              key="ex_limit", help="La descarga siempre incluye todas las filas filtradas.")
    csv = view.drop(columns=_EXPORT_DROP, errors="ignore").to_csv(index=False).encode("utf-8-sig")
    right.download_button(f"Descargar CSV ({fmt_int(len(view))})", csv, "streamview_catalogo_filtrado.csv",
                          "text/csv", key="ex_download")

    shown = view.head(limit)
    table = shown[list(_TABLE_COLUMNS)].rename(columns=_TABLE_COLUMNS)
    pop_max = float(view["popularity"].quantile(0.99) or 1)
    config = {
        "Año": st.column_config.NumberColumn(format="%d"),
        "Popularidad": st.column_config.ProgressColumn(min_value=0, max_value=pop_max, format="%.1f"),
        "Votos": st.column_config.NumberColumn(format="%d"),
        "Valoración": st.column_config.ProgressColumn(min_value=0, max_value=10, format="%.1f"),
        "Descripción": st.column_config.TextColumn(width="large"),
    }
    event = UI.stretch(st.dataframe, table, hide_index=True, height=520, column_config=config,
                       on_select="rerun", selection_mode="single-row", key="ex_table")
    st.caption(f"Mostrando {fmt_int(len(shown))} de {fmt_int(len(view))} títulos. "
               "Selecciona una fila para ver su ficha.")

    selected = list(getattr(getattr(event, "selection", None), "rows", []) or [])
    if selected and selected[0] < len(shown):
        row = shown.iloc[selected[0]].copy()
        row["score"] = row["popularity"]
        UI.gap()
        with UI.card("ex_detail"):
            UI.render_feature(row, "popularity", "Popularidad", "Título seleccionado")


# --- 8. Top content ---------------------------------------------------------
def render_top(df: pd.DataFrame) -> None:
    UI.section_header("Top Content", "Los títulos que lideran la selección actual")
    if df.empty:
        return UI.empty_state(NO_DATA)

    metric = st.radio("Clasificar por", list(M.RANK_METRICS), format_func=M.RANK_METRICS.get,
                      horizontal=True, key="top_metric")
    if metric == "vote_count":
        UI.note("Los votos miden cuántas personas valoraron un título, no cuántas lo vieron.")

    groups = [(C.MOVIE, "Películas"), (C.SERIES, "Series")]
    rankings = {label: M.rank_titles(df[df["type_label"] == label], metric, 10) for label, _ in groups}

    for label, plural in groups:
        ranked = rankings[label]
        UI.section_header(f"Top 10 · {plural}")
        if ranked.empty:
            UI.empty_state(f"No hay {plural.lower()} en la selección actual.")
            continue
        with UI.card(f"top_feature_{label}"):
            UI.render_feature(ranked.iloc[0], metric, M.RANK_METRICS[metric],
                              f"{label} número 1 por {M.RANK_METRICS[metric].lower()}")
        UI.gap()
        UI.render_poster_grid(ranked, metric)
