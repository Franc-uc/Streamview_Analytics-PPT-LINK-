# StreamView Analytics — Plataforma Corporativa de Visual Analytics

Solución integral de **Business Intelligence y Visualización de Datos** desarrollada en **Python (Streamlit + Plotly)** para el análisis estratégico del catálogo audiovisual de **StreamView Analytics** (Asignatura **ADY1104 — Visualización de Datos**, Duoc UC).

**Integrantes:** Fabio Lobos, Franco Pareja (Sección 001D)

---

## Estructura Profesional del Proyecto

```text
STREAMVIEW-main/
├── .streamlit/
│   └── config.toml                                # Tema oscuro corporativo y configuración de servidor
├── data/
│   ├── netflix_movies_detailed_up_to_2025.csv     # 16.000 películas (2010–2025)
│   └── netflix_tv_shows_detailed_up_to_2025.csv   # 16.000 series (2010–2025)
├── images/                                        # Gráficos estáticos de alta resolución para el Informe Ejecutivo
│   ├── 01_top_generos_catalogo.png
│   ├── 02_geografia_idiomas.png
│   ├── 03_finanzas_roi_peliculas.png
│   └── 04_evolucion_y_correlacion.png
├── notebooks/
│   └── EDA_Calidad_y_Hallazgos_StreamView.ipynb   # Notebook reproducible de auditoría de datos y EDA
├── streamview/                                    # Paquete modular de la aplicación
│   ├── __init__.py
│   ├── config.py                                  # Constantes de negocio, rutas y paleta accesible WCAG AA
│   ├── data.py                                    # Carga en caché, validación de esquema y limpieza pura
│   ├── filters.py                                 # Estado global inmutable (@dataclass) de filtros interactivos
│   ├── metrics.py                                 # KPIs, Valoración Ponderada Bayesiana (IMDb), Spearman y ROI
│   ├── charts.py                                  # Constructores de gráficos interactivos Plotly
│   ├── components.py                              # Tarjetas KPI HTML/CSS, grillas de pósters y tablas
│   ├── navigation.py                              # Barra de navegación horizontal en 8 módulos analíticos
│   ├── sections.py                                # Renderizado de las 8 vistas ejecutivas, tácticas y operativas
│   ├── sidebar.py                                 # Segmentadores globales y controles de restablecimiento
│   ├── styles.py                                  # Hoja de estilos CSS personalizada con soporte reduced-motion
│   └── utils.py                                   # Formateo numérico en español y sanitización HTML
├── app.py                                         # Punto de entrada principal de la aplicación Streamlit
├── requirements.txt                               # Dependencias del entorno virtual
└── README.md                                      # Documentación técnica y guía de ejecución
```

---

## Requisitos e Instrucciones de Ejecución

1. **Crear y activar entorno virtual (Python 3.10+):**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / macOS:
   source .venv/bin/activate
   ```
2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Ejecutar el Dashboard Interactivo:**
   ```bash
   streamlit run app.py
   ```

---

## Alcance y Reglas de Negocio Aplicadas

- Los datasets contienen **32.000 títulos** (16.000 películas y 16.000 series; 2010–2025) enriquecidos con metadatos públicos de TMDB.
- Las variables financieras (`budget`, `revenue`, `roi`) aplican exclusivamente a películas con registros mayores a cero ($n = 3.540$ con ambos campos).
- La popularidad y el número de votos son métricas externas de recepción pública y **no representan reproducciones, horas vistas ni retención de suscriptores**.
