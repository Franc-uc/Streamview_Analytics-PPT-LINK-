"""CSS personalizado: tema cinematográfico inspirado en Netflix."""
import streamlit as st

from . import config as C

_VARS = f"""
:root {{
  --red: {C.RED}; --red-dark: {C.RED_DARK}; --black: {C.BLACK}; --black-2: {C.BLACK_2};
  --grey-dark: {C.GREY_DARK}; --grey: {C.GREY_TEXT}; --white: {C.WHITE};
  --line: rgba(255,255,255,0.08);
  --display: 'Bebas Neue', 'Oswald', Impact, 'Arial Narrow', sans-serif;
  --body: 'Inter', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}}
"""

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: var(--body); }
.stApp {
  background:
    radial-gradient(1100px 480px at 6% -8%, rgba(229,9,20,0.17), transparent 60%),
    radial-gradient(800px 380px at 100% 0%, rgba(229,9,20,0.07), transparent 55%),
    var(--black);
}
#MainMenu, footer, .stDeployButton { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1560px; padding: 1.4rem 2.2rem 3rem; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: #2b2b2b; border-radius: 8px; }

/* ---------- Cabecera ---------- */
.sv-hero {
  display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; flex-wrap: wrap;
  padding: 26px 30px; border-radius: 20px; border: 1px solid var(--line);
  background: linear-gradient(120deg, rgba(229,9,20,0.20) 0%, rgba(20,20,20,0.92) 46%, rgba(8,8,8,0.95) 100%);
  box-shadow: 0 18px 50px rgba(0,0,0,0.45); margin-bottom: 1.1rem;
}
.sv-logo { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.sv-logo .brand { font-family: var(--display); font-size: clamp(2.6rem, 5vw, 4rem); letter-spacing: 0.07em; color: var(--red); line-height: 1; }
.sv-logo .product { font-size: clamp(0.95rem, 1.6vw, 1.25rem); font-weight: 400; letter-spacing: 0.42em; color: var(--white); }
.sv-hero .tagline { margin-top: 8px; color: #BDBDBD; font-size: 0.98rem; max-width: 640px; }
.sv-hero .side { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }
.sv-badge {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px;
  border: 1px solid rgba(229,9,20,0.55); background: rgba(229,9,20,0.10);
  color: #FFD9DB; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.04em;
}
.sv-badge .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--red); animation: sv-pulse 2.2s ease-out infinite; }
@keyframes sv-pulse { 0% { box-shadow: 0 0 0 0 rgba(229,9,20,0.7); } 70% { box-shadow: 0 0 0 9px rgba(229,9,20,0); } 100% { box-shadow: 0 0 0 0 rgba(229,9,20,0); } }
@media (prefers-reduced-motion: reduce) { .sv-badge .dot { animation: none; } }
.sv-chips { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
.sv-chip { padding: 4px 11px; border-radius: 8px; background: rgba(255,255,255,0.06); color: #D5D5D5; font-size: 0.8rem; }

/* ---------- Navegación ---------- */
.st-key-nav [role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 8px; }
.st-key-nav label {
  padding: 8px 18px; border-radius: 999px; background: var(--black-2); border: 1px solid var(--line);
  cursor: pointer; transition: border-color .15s, background .15s;
}
.st-key-nav label:hover { border-color: rgba(229,9,20,0.6); }
.st-key-nav label > div:first-child { display: none; }
.st-key-nav label p { font-size: 0.9rem; font-weight: 500; color: #D0D0D0; }
.st-key-nav label:has(input:checked) { background: var(--red); border-color: var(--red); }
.st-key-nav label:has(input:checked) p { color: var(--white); font-weight: 600; }

/* ---------- Secciones y tarjetas ---------- */
.sv-section { margin: 1.4rem 0 0.9rem; padding-left: 14px; border-left: 4px solid var(--red); }
.sv-section h2 { margin: 0; padding: 0; font-family: var(--display); font-size: 2rem; letter-spacing: 0.05em; font-weight: 400; color: var(--white); }
.sv-section p { margin: 2px 0 0; color: var(--grey); font-size: 0.92rem; }
[class*="st-key-card_"] {
  background: rgba(20,20,20,0.86); border: 1px solid var(--line); border-radius: 16px;
  padding: 0.9rem 1.1rem; box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.sv-note {
  border-left: 3px solid var(--red); background: rgba(229,9,20,0.07); border-radius: 10px;
  padding: 10px 14px; color: #CFCFCF; font-size: 0.88rem; margin: 6px 0 12px;
}
.sv-empty {
  text-align: center; padding: 48px 20px; border: 1px dashed #333; border-radius: 14px; color: var(--grey);
}
.sv-empty b { display: block; color: var(--white); font-size: 1.05rem; margin-bottom: 4px; }

/* ---------- KPIs ---------- */
.sv-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; }
.sv-kpi {
  background: linear-gradient(160deg, #1A1A1A, #0F0F0F); border: 1px solid var(--line); border-radius: 16px;
  padding: 18px 20px; box-shadow: 0 10px 28px rgba(0,0,0,0.4); transition: transform .18s, border-color .18s, box-shadow .18s;
}
.sv-kpi:hover { transform: translateY(-3px); border-color: rgba(229,9,20,0.6); box-shadow: 0 14px 34px rgba(229,9,20,0.14); }
.sv-kpi .top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.sv-kpi .label { color: var(--grey); font-size: 0.84rem; font-weight: 500; }
.sv-kpi .ktag { padding: 3px 8px; border-radius: 6px; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em; color: #F8D7DA; background: rgba(229,9,20,0.18); border: 1px solid rgba(229,9,20,0.35); }
.sv-kpi .value { margin-top: 10px; font-family: var(--display); font-size: 2.5rem; letter-spacing: 0.03em; line-height: 1.05; color: var(--white); overflow-wrap: anywhere; }
.sv-kpi .sub { margin-top: 4px; font-size: 0.8rem; color: var(--grey); }
.sv-kpi .delta { margin-top: 8px; font-size: 0.8rem; font-weight: 600; }
.sv-kpi .delta.up { color: #46D369; } .sv-kpi .delta.down { color: #FF7B7B; }
.sv-kpi .delta span { color: var(--grey); font-weight: 400; }

/* ---------- Insights ---------- */
.sv-insights { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }
.sv-insight { display: flex; gap: 12px; padding: 14px 16px; border-radius: 14px; background: rgba(255,255,255,0.03); border: 1px solid var(--line); border-left: 3px solid var(--red); }
.sv-insight .ico { font-size: 1.4rem; }
.sv-insight b { display: block; font-size: 0.86rem; color: var(--white); margin-bottom: 2px; }
.sv-insight span { font-size: 0.84rem; color: #BDBDBD; }

/* ---------- Tarjetas de póster (Top Content) ---------- */
.sv-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 14px; }
.sv-poster {
  position: relative; min-height: 290px; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column;
  justify-content: flex-end; border: 1px solid var(--line); box-shadow: 0 12px 30px rgba(0,0,0,0.45);
  transition: transform .18s, border-color .18s;
}
.sv-poster:hover { transform: translateY(-4px); border-color: rgba(229,9,20,0.65); }
.sv-poster .rank {
  position: absolute; top: 0; left: 12px; font-family: var(--display); font-size: 6.5rem; line-height: 1;
  color: transparent; -webkit-text-stroke: 2px rgba(255,255,255,0.55);
}
.sv-poster .badge { position: absolute; top: 12px; right: 12px; padding: 3px 10px; border-radius: 999px; background: rgba(0,0,0,0.55); font-size: 0.72rem; color: #EEE; }
.sv-poster .body { padding: 14px; background: linear-gradient(to top, rgba(0,0,0,0.88) 55%, transparent); }
.sv-poster .title { font-weight: 700; font-size: 1rem; line-height: 1.2; color: var(--white); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.sv-poster .meta { margin-top: 3px; font-size: 0.78rem; color: #B5B5B5; }
.sv-poster .chips { margin-top: 8px; display: flex; gap: 6px; flex-wrap: wrap; }
.sv-poster .chips i { font-style: normal; font-size: 0.7rem; padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.12); color: #EAEAEA; }
.sv-bar { margin-top: 10px; height: 5px; border-radius: 4px; background: rgba(255,255,255,0.15); overflow: hidden; }
.sv-bar span { display: block; height: 100%; background: linear-gradient(90deg, var(--red-dark), var(--red)); border-radius: 4px; }
.sv-poster .stats { margin-top: 6px; font-size: 0.76rem; color: #CFCFCF; }
.sv-poster .stats b { color: var(--white); font-size: 0.95rem; }

.sv-feature { display: grid; grid-template-columns: minmax(220px, 300px) 1fr; gap: 24px; align-items: stretch; }
.sv-feature .sv-poster { min-height: 340px; }
.sv-feature .info { display: flex; flex-direction: column; justify-content: center; gap: 10px; }
.sv-feature .kicker { color: var(--red); font-weight: 700; font-size: 0.85rem; letter-spacing: 0.06em; }
.sv-feature h3 { margin: 0; font-family: var(--display); font-size: clamp(2rem, 4vw, 3.2rem); letter-spacing: 0.04em; font-weight: 400; line-height: 1.05; color: var(--white); }
.sv-feature .desc { color: #C6C6C6; line-height: 1.55; max-width: 70ch; font-size: 0.95rem; }
.sv-feature .facts { display: flex; gap: 22px; flex-wrap: wrap; }
.sv-feature .facts div { font-size: 0.78rem; color: var(--grey); }
.sv-feature .facts b { display: block; font-size: 1.25rem; color: var(--white); font-family: var(--display); letter-spacing: 0.04em; font-weight: 400; }

/* ---------- Tabla HTML ---------- */
.sv-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.sv-table th { text-align: right; color: var(--grey); font-weight: 500; padding: 8px 10px; border-bottom: 1px solid var(--line); }
.sv-table td { text-align: right; padding: 9px 10px; border-bottom: 1px solid rgba(255,255,255,0.04); color: #E5E5E5; }
.sv-table th:first-child, .sv-table td:first-child { text-align: left; font-weight: 600; }
.sv-table-wrap { overflow-x: auto; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background: #0C0C0C; border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
.sv-side-logo { font-family: var(--display); font-size: 2.1rem; letter-spacing: 0.07em; color: var(--red); line-height: 1; }
.sv-side-logo span { display: block; font-family: var(--body); font-size: 0.68rem; letter-spacing: 0.4em; color: #DDD; margin-top: 4px; }
.sv-side-title { margin: 14px 0 4px; font-size: 0.78rem; color: var(--grey); font-weight: 600; }
.sv-side-count { padding: 10px 12px; border-radius: 12px; background: rgba(229,9,20,0.10); border: 1px solid rgba(229,9,20,0.35); font-size: 0.85rem; color: #FFE1E3; margin: 6px 0 4px; }
span[data-baseweb="tag"] { background-color: var(--red) !important; border-radius: 6px; }
div[data-baseweb="input"], div[data-baseweb="select"] > div { border-radius: 10px; }
.stButton > button, .stDownloadButton > button {
  border-radius: 10px; border: 1px solid rgba(229,9,20,0.6); background: rgba(229,9,20,0.10); color: var(--white); font-weight: 600;
  transition: background .15s, border-color .15s;
}
.stButton > button:hover, .stDownloadButton > button:hover { background: var(--red); border-color: var(--red); color: var(--white); }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid var(--line); }

/* ---------- Responsive ---------- */
@media (max-width: 1100px) {
  .block-container { padding: 1rem 1.1rem 2rem; }
  .sv-hero { padding: 20px; } .sv-hero .side { align-items: flex-start; } .sv-chips { justify-content: flex-start; }
  .sv-kpi .value { font-size: 2.1rem; } .sv-feature { grid-template-columns: 1fr; }
}
@media (max-width: 640px) { .sv-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); } .sv-section h2 { font-size: 1.6rem; } }
"""


def inject_css() -> None:
    st.markdown(f"<style>{_VARS}{_CSS}</style>", unsafe_allow_html=True)
