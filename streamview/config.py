"""Configuración global: rutas, paleta, etiquetas y constantes de negocio."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MOVIES_CSV = DATA_DIR / "netflix_movies_detailed_up_to_2025.csv"
TV_CSV = DATA_DIR / "netflix_tv_shows_detailed_up_to_2025.csv"

APP_NAME = "StreamView"
APP_SUBTITLE = "Analítica del catálogo de películas y series de Netflix"

# --- Paleta -----------------------------------------------------------------
RED = "#E50914"
RED_DARK = "#8A0610"
BLACK = "#080808"
BLACK_2 = "#141414"
GREY_DARK = "#222222"
GREY_TEXT = "#999999"
WHITE = "#FFFFFF"

# Etiquetas de tipo (valor normalizado en la columna `type_label`)
MOVIE = "Película"
SERIES = "Serie"
TYPE_COLORS = {MOVIE: RED, SERIES: "#B8B8B8"}
TYPE_PLURAL = {MOVIE: "Películas", SERIES: "Series"}
RED_SCALE = [[0.0, "#1C0407"], [0.45, RED_DARK], [1.0, RED]]

# --- Datos ------------------------------------------------------------------
# Columnas sin las cuales el dashboard no puede funcionar.
REQUIRED_COLUMNS = ["title", "release_year", "popularity", "vote_count", "genres"]
# Columnas opcionales: si faltan se crean vacías para no romper los gráficos.
OPTIONAL_TEXT = ["director", "cast", "country", "language", "description", "type"]
OPTIONAL_NUMERIC = ["vote_average", "budget", "revenue", "show_id"]
TYPE_MAP = {"Movie": MOVIE, "TV Show": SERIES}

# Mínimo de títulos por año para mostrar variaciones interanuales (evita ruido).
MIN_TITLES_FOR_DELTA = 30
SCATTER_MAX_POINTS = 4000

SECTIONS = ["Overview", "Content Analytics", "Temporal Analytics",
            "Engagement Analytics", "Content Explorer", "Top Content"]

MONTHS_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
