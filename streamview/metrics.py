"""Cálculo de métricas, rankings e insights. Todo son funciones puras sobre DataFrames."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .utils import fmt_float, fmt_int, safe_div

RANK_METRICS = {
    "popularity": "Popularidad",
    "vote_count": "Número de votos",
    "weighted_rating": "Valoración ponderada",
}

CORR_LABELS = {
    "popularity": "Popularidad",
    "vote_count": "Votos",
    "rating_clean": "Valoración media",
    "release_year": "Año",
    "budget_clean": "Presupuesto",
    "revenue_clean": "Ingresos",
}

TREND_METRICS = {
    "popularity": "Popularidad media",
    "vote_count": "Votos (mediana por título)",
    "rating": "Valoración media (títulos con votos)",
    "titles": "Número de títulos",
}


# --- Géneros ----------------------------------------------------------------
def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por (título, género). Solo copia las columnas necesarias."""
    if df.empty:
        return pd.DataFrame(columns=["uid", "type_label", "genre", "popularity", "vote_count"])
    cols = ["uid", "type_label", "genres_list", "popularity", "vote_count", "release_year"]
    out = df[cols].explode("genres_list").rename(columns={"genres_list": "genre"})
    return out[out["genre"].notna() & (out["genre"] != "")]


def genre_counts(df: pd.DataFrame) -> pd.DataFrame:
    exploded = explode_genres(df)
    if exploded.empty:
        return pd.DataFrame(columns=["genre", "type_label", "titles"])
    return (exploded.groupby(["genre", "type_label"]).size()
            .rename("titles").reset_index())


# --- Rankings ---------------------------------------------------------------
def weighted_rating(df: pd.DataFrame, quantile: float = 0.75) -> pd.Series:
    """Valoración ponderada tipo IMDb: evita que un título con 3 votos gane a uno con 30.000.

    WR = v/(v+m)·R + m/(v+m)·C, con C = media global y m = percentil de votos.
    Los títulos sin votos reciben NaN.
    """
    voted = df[df["has_votes"] & df["rating_clean"].notna()]
    if voted.empty:
        return pd.Series(np.nan, index=df.index)
    mean_rating = voted["rating_clean"].mean()
    min_votes = voted["vote_count"].quantile(quantile)
    v = df["vote_count"].astype(float)
    denom = (v + min_votes).replace(0, np.nan)
    wr = (v / denom) * df["rating_clean"] + (min_votes / denom) * mean_rating
    return wr.where(df["has_votes"] & df["rating_clean"].notna())


def rank_titles(df: pd.DataFrame, metric: str = "popularity", n: int = 10) -> pd.DataFrame:
    """Top-n títulos por métrica; añade la columna `score`."""
    if df.empty:
        return df.head(0).assign(score=pd.Series(dtype=float))
    score = weighted_rating(df) if metric == "weighted_rating" else df[metric]
    ranked = df.assign(score=score).dropna(subset=["score"])
    return ranked.nlargest(n, "score")


# --- KPIs -------------------------------------------------------------------
def yoy_delta(df: pd.DataFrame, column: str, how: str = "mean"):
    """Variación % del último año del filtro frente al anterior, o None si no es fiable."""
    years = df["release_year"].dropna()
    if years.nunique() < 2:
        return None
    last = int(years.max())
    cur, old = df[df["release_year"] == last], df[df["release_year"] == last - 1]
    if len(cur) < C.MIN_TITLES_FOR_DELTA or len(old) < C.MIN_TITLES_FOR_DELTA:
        return None
    agg = (lambda s: s.mean()) if how == "mean" else (lambda s: s.sum())
    a, b = agg(cur[column]), agg(old[column])
    ratio = safe_div(a - b, b)
    if ratio is None:
        return None
    return ratio * 100, f"vs {last - 1}"


