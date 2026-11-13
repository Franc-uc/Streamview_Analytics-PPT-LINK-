"""Un gráfico Plotly por función. Todas devuelven `go.Figure` o `None` si no hay datos."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config as C
from . import metrics as M
from .utils import fmt_int

FONT = "Inter, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
GRID = "rgba(255,255,255,0.07)"
TYPE_ORDER = [C.MOVIE, C.SERIES]


def _style(fig: go.Figure, title: str, height: int = 380, legend: bool = True) -> go.Figure:
    """Tema común: fondo transparente, tipografía y tooltips coherentes con el dashboard."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color="#E5E5E5", size=13),
        title=dict(text=title, x=0, xanchor="left", font=dict(size=16, color=C.WHITE)),
        margin=dict(l=8, r=8, t=56, b=8),
        height=height,
        separators=",.",
        hoverlabel=dict(bgcolor=C.BLACK_2, bordercolor=C.RED, font=dict(color=C.WHITE, size=13)),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", title_text=""),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, title_font=dict(size=12, color=C.GREY_TEXT))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, title_font=dict(size=12, color=C.GREY_TEXT))
    return fig


def _type_color(label: str) -> str:
    return C.TYPE_COLORS.get(label, C.GREY_TEXT)


# --- Content analytics ------------------------------------------------------
def fig_type_donut(df: pd.DataFrame):
    counts = df["type_label"].value_counts()
    if counts.empty:
        return None
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.68, sort=False,
        marker=dict(colors=[_type_color(x) for x in counts.index], line=dict(color=C.BLACK_2, width=3)),
        textinfo="percent", textfont=dict(color=C.WHITE, size=14),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} títulos (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{fmt_int(counts.sum())}</b><br><span style='font-size:12px;color:#999'>títulos</span>",
                       showarrow=False, font=dict(size=28, color=C.WHITE))
    return _style(fig, "Películas vs series", height=360)


def fig_top_genres(df: pd.DataFrame, n: int = 10):
    gc = M.genre_counts(df)
    if gc.empty:
        return None
    top = gc.groupby("genre")["titles"].sum().nlargest(n)
    gc = gc[gc["genre"].isin(top.index)]
    fig = px.bar(gc, x="titles", y="genre", color="type_label", orientation="h",
                 color_discrete_map=C.TYPE_COLORS,
                 category_orders={"genre": top.index[::-1].tolist(), "type_label": TYPE_ORDER})
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{fullData.name}: %{x:,.0f} títulos<extra></extra>",
                      marker_line_width=0)
    fig.update_layout(barmode="stack", bargap=0.28)
    fig.update_xaxes(title="Títulos")
    fig.update_yaxes(title="")
    return _style(fig, f"Top {len(top)} géneros", height=400)


