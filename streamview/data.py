"""Carga, validación y limpieza de los CSV. Las funciones de limpieza son puras."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from . import config as C


class DataError(Exception):
    """Error de datos con mensaje legible para el usuario."""


def _split_list(series: pd.Series) -> pd.Series:
    """'Drama, Comedy' -> ['Drama', 'Comedy']; nulos -> []."""
    return series.fillna("").astype(str).apply(
        lambda text: [part.strip() for part in text.split(",") if part.strip()]
    )


def validate_columns(df: pd.DataFrame, source: str) -> None:
    missing = [col for col in C.REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise DataError(
            f"Al archivo '{source}' le faltan columnas obligatorias: {', '.join(missing)}. "
            f"Columnas encontradas: {', '.join(map(str, df.columns))}."
        )


def clean_frame(raw: pd.DataFrame, fallback_label: str, source: str) -> pd.DataFrame:
    """Valida y limpia un DataFrame sin eliminar ninguna columna original."""
    validate_columns(raw, source)
    df = raw.copy()

    # Columnas opcionales: se crean vacías si no existen.
    for col in C.OPTIONAL_TEXT:
        if col not in df.columns:
            df[col] = np.nan
    if "vote_average" not in df.columns and "rating" in df.columns:
        df["vote_average"] = df["rating"]
    for col in C.OPTIONAL_NUMERIC:
        if col not in df.columns:
            df[col] = np.nan

    # Conversión de tipos numéricos.
    for col in ["release_year", "popularity", "vote_count", "vote_average", "budget", "revenue"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["vote_count"] = df["vote_count"].fillna(0).astype(int)
    if not df["release_year"].isna().any():
        df["release_year"] = df["release_year"].astype(int)

    # Texto básico.
    df["title"] = df["title"].fillna("Sin título").astype(str).str.strip()

    # Tipo de contenido normalizado (si falta `type` se usa el archivo de origen).
    df["type_label"] = df["type"].map(C.TYPE_MAP).fillna(fallback_label)

    # Fechas.
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
        df["added_year"] = df["date_added"].dt.year
        df["added_month"] = df["date_added"].dt.month
    else:
        df["date_added"] = pd.NaT
        df["added_year"] = np.nan
        df["added_month"] = np.nan

    # Listas de géneros y países.
    df["genres_list"] = _split_list(df["genres"])
    df["country_list"] = _split_list(df["country"])
    df["primary_genre"] = df["genres_list"].apply(lambda xs: xs[0] if xs else "Sin género")
    df["primary_country"] = df["country_list"].apply(lambda xs: xs[0] if xs else "Desconocido")

    # En estos CSV un 0 significa "sin dato", no un valor real.
    df["has_votes"] = df["vote_count"] > 0
    df["rating_clean"] = df["vote_average"].where(df["has_votes"] & (df["vote_average"] > 0))
    df["budget_clean"] = df["budget"].where(df["budget"] > 0)
    df["revenue_clean"] = df["revenue"].where(df["revenue"] > 0)
    df["roi"] = (df["revenue_clean"] / df["budget_clean"]).replace([np.inf, -np.inf], np.nan)
    return df


def _read_csv(path, fallback_label: str) -> pd.DataFrame:
    if not path.exists():
        raise DataError(f"No se encuentra el archivo {path}. Colócalo en la carpeta data/.")
    try:
        raw = pd.read_csv(path)
    except Exception as exc:  # CSV corrupto, codificación, etc.
        raise DataError(f"No se pudo leer {path.name}: {exc}") from exc
    return clean_frame(raw, fallback_label, path.name)


def files_token() -> str:
    """Huella de los archivos: invalida la caché cuando cambian."""
    parts = []
    for path in (C.MOVIES_CSV, C.TV_CSV):
        parts.append(str(path.stat().st_mtime_ns) if path.exists() else "missing")
    return "-".join(parts)


@st.cache_data(show_spinner="Cargando catálogo…")
def load_data(token: str) -> pd.DataFrame:
    """Carga ambos CSV y los combina en un único DataFrame con `uid` único."""
    movies = _read_csv(C.MOVIES_CSV, C.MOVIE)
    shows = _read_csv(C.TV_CSV, C.SERIES)
    df = pd.concat([movies, shows], ignore_index=True, sort=False)
    df.insert(0, "uid", np.arange(len(df)))
    return df


def genre_options(df: pd.DataFrame) -> list[str]:
    """Géneros ordenados por frecuencia."""
    if df.empty:
        return []
    counts = df["genres_list"].explode().dropna().value_counts()
    return [g for g in counts.index if g]