def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    movies = int((df["type_label"] == C.MOVIE).sum())
    series = int((df["type_label"] == C.SERIES).sum())
    genres = genre_counts(df)
    top_genre = None
    if not genres.empty:
        by_genre = genres.groupby("genre")["titles"].sum().sort_values(ascending=False)
        top_genre = (by_genre.index[0], int(by_genre.iloc[0]),
                     safe_div(by_genre.iloc[0], total, 0) * 100)
    return {
        "total": total,
        "movies": movies,
        "series": series,
        "movies_share": (safe_div(movies, total, 0) or 0) * 100,
        "series_share": (safe_div(series, total, 0) or 0) * 100,
        "avg_popularity": df["popularity"].mean() if total else None,
        "total_votes": int(df["vote_count"].sum()) if total else 0,
        "top_genre": top_genre,
        "popularity_delta": yoy_delta(df, "popularity", "mean"),
        "votes_delta": yoy_delta(df, "vote_count", "sum"),
    }


# --- Comparativas y series temporales ---------------------------------------
def type_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby("type_label")
    out = pd.DataFrame({
        "Títulos": grouped.size(),
        "Popularidad media": grouped["popularity"].mean(),
        "Popularidad mediana": grouped["popularity"].median(),
        "Popularidad P90": grouped["popularity"].quantile(0.9),
        "Votos totales": grouped["vote_count"].sum(),
        "Votos (mediana)": grouped["vote_count"].median(),
        "Valoración media": grouped["rating_clean"].mean(),
        "% con votos": grouped["has_votes"].mean() * 100,
    })
    return out