def fig_genre_treemap(df: pd.DataFrame):
    ex = M.explode_genres(df)
    if ex.empty:
        return None
    grouped = (ex.groupby(["type_label", "genre"])
               .agg(titles=("uid", "size"), avg_pop=("popularity", "mean")).reset_index())
    grouped["avg_pop"] = grouped["avg_pop"].fillna(0)
    fig = px.treemap(grouped, path=[px.Constant("Catálogo"), "type_label", "genre"], values="titles",
                     color="avg_pop", color_continuous_scale=C.RED_SCALE)
    fig.update_traces(
        marker_line_color=C.BLACK, marker_line_width=2, root_color="rgba(0,0,0,0)",
        textinfo="label+value", textfont=dict(color=C.WHITE),
        hovertemplate="<b>%{label}</b><br>Títulos: %{value:,.0f}<br>Popularidad media: %{color:,.1f}<extra></extra>",
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Pop. media", thickness=10, len=0.7))
    return _style(fig, "Composición de géneros (tamaño: títulos, color: popularidad media)", height=460, legend=False)


def fig_top_titles(df: pd.DataFrame, metric: str = "popularity", n: int = 10):
    top = M.rank_titles(df, metric, n)
    if top.empty:
        return None
    top = top.iloc[::-1].reset_index(drop=True)
    labels = [f"{str(t)[:36]} ({int(y)})" + "\u200b" * i
              for i, (t, y) in enumerate(zip(top["title"], top["release_year"]))]
    fmt = {"popularity": ",.1f", "vote_count": ",.0f", "weighted_rating": ".2f"}[metric]
    fig = go.Figure(go.Bar(
        x=top["score"], y=labels, orientation="h",
        marker=dict(color=[_type_color(x) for x in top["type_label"]]),
        text=top["score"], texttemplate=f"%{{text:{fmt}}}", textposition="outside", cliponaxis=False,
        textfont=dict(color=C.WHITE),
        customdata=top.assign(_rating=top["rating_clean"].fillna(0))[
            ["type_label", "vote_count", "_rating"]].to_numpy(dtype=object),
        hovertemplate=("<b>%{y}</b><br>%{customdata[0]}<br>" + M.RANK_METRICS[metric] +
                       f": %{{x:{fmt}}}<br>Votos: %{{customdata[1]:,.0f}}<br>"
                       "Valoración: %{customdata[2]:.1f}<extra></extra>"),
    ))
    note = ""
    if metric == "weighted_rating":
        low = math.floor(top["score"].min() * 2 - 1) / 2
        fig.update_xaxes(range=[low, top["score"].max() * 1.04])
        note = f" (eje desde {low:g})"
    else:
        fig.update_xaxes(range=[0, top["score"].max() * 1.15])
    fig.update_layout(bargap=0.3)
    fig.update_yaxes(title="", automargin=True)
    fig.update_xaxes(title=M.RANK_METRICS[metric])
    return _style(fig, f"Top {len(top)} por {M.RANK_METRICS[metric].lower()}{note}", height=440, legend=False)


def fig_popularity_box(df: pd.DataFrame):
    data = df[df["popularity"] > 0]
    if data.empty:
        return None
    fig = px.box(data, x="type_label", y="popularity", color="type_label", log_y=True,
                 color_discrete_map=C.TYPE_COLORS, category_orders={"type_label": TYPE_ORDER})
    fig.update_traces(boxmean=True, marker_opacity=0.5, line_width=1.5)
    fig.update_xaxes(title="")
    fig.update_yaxes(title="Popularidad (escala logarítmica)")
    return _style(fig, "Distribución de popularidad por tipo", height=380, legend=False)


def fig_genre_popularity(df: pd.DataFrame, n: int = 8):
    ex = M.explode_genres(df)
    if ex.empty:
        return None
    top = ex["genre"].value_counts().nlargest(n).index
    grouped = (ex[ex["genre"].isin(top)].groupby(["genre", "type_label"])["popularity"]
               .median().rename("median_pop").reset_index())
    order = grouped.groupby("genre")["median_pop"].max().sort_values().index.tolist()
    fig = px.bar(grouped, x="median_pop", y="genre", color="type_label", orientation="h", barmode="group",
                 color_discrete_map=C.TYPE_COLORS,
                 category_orders={"genre": order, "type_label": TYPE_ORDER})
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{fullData.name}: %{x:,.1f}<extra></extra>")
    fig.update_xaxes(title="Popularidad mediana")
    fig.update_yaxes(title="")
    return _style(fig, "Popularidad mediana por género y tipo", height=420)


# --- Temporal analytics -----------------------------------------------------
def _year_axis(fig: go.Figure, years: pd.Series) -> None:
    if years.nunique() <= 20:
        fig.update_xaxes(dtick=1)


def fig_releases_area(df: pd.DataFrame):
    counts = df.groupby(["release_year", "type_label"]).size().rename("titles").reset_index()
    if counts.empty:
        return None
    fig = px.area(counts, x="release_year", y="titles", color="type_label",
                  color_discrete_map=C.TYPE_COLORS, category_orders={"type_label": TYPE_ORDER})
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,.0f} títulos<extra></extra>",
                      line_width=2)
    fig.update_xaxes(title="Año de lanzamiento")
    fig.update_yaxes(title="Títulos")
    _year_axis(fig, counts["release_year"])
    return _style(fig, "Lanzamientos por año", height=380)


def fig_metric_trend(df: pd.DataFrame, metric: str = "popularity", index100: bool = False):
    trend = M.trend_table(df, metric)
    if trend.empty:
        return None
    if index100:
        trend = M.to_index100(trend).dropna(subset=["value"])
        if trend.empty:
            return None
    fig = px.line(trend, x="release_year", y="value", color="type_label", markers=True,
                  color_discrete_map=C.TYPE_COLORS, category_orders={"type_label": TYPE_ORDER})
    unit = "Índice (base 100 = primer año)" if index100 else M.TREND_METRICS[metric]
    value_fmt = ".1f" if (index100 or metric != "titles") else ",.0f"
    fig.update_traces(line_width=3, marker_size=7,
                      hovertemplate=f"<b>%{{x}}</b><br>%{{fullData.name}}: %{{y:{value_fmt}}}<extra></extra>")
    if index100:
        fig.add_hline(y=100, line_dash="dot", line_color=C.GREY_TEXT, opacity=0.6)
    fig.update_xaxes(title="Año de lanzamiento")
    fig.update_yaxes(title=unit)
    _year_axis(fig, trend["release_year"])
    return _style(fig, f"Evolución: {M.TREND_METRICS[metric].lower()}", height=380)


