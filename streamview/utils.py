"""Utilidades puras: formato de números en español, escape HTML y divisiones seguras."""
import html
import math

import pandas as pd


def is_missing(value) -> bool:
    """True si el valor es None, NaN o pd.NA."""
    if value is None or value is pd.NA:
        return True
    try:
        return isinstance(value, float) and math.isnan(value)
    except TypeError:
        return False


def safe_div(numerator, denominator, default=None):
    """División que devuelve `default` cuando el denominador es 0, nulo o NaN."""
    if is_missing(numerator) or is_missing(denominator) or denominator == 0:
        return default
    return numerator / denominator


def fmt_int(value) -> str:
    """1234567 -> '1.234.567'. Devuelve '—' para nulos."""
    if is_missing(value):
        return "—"
    return f"{int(round(float(value))):,}".replace(",", ".")


def fmt_float(value, decimals: int = 1) -> str:
    """1234.56 -> '1.234,6'. Devuelve '—' para nulos."""
    if is_missing(value):
        return "—"
    text = f"{float(value):,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt_compact(value) -> str:
    """Formato compacto en español: 391.400.000.000 -> '391,4 mil M'; 11.500.000 -> '11,5 M'."""
    if is_missing(value):
        return "—"
    value = float(value)
    if abs(value) >= 1e9:
        return f"{value / 1e9:.1f} mil M".replace(".", ",")
    if abs(value) >= 1e6:
        return f"{value / 1e6:.1f} M".replace(".", ",")
    if abs(value) >= 1e3:
        return f"{value / 1e3:.1f} K".replace(".", ",")
    return fmt_int(value)


def fmt_pct(value, decimals: int = 1, signed: bool = False) -> str:
    if is_missing(value):
        return "—"
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{fmt_float(value, decimals)}%"


def esc(value) -> str:
    """Escapa texto de los datos antes de incrustarlo en HTML.

    También neutraliza `$` para que Streamlit no lo interprete como LaTeX.
    """
    if is_missing(value):
        return ""
    return html.escape(str(value), quote=True).replace("$", "&#36;")


def html_block(markup: str) -> str:
    """Compacta HTML multilínea en una sola línea.

    Markdown trata las líneas con 4+ espacios de sangría como bloque de código;
    al quitar saltos de línea y sangrías se evita ese problema.
    """
    return "".join(line.strip() for line in markup.splitlines())