def trend_table(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Tabla larga [release_year, type_label, value] para gráficos de evolución."""
    if df.empty:
        return pd.DataFrame(columns=["release_year", "type_label", "value"])
    grouped = df.groupby(["release_year", "type_label"])
    if metric == "popularity":
        series = grouped["popularity"].mean()
    elif metric == "vote_count":
        series = grouped["vote_count"].median()
    elif metric == "rating":
        series = grouped["rating_clean"].mean()
    else:
        series = grouped.size()
    return series.rename("value").reset_index().dropna(subset=["value"])


def to_index100(trend: pd.DataFrame) -> pd.DataFrame:
    """Base 100 = primer año con valor > 0 de cada tipo."""
    out = trend.sort_values("release_year").copy()
    out["value"] = out["value"].astype(float)
    for label, part in out.groupby("type_label"):
        base = part.loc[part["value"] > 0, "value"]
        if base.empty:
            out.loc[part.index, "value"] = np.nan
        else:
            out.loc[part.index, "value"] = part["value"] / base.iloc[0] * 100
    return out


def top_years(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["release_year", "titles"])
    counts = df.groupby("release_year").size().rename("titles").reset_index()
    return counts.sort_values(["titles", "release_year"], ascending=[False, False]).head(n)


def month_year_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Altas por año (filas) y mes (columnas 1-12) según `date_added`."""
    valid = df.dropna(subset=["added_year", "added_month"])
    if valid.empty:
        return pd.DataFrame()
    matrix = pd.crosstab(valid["added_year"].astype(int), valid["added_month"].astype(int))
    return matrix.reindex(columns=range(1, 13), fill_value=0)


def corr_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame | None:
    """Correlación de Spearman (rangos, por pares). Devuelve None si no hay datos."""
    cols = [c for c in columns if c in df.columns and df[c].notna().sum() >= 10]
    if len(cols) < 2:
        return None
    corr = df[cols].rank().corr(min_periods=10)
    return corr.rename(index=CORR_LABELS, columns=CORR_LABELS)


# --- Insights y calidad de datos --------------------------------------------
def build_insights(df: pd.DataFrame) -> list[dict]:
    """Hallazgos calculados sobre la selección actual (nunca texto fijo con cifras)."""
    if df.empty:
        return []
    items: list[dict] = []

    genres = genre_counts(df)
    if not genres.empty:
        by_genre = genres.groupby("genre")["titles"].sum().sort_values(ascending=False)
        share = safe_div(by_genre.iloc[0], len(df), 0) * 100
        items.append({"icon": "🎭", "title": "Género dominante",
                      "text": f"{by_genre.index[0]} aparece en el {fmt_float(share)}% de los títulos."})

    top = rank_titles(df, "popularity", 1)
    if not top.empty:
        row = top.iloc[0]
        items.append({"icon": "🔥", "title": "Título más popular",
                      "text": f"{row['title']} ({row['type_label'].lower()}, {int(row['release_year'])}) "
                              f"con popularidad {fmt_float(row['popularity'])}."})

    most_voted = rank_titles(df, "vote_count", 1)
    if not most_voted.empty and most_voted.iloc[0]["vote_count"] > 0:
        row = most_voted.iloc[0]
        items.append({"icon": "🗳️", "title": "Título con más votos",
                      "text": f"{row['title']} acumula {fmt_int(row['vote_count'])} votos."})

    summary = type_summary(df)
    if {C.MOVIE, C.SERIES} <= set(summary.index):
        movie_med = summary.loc[C.MOVIE, "Popularidad mediana"]
        series_med = summary.loc[C.SERIES, "Popularidad mediana"]
        ratio = safe_div(series_med, movie_med)
        if ratio:
            items.append({"icon": "⚖️", "title": "Películas frente a series",
                          "text": f"La popularidad mediana de las series ({fmt_float(series_med)}) es "
                                  f"{fmt_float(ratio)}× la de las películas ({fmt_float(movie_med)})."})

    no_votes = safe_div((~df["has_votes"]).sum(), len(df), 0) * 100
    items.append({"icon": "📭", "title": "Títulos sin votos",
                  "text": f"El {fmt_float(no_votes)}% de la selección no tiene ningún voto."})
    return items[:4]


def data_quality_notes(df: pd.DataFrame) -> list[str]:
    """Advertencias sobre los datos completos, calculadas dinámicamente."""
    notes: list[str] = []
    if df.empty:
        return notes

    sizes = df.groupby(["type_label", "release_year"]).size()
    if len(sizes) > 1 and sizes.nunique() == 1:
        notes.append(
            f"El dataset contiene exactamente {fmt_int(sizes.iloc[0])} títulos por año y tipo "
            "(muestra equilibrada): el conteo anual no refleja el crecimiento real del catálogo."
        )
    if {"rating", "vote_average"} <= set(df.columns) and df["rating"].equals(df["vote_average"]):
        notes.append("`rating` y `vote_average` son idénticas; se usa `vote_average` como valoración.")
    if "duration" in df.columns and df["duration"].dropna().nunique() <= 1:
        notes.append("`duration` no tiene variación (vacía en películas y constante en series), "
                     "por eso no se analiza.")
    if df["date_added"].notna().any():
        same = (df["added_year"] == df["release_year"]).mean()
        if same == 1:
            notes.append("`date_added` coincide siempre con `release_year`; se usa como fecha de "
                         "lanzamiento y no como fecha de incorporación a Netflix.")
    for label, part in df.groupby("type_label"):
        zero = int((~part["has_votes"]).sum())
        if zero:
            notes.append(f"{fmt_int(zero)} {C.TYPE_PLURAL.get(label, label).lower()} "
                         "no tienen votos; se excluyen de las medias de valoración.")
    movies = df[df["type_label"] == C.MOVIE]
    if not movies.empty and movies["budget_clean"].notna().any():
        notes.append(f"Solo {fmt_int(movies['budget_clean'].notna().sum())} de "
                     f"{fmt_int(len(movies))} películas tienen presupuesto (un 0 se trata como dato ausente).")
    notes.append("Las variaciones de los KPI comparan el último año del filtro con el anterior. Los títulos "
                 "recientes acumulan menos votos, así que una caída en votos refleja antigüedad, no pérdida de interés.")
    notes.append("La popularidad es una métrica propia del dataset, y el número de votos no equivale "
                 "a espectadores ni a visualizaciones. Las escalas de popularidad de películas y series "
                 "no son directamente comparables.")
    return notes


def balanced_yearly_size(df: pd.DataFrame):
    """Si cada (tipo, año) tiene exactamente el mismo número de títulos devuelve ese número; si no, None."""
    if df.empty:
        return None
    sizes = df.groupby(["type_label", "release_year"]).size()
    return int(sizes.iloc[0]) if len(sizes) > 1 and sizes.nunique() == 1 else None