def fig_month_heatmap(df: pd.DataFrame):
    matrix = M.month_year_matrix(df)
    if matrix.empty:
        return None
    fig = go.Figure(go.Heatmap(
        z=matrix.values, x=C.MONTHS_ES, y=[str(y) for y in matrix.index],
        colorscale=C.RED_SCALE, xgap=3, ygap=3, texttemplate="%{z:,.0f}", textfont=dict(size=11, color=C.WHITE),
        colorbar=dict(title="Títulos", thickness=10),
        hovertemplate="<b>%{y} · %{x}</b><br>%{z:,.0f} títulos<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed", type="category")
    return _style(fig, "Estacionalidad: títulos por año y mes de `date_added`",
                  height=max(360, 40 * len(matrix) + 110), legend=False)


def fig_top_years(df: pd.DataFrame, n: int = 8):
    top = M.top_years(df, n)
    if top.empty:
        return None
    top = top.iloc[::-1]
    fig = go.Figure(go.Bar(
        x=top["titles"], y=top["release_year"].astype(int).astype(str), orientation="h",
        marker_color=C.RED, text=top["titles"], texttemplate="%{text:,.0f}", textposition="outside",
        cliponaxis=False, textfont=dict(color=C.WHITE),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} títulos<extra></extra>",
    ))
    fig.update_xaxes(title="Títulos", range=[0, top["titles"].max() * 1.15])
    fig.update_yaxes(title="", type="category")
    fig.update_layout(bargap=0.3)
    return _style(fig, f"Años con más lanzamientos (top {len(top)})", height=380, legend=False)


# --- Engagement analytics ---------------------------------------------------
def fig_scatter_engagement(df: pd.DataFrame):
    data = df[(df["vote_count"] > 0) & (df["popularity"] > 0)]
    if data.empty:
        return None
    if len(data) > C.SCATTER_MAX_POINTS:
        top = data.nlargest(200, "popularity")
        rest = data.drop(top.index).sample(C.SCATTER_MAX_POINTS - 200, random_state=42)
        data = pd.concat([top, rest])
    fig = px.scatter(data, x="vote_count", y="popularity", color="type_label", log_x=True, log_y=True,
                     opacity=0.55, color_discrete_map=C.TYPE_COLORS,
                     custom_data=["title", "release_year"], category_orders={"type_label": TYPE_ORDER})
    fig.update_traces(marker=dict(size=6, line=dict(width=0)),
                      hovertemplate=("<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                                     "Votos: %{x:,.0f}<br>Popularidad: %{y:,.1f}<extra>%{fullData.name}</extra>"))
    fig.update_xaxes(title="Número de votos (escala log)")
    fig.update_yaxes(title="Popularidad (escala log)")
    return _style(fig, "Popularidad vs número de votos", height=460)


def fig_popularity_hist(df: pd.DataFrame):
    data = df[df["popularity"] > 0].assign(log_pop=lambda d: np.log10(d["popularity"]))
    if data.empty:
        return None
    fig = px.histogram(data, x="log_pop", color="type_label", nbins=40, barmode="overlay", opacity=0.7,
                       color_discrete_map=C.TYPE_COLORS, category_orders={"type_label": TYPE_ORDER})
    low, high = math.floor(data["log_pop"].min()), math.ceil(data["log_pop"].max())
    ticks = list(range(low, high + 1))
    fig.update_xaxes(tickvals=ticks, ticktext=[fmt_int(10 ** t) for t in ticks], title="Popularidad (escala log)")
    fig.update_yaxes(title="Títulos")
    fig.update_traces(hovertemplate="%{y:,.0f} títulos en este tramo<extra>%{fullData.name}</extra>")
    return _style(fig, "Distribución de popularidad", height=380)


def fig_rating_hist(df: pd.DataFrame):
    data = df[df["rating_clean"].notna()]
    if data.empty:
        return None
    fig = px.histogram(data, x="rating_clean", color="type_label", nbins=20, histnorm="percent",
                       barmode="overlay", opacity=0.7, color_discrete_map=C.TYPE_COLORS,
                       category_orders={"type_label": TYPE_ORDER})
    fig.update_xaxes(title="Valoración media (títulos con votos)", range=[0, 10])
    fig.update_yaxes(title="% de títulos")
    fig.update_traces(hovertemplate="%{y:.1f}% de los títulos<extra>%{fullData.name}</extra>")
    return _style(fig, "Distribución de valoraciones", height=380)


def fig_corr_heatmap(corr: pd.DataFrame | None):
    if corr is None or corr.empty:
        return None
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(), zmin=-1, zmax=1,
        colorscale=[[0, "#B8B8B8"], [0.5, C.BLACK_2], [1, C.RED]], xgap=3, ygap=3,
        texttemplate="%{z:.2f}", textfont=dict(color=C.WHITE),
        colorbar=dict(title="ρ", thickness=10),
        hovertemplate="<b>%{y} × %{x}</b><br>Correlación de Spearman: %{z:.2f}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    return _style(fig, "Correlación entre variables (Spearman)", height=420, legend=False)
