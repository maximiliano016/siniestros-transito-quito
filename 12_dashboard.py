import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from shapely.geometry import shape

# Para abrir el dashboard, en la terminal:
#   streamlit run 12_dashboard.py
# Necesita los archivos que generan los scripts anteriores (transformado, cruces y resultados del clustering)


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Dashboard · Siniestros de Tránsito en Quito",
    page_icon="🚦",
    layout="wide"
)

# colores del proyecto (los mismos de las presentaciones y del informe)
TINTA = "#16150F"
TINTA2 = "#3A372F"
GRIS = "#6B6657"
CLARO = "#DDD7C8"
PALIDO = "#ECE7DB"
TARJETA = "#FBFAF6"
ROJO = "#B8321F"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
SIN_BARRA = {"displayModeBar": False}
#oculta la barra de botones de plotly (zoom, descargar...) para que se vea limpio
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


# ============================================================
# ESTILO VISUAL (CSS)
# ============================================================
# Streamlit trae un diseño por defecto. Con este bloque de CSS se le da el estilo del proyecto:
# fondo cuadriculado, barra lateral oscura, tarjetas con borde y tipografias propias

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900&family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:ital@1&display=swap" rel="stylesheet">
<style>
html, body, .stApp, .stMarkdown p, label, input, button { font-family: 'IBM Plex Mono', monospace; }
.stApp { background-color:#F1EEE6;
  background-image: linear-gradient(#E6E1D5 1px, transparent 1px), linear-gradient(90deg, #E6E1D5 1px, transparent 1px);
  background-size: 24px 24px; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stAppDeployButton"] { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1400px; }
/* barra lateral oscura */
[data-testid="stSidebar"] { background:#16150F; }
[data-testid="stSidebar"] * { color:#F1EEE6; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size:10.5px; letter-spacing:.16em; text-transform:uppercase; color:#9E978A; }
[data-testid="stSidebar"] .react-aria-ComboBox > div { background:#24221B; border:1px solid #4A473D; border-radius:0; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button { background:#24221B; border-color:#4A473D; border-radius:0; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[kind*="Active"] { background:#F1EEE6; }
[data-testid="stSidebar"] [data-testid="stButtonGroup"] button[kind*="Active"] * { color:#16150F; font-weight:600; }
[data-testid="stSidebar"] [data-testid="stRadioOption"], [data-testid="stSidebar"] [role="radiogroup"] label { padding:7px 10px; width:100%; margin:0; }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] { background:#F1EEE6; }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] * { color:#16150F; font-weight:600; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child { display:none; }
/* tarjetas: los st.container(border=True) */
[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] { background:#FBFAF6; border:1.5px solid #16150F !important; border-radius:0 !important; }
[data-testid="stMetricLabel"] p { font-size:11px !important; letter-spacing:.14em; text-transform:uppercase; color:#6B6657; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] p { font-family:'Big Shoulders Display', sans-serif !important; font-weight:800 !important; font-size:52px !important; line-height:1 !important; }
[data-testid="stCaptionContainer"] p { font-size:12px; color:#6B6657; }
/* textos propios */
.titulo { font-family:'Big Shoulders Display', sans-serif !important; font-weight:800 !important; font-size:42px !important; text-transform:uppercase; line-height:1 !important; margin:0 !important; }
.subtitulo { font-family:'Newsreader', serif !important; font-style:italic; font-size:16px !important; color:#3A372F; margin:6px 0 0 0 !important; }
.badge { font-size:11.5px; border:1.5px solid #16150F; padding:6px 10px; background:#FBFAF6; display:inline-block; }
.badge b { color:#B8321F; }
.etiqueta { font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:#6B6657; margin-bottom:4px; }
.nota { font-family:'Newsreader', serif !important; font-style:italic; font-size:15px !important; color:#3A372F; }
.nota b { font-family:'IBM Plex Mono', monospace; font-style:normal; font-size:12.5px; color:#B8321F; }
.grande { font-family:'Big Shoulders Display', sans-serif; font-weight:900; font-size:48px; line-height:.95; }
.marca { font-family:'Big Shoulders Display', sans-serif; font-weight:900; font-size:34px; line-height:.95; text-transform:uppercase; }
.linea { border-bottom:2px solid #16150F; margin:10px 0 18px 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# CARGAR DATASET
# ============================================================

@st.cache_data
def cargar_datos():
    df = pd.read_csv("accidentes_transito_quito_transformado.csv", sep=";", encoding="utf-8-sig", low_memory=False)
    cruces = pd.read_csv("cruces_clima_parroquia_quito_2024_2026.csv", sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    df = df.merge(cruces[["ID_Registro", "Parroquia_DMQ"]], on="ID_Registro", how="left")
    df["Parroquia_DMQ"] = df["Parroquia_DMQ"].fillna("N/D")
    #se agrega la parroquia real de cada siniestro (calculada con sus coordenadas)

    def familia(causa):
        c = str(causa).upper()
        if "SEÑALES" in c: return "Irrespeto a señales"
        if "VELOCIDAD" in c: return "Exceso de velocidad"
        if "EMBRIAGUEZ" in c or c.startswith("CONDUCE BAJO LA INFLUENCIA"): return "Alcohol o drogas"
        if "PEATÓN" in c or "ACERAS" in c: return "Imprudencia del peatón"
        if "CLIMÁTIC" in c or "AMBIENTALES" in c: return "Clima"
        if "MECÁNIC" in c or "ESTADO DE LA VÍA" in c or "NEÚMATICOS" in c: return "Vehículo o vía"
        if "OTRAS CAUSAS" in c: return "Otras causas"
        return "Conducción imprudente"
    df["Familia_Causa"] = df["Causa"].map(familia)
    #el INEC y la ANT nombran distinto la misma causa: se agrupan en familias
    return df


@st.cache_data
def cargar_clusters():
    clusters = pd.read_csv("resultados/dataset_clustering.csv", sep=";", encoding="utf-8-sig")
    perfil = pd.read_csv("resultados/perfil_clusters.csv", sep=";", encoding="utf-8-sig")
    grupo_letal = perfil.loc[perfil["letalidad"].idxmax(), "cluster"]
    grupo_grande = perfil.loc[perfil["siniestros"].idxmax(), "cluster"]
    nombres = {grupo_letal: "Pocos siniestros, alta letalidad", grupo_grande: "Muchos siniestros"}
    clusters["grupo"] = clusters["cluster"].map(lambda c: nombres.get(c, "Riesgo típico"))
    perfil["grupo"] = perfil["cluster"].map(lambda c: nombres.get(c, "Riesgo típico"))
    #a cada cluster se le pone un nombre segun su perfil (igual que en 11_mapa_siniestros.py)
    return clusters, perfil


@st.cache_data
def cargar_parroquias():
    datos = json.load(open("parroquias_dmq.geojson", encoding="utf-8"))
    formas = []
    for f in datos["features"]:
        g = shape(f["geometry"]).simplify(0.0012)
        poligonos = [g] if g.geom_type == "Polygon" else list(g.geoms)
        for p in poligonos:
            x, y = p.exterior.xy
            formas.append({"nombre": f["properties"]["dpa_despar"],
                           "urbana": int(str(f["properties"]["dpa_parroq"])[4:]) < 50,
                           "x": list(x), "y": list(y)})
    return formas
    #limites oficiales de las 65 parroquias (GeoQuito). Se simplifican para que el mapa cargue rapido


df = cargar_datos()
df_clusters, perfil_clusters = cargar_clusters()
formas = cargar_parroquias()
grupo_de = dict(zip(df_clusters["Parroquia_DMQ"], df_clusters["grupo"]))
COLOR_GRUPO = {"Pocos siniestros, alta letalidad": ROJO, "Muchos siniestros": TINTA,
               "Riesgo típico": "#A39D8C", "Sin grupo (menos de 30 siniestros)": "#CFC8B6"}

ACENTOS = {"CALDERON": "Calderón", "PINTAG": "Píntag", "YARUQUI": "Yaruquí", "CUMBAYA": "Cumbayá", "PUENGASI": "Puengasí",
           "ITCHIMBIA": "Itchimbía", "CARCELEN": "Carcelén", "ALANGASI": "Alangasí", "NAYON": "Nayón", "ZAMBIZA": "Zámbiza",
           "CENTRO HISTORICO": "Centro Histórico", "GUAMANI": "Guamaní", "COMITE DEL PUEBLO": "Comité del Pueblo", "LA CONCEPCION": "La Concepción"}
def bonito(nombre):
    return ACENTOS.get(nombre, str(nombre).title().replace(" De ", " de ").replace(" Del ", " del "))
#la fuente escribe los nombres en mayusculas y sin tildes; esto los muestra bien

def miles(n):
    return f"{n:,.0f}".replace(",", ".")

def decimal(n, d=1):
    return f"{n:.{d}f}".replace(".", ",")


# ============================================================
# ESTILO DE LOS GRÁFICOS
# ============================================================

def estilo(fig, alto=320):
    fig.update_layout(
        height=alto,
        paper_bgcolor=TARJETA, plot_bgcolor=TARJETA,
        font=dict(family="IBM Plex Mono, monospace", size=11, color=TINTA2),
        margin=dict(l=10, r=45, t=10, b=10),
        showlegend=False,
        hoverlabel=dict(bgcolor=TINTA, font_color="#F1EEE6", font_family="IBM Plex Mono"),
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=False, linecolor=TINTA, ticks="", tickangle=0)
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    #cliponaxis=False: que los numeros al final de las barras no se corten
    fig.update_yaxes(gridcolor=CLARO, zeroline=False, separatethousands=True)
    return fig
#todos los graficos usan el mismo fondo, tipografia y colores

def tarjeta_titulo(texto, derecha=""):
    st.markdown(f'<div class="etiqueta">{texto}<span style="float:right;color:#3A372F">{derecha}</span></div>', unsafe_allow_html=True)

def nota(texto):
    st.markdown(f'<p class="nota">{texto}</p>', unsafe_allow_html=True)


# ============================================================
# BARRA LATERAL
# ============================================================

st.sidebar.markdown("""
<div style="font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#9E978A">Ciencia y Análisis de Datos · 2026</div>
<div class="marca" style="margin:8px 0 6px 0">Siniestros de tránsito en <span style="color:#E2563E">Quito</span></div>
<div style="font-family:'Newsreader',serif;font-style:italic;font-size:14px;color:#C9C2B0">Análisis predictivo para identificar las zonas de mayor riesgo.</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

# ------------------------------------------------------------
# FILTRO PERIODO
# ------------------------------------------------------------

anios = sorted(df["Año"].unique())
opciones_periodo = ["2017 – 2026 (todo)"] + [f"{a} (ene–ago)" if a == 2026 else str(a) for a in anios]
periodo = st.sidebar.selectbox("Periodo", opciones_periodo)

# ------------------------------------------------------------
# FILTRO ZONA
# ------------------------------------------------------------

zona = st.sidebar.segmented_control("Zona", ["Todas", "Urbana", "Rural"], default="Todas") or "Todas"

# ------------------------------------------------------------
# SECCIONES
# ------------------------------------------------------------

secciones = ["01  Resumen", "02  Mapa de riesgo", "03  Cuándo ocurren", "04  Causas y perfil",
             "05  Grupos de riesgo", "06  Simulador", "07  Datos"]
seccion = st.sidebar.radio("Secciones", secciones)

st.sidebar.divider()
st.sidebar.caption("**Fuentes:** ANT (2024–2026), INEC (2017–2023), GeoQuito, REMMAQ.  \n"
                   "**Equipo:** Maximiliano Parra, Jonathan Larraga, Ariel Pilliza.")


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()
if periodo != opciones_periodo[0]:
    df_filtrado = df_filtrado[df_filtrado["Año"] == int(periodo[:4])]
if zona != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Zona"] == zona]

df_mapa = df_filtrado[df_filtrado["Parroquia_DMQ"] != "N/D"]
if len(df_mapa) == 0:
    df_mapa = df[(df["Parroquia_DMQ"] != "N/D") & ((df["Zona"] == zona) | (zona == "Todas"))]
#el mapa solo usa 2024-2026 (los unicos años con ubicacion). Si se elige un año anterior, muestra 2024-2026

def encabezado(titulo, subtitulo, ubicacion=False):
    texto_periodo = "2017–2026" if periodo == opciones_periodo[0] else periodo
    extra = " · ubicación: 2024–2026" if ubicacion else ""
    c1, c2 = st.columns([3, 1.3])
    c1.markdown(f'<p class="titulo">{titulo}</p><p class="subtitulo">{subtitulo}</p>', unsafe_allow_html=True)
    c2.markdown(f'<div style="text-align:right;margin-top:22px"><span class="badge">Periodo <b>{texto_periodo}</b> · zona <b>{zona.lower()}</b>{extra}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="linea"></div>', unsafe_allow_html=True)


# ============================================================
# 01 · RESUMEN
# ============================================================

if seccion == secciones[0]:

    encabezado("Panorama general", "Cuántos siniestros hay, cómo cambian en el tiempo y qué tan graves son.")

    # ---------------- indicadores principales ----------------
    total = len(df_filtrado)
    fallecidos = df_filtrado["Fallecidos"].sum()
    lesionados = df_filtrado["Lesionados"].sum()
    dias = 3530 if periodo == opciones_periodo[0] else (243 if periodo.startswith("2026") else 365)
    #dias del periodo, para calcular cuantos siniestros hay en promedio por dia

    col1, col2, col3, col4 = st.columns(4)
    with col1.container(border=True):
        st.metric("Siniestros", miles(total))
        st.caption(f"≈ {decimal(total / dias)} siniestros por día")
    with col2.container(border=True):
        st.metric("Fallecidos", miles(fallecidos))
        st.caption(f"1 de cada {round(total / fallecidos) if fallecidos else 0} siniestros es mortal")
    with col3.container(border=True):
        st.metric("Lesionados", miles(lesionados))
        st.caption(f"≈ {decimal(lesionados / dias)} heridos por día")
    with col4.container(border=True):
        st.metric("Letalidad", decimal(fallecidos / total * 100) if total else "–")
        st.caption("fallecidos por cada 100 siniestros")

    # ---------------- evolución por año ----------------
    base_zona = df if zona == "Todas" else df[df["Zona"] == zona]
    por_anio = base_zona.groupby("Año").agg(siniestros=("Siniestros", "sum"), fallecidos=("Fallecidos", "sum")).reset_index()
    por_anio["letalidad"] = por_anio["fallecidos"] / por_anio["siniestros"] * 1000

    col1, col2 = st.columns([2, 1])
    with col1.container(border=True):
        tarjeta_titulo("Siniestros por año", "el año elegido en rojo")
        colores = [ROJO if periodo != opciones_periodo[0] and periodo.startswith(str(a)) else TINTA for a in por_anio["Año"]]
        fig = go.Figure(go.Bar(x=por_anio["Año"].astype(str), y=por_anio["siniestros"], marker_color=colores,
                               marker_cornerradius=2, hovertemplate="<b>%{x}</b><br>%{y:,} siniestros<extra></extra>"))
        st.plotly_chart(estilo(fig, 300), width="stretch", config=SIN_BARRA)
    with col2.container(border=True):
        tarjeta_titulo("Letalidad por año", "por cada 1.000 siniestros")
        fig = go.Figure(go.Scatter(x=por_anio["Año"].astype(str), y=por_anio["letalidad"], mode="lines+markers",
                                   line=dict(color=ROJO, width=2), marker=dict(size=8, color=TARJETA, line=dict(color=ROJO, width=2)),
                                   hovertemplate="<b>%{x}</b><br>%{y:.1f} fallecidos por cada 1.000<extra></extra>"))
        st.plotly_chart(estilo(fig, 240), width="stretch", config=SIN_BARRA)
        l17 = por_anio.loc[por_anio["Año"] == 2017, "letalidad"].iloc[0]
        l25 = por_anio.loc[por_anio["Año"] == 2025, "letalidad"].iloc[0]
        nota(f"De <b>{round(l17)}</b> a <b>{round(l25)}</b>: hay menos siniestros, pero más mortales.")

    # ---------------- top parroquias y hallazgos ----------------
    col1, col2 = st.columns([1, 2])
    with col1.container(border=True):
        tarjeta_titulo("Parroquias con más siniestros", "2024–2026")
        top = df_mapa.groupby("Parroquia_DMQ").agg(siniestros=("Siniestros", "sum"), fallecidos=("Fallecidos", "sum")) \
                     .sort_values("siniestros", ascending=False).head(7).reset_index()
        filas = "".join(f'<div style="display:flex;justify-content:space-between;border-bottom:1px solid #DDD7C8;padding:6px 0">'
                        f'<span><b style="color:#6B6657">{i + 1}</b>&nbsp;&nbsp;<span style="font-family:Big Shoulders Display;font-weight:700;font-size:19px;text-transform:uppercase">{bonito(r.Parroquia_DMQ)}</span></span>'
                        f'<span style="font-size:12px">{miles(r.siniestros)} · <span style="color:{ROJO}">{r.fallecidos} fall.</span></span></div>'
                        for i, r in top.iterrows())
        st.markdown(filas, unsafe_allow_html=True)
    with col2.container(border=True):
        tarjeta_titulo("Hallazgos principales")
        hallazgos = [("×2,7", "más mortales que en 2017", "La letalidad pasó de 31 a 85 por cada 1.000 siniestros."),
                     ("34,5 %", "ocurre en fin de semana", "En solo dos de los siete días de la semana."),
                     ("×2,3", "letalidad rural vs. urbana", "11,2 contra 4,8 fallecidos por cada 100 siniestros."),
                     ("45 %", "velocidad, señales y alcohol", "Casi todos los siniestros dependen del conductor."),
                     ("07:00", "y 19:00, las horas pico", "El sábado es el día con más siniestros en los 9 años."),
                     ("44,9", "fallecidos por 100 en Pifo", "Las parroquias rurales con vías rápidas son las más mortales.")]
        for fila in range(2):
            columnas = st.columns(3)
            for j, (num, titulo, texto) in enumerate(hallazgos[fila * 3: fila * 3 + 3]):
                columnas[j].markdown(f'<div class="grande" style="color:{ROJO}">{num}</div><div style="font-weight:600;margin-top:4px">{titulo}</div>'
                                     f'<p class="nota" style="font-size:13.5px">{texto}</p>', unsafe_allow_html=True)


# ============================================================
# 02 · MAPA DE RIESGO
# ============================================================

elif seccion == secciones[1]:

    encabezado("Mapa de riesgo por parroquia", "Dónde se concentran los siniestros y dónde son más mortales.", ubicacion=True)

    por_parroquia = df_mapa.groupby("Parroquia_DMQ").agg(
        siniestros=("Siniestros", "sum"), fallecidos=("Fallecidos", "sum"),
        lat=("Latitud", lambda s: pd.to_numeric(s).median()), lon=("Longitud", lambda s: pd.to_numeric(s).median()),
        fin_de_semana=("Fin_de_Semana", lambda s: (s == "SI").mean() * 100),
    ).reset_index()
    por_parroquia["letalidad"] = por_parroquia["fallecidos"] / por_parroquia["siniestros"] * 100
    por_parroquia["grupo"] = por_parroquia["Parroquia_DMQ"].map(lambda n: grupo_de.get(n, "Sin grupo (menos de 30 siniestros)"))
    #la ubicacion de cada burbuja es la mediana de las coordenadas de los siniestros de esa parroquia

    if "parroquia" not in st.session_state:
        st.session_state["parroquia"] = "QUITUMBE"

    col1, col2 = st.columns([1.7, 1])
    with col1.container(border=True):
        metrica = st.segmented_control("Ver por", ["Grupo de riesgo", "Siniestros", "Letalidad"], default="Grupo de riesgo") or "Grupo de riesgo"
        fig = go.Figure()
        for f in formas:
            fig.add_trace(go.Scatter(x=f["x"], y=f["y"], fill="toself", mode="lines", fillcolor="#E3DDCE" if f["urbana"] else "#EFEBE0",
                                     line=dict(color="#C9C2B0", width=0.8), hoverinfo="skip"))
        #primero se dibujan los limites de las parroquias como fondo (sin necesidad de internet ni de OpenStreetMap)

        tamano = 8 + np.sqrt(por_parroquia["siniestros"] / por_parroquia["siniestros"].max()) * 42
        if metrica == "Grupo de riesgo":
            color = por_parroquia["grupo"].map(COLOR_GRUPO)
        elif metrica == "Siniestros":
            color = TINTA
        else:
            color = [ROJO if s >= 30 and l > 15 else ("#D98C7E" if s >= 30 and l > 8 else "#F1DED8") for s, l in zip(por_parroquia["siniestros"], por_parroquia["letalidad"])]
        destacar = por_parroquia["grupo"].isin(["Pocos siniestros, alta letalidad", "Muchos siniestros"])
        fig.add_trace(go.Scatter(
            x=por_parroquia["lon"], y=por_parroquia["lat"], mode="markers+text",
            marker=dict(size=tamano, color=color, opacity=0.9, line=dict(color=TARJETA, width=1.2)),
            text=[bonito(n) if d else "" for n, d in zip(por_parroquia["Parroquia_DMQ"], destacar)],
            textposition=["middle left" if n == "YARUQUI" else "middle right" for n in por_parroquia["Parroquia_DMQ"]],
            textfont=dict(family="IBM Plex Mono", size=12, color=TINTA),
            customdata=np.stack([por_parroquia["Parroquia_DMQ"].map(bonito), por_parroquia["grupo"], por_parroquia["siniestros"],
                                 por_parroquia["fallecidos"], por_parroquia["letalidad"].round(1), por_parroquia["Parroquia_DMQ"]], axis=-1),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]} siniestros · %{customdata[3]} fallecidos<br>Letalidad: %{customdata[4]} por cada 100<extra></extra>",
        ))
        #despues, una burbuja por parroquia: tamaño = siniestros, color = la metrica elegida
        estilo(fig, 620)
        fig.update_xaxes(visible=False, range=[-78.62, -78.18])
        fig.update_yaxes(visible=False, range=[-0.40, 0.08], scaleanchor="x")
        seleccion = st.plotly_chart(fig, width="stretch", config=SIN_BARRA, on_select="rerun", key="mapa", selection_mode="points")
        if seleccion and seleccion.selection.points:
            punto = seleccion.selection.points[0]
            if "customdata" in punto:
                st.session_state["parroquia"] = punto["customdata"][5]
        #al hacer clic en una burbuja se actualiza la ficha de la derecha
        st.markdown(" &nbsp; ".join(f'<span style="color:{c};font-size:16px">●</span> <span style="font-size:11.5px">{g}</span>' for g, c in COLOR_GRUPO.items())
                    + ' &nbsp; <span style="font-size:11.5px;color:#6B6657">· tamaño = siniestros</span>', unsafe_allow_html=True)

    with col2.container(border=True):
        lista = sorted(por_parroquia["Parroquia_DMQ"])
        elegida = st.session_state["parroquia"] if st.session_state["parroquia"] in lista else lista[0]
        elegida = st.selectbox("Ficha de la parroquia", lista, index=lista.index(elegida), format_func=bonito)
        st.session_state["parroquia"] = elegida
        datos = por_parroquia[por_parroquia["Parroquia_DMQ"] == elegida].iloc[0]
        grupo = datos["grupo"]
        st.markdown(f'<div class="grande" style="text-transform:uppercase">{bonito(elegida)}</div>'
                    f'<span class="badge" style="margin-top:8px"><span style="color:{COLOR_GRUPO[grupo]}">●</span> {grupo}</span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Siniestros", miles(datos["siniestros"]))
        c2.metric("Fallecidos", miles(datos["fallecidos"]))
        c1.metric("Letalidad", decimal(datos["letalidad"]))
        c2.metric("Fin de semana", decimal(datos["fin_de_semana"]) + "%")
        horas = df_mapa[df_mapa["Parroquia_DMQ"] == elegida].groupby("Hora_Num").size().reindex(range(24), fill_value=0)
        pico = int(horas.idxmax())
        tarjeta_titulo("Siniestros por hora")
        fig = go.Figure(go.Bar(x=[f"{h:02d}" for h in range(24)], y=horas.values, marker_cornerradius=2,
                               marker_color=[ROJO if h == pico else TINTA for h in range(24)],
                               hovertemplate="<b>%{x}:00</b><br>%{y} siniestros<extra></extra>"))
        st.plotly_chart(estilo(fig, 170), width="stretch", config=SIN_BARRA)
        tipo = df_mapa[df_mapa["Parroquia_DMQ"] == elegida]["Tipo_Siniestro"].mode()[0]
        nota(f"Hora pico: <b>{pico:02d}:00</b>. Tipo más frecuente: <b>{tipo}</b>.")


# ============================================================
# 03 · CUÁNDO OCURREN
# ============================================================

elif seccion == secciones[2]:

    encabezado("Cuándo ocurren", "Los patrones por hora, día y mes que se repiten cada año.")

    con_hora = df_filtrado.dropna(subset=["Hora_Num"])
    tabla = con_hora.groupby(["Dia_Semana_Num", "Hora_Num"]).size().unstack(fill_value=0).reindex(index=range(1, 8), columns=range(24), fill_value=0)
    corte = np.sort(tabla.values.flatten())[-8]
    #tabla dia x hora; "corte" es el valor de la octava casilla mas alta (las 8 horas mas criticas)

    with st.container(border=True):
        tarjeta_titulo("Mapa de calor: día de la semana × hora", "las 8 horas más críticas en rojo")
        fig = go.Figure(go.Heatmap(z=tabla.values, x=[f"{h:02d}" for h in range(24)], y=DIAS, xgap=2, ygap=2,
                                   colorscale=[[0, PALIDO], [0.5, "#8C8677"], [1, TINTA]], showscale=False,
                                   hovertemplate="<b>%{y} · %{x}</b><br>%{z} siniestros<extra></extra>"))
        criticas = np.where(tabla.values >= corte, tabla.values, np.nan)
        fig.add_trace(go.Heatmap(z=criticas, x=[f"{h:02d}" for h in range(24)], y=DIAS, xgap=2, ygap=2,
                                 colorscale=[[0, ROJO], [1, ROJO]], showscale=False,
                                 hovertemplate="<b>%{y} · %{x}</b><br>%{z} siniestros (crítica)<extra></extra>"))
        estilo(fig, 290)
        fig.update_yaxes(autorange="reversed", gridcolor=TARJETA)
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)

    col1, col2, col3 = st.columns(3)
    with col1.container(border=True):
        tarjeta_titulo("Por hora del día")
        por_hora = tabla.sum(axis=0)
        pico_m, pico_t = int(por_hora[:12].idxmax()), int(por_hora[12:].idxmax())
        fig = go.Figure(go.Bar(x=[f"{h:02d}" for h in range(24)], y=por_hora.values, marker_cornerradius=2,
                               marker_color=[ROJO if h in (pico_m, pico_t) else TINTA for h in range(24)],
                               hovertemplate="<b>%{x}:00</b><br>%{y:,} siniestros<extra></extra>"))
        st.plotly_chart(estilo(fig, 230), width="stretch", config=SIN_BARRA)
        nota(f"Dos picos: <b>{pico_m:02d}:00</b> y <b>{pico_t:02d}:00</b>, la entrada y salida del trabajo.")
    with col2.container(border=True):
        tarjeta_titulo("Por día de la semana")
        por_dia = tabla.sum(axis=1)
        fig = go.Figure(go.Bar(x=[d[:3] for d in DIAS], y=por_dia.values, marker_cornerradius=2,
                               marker_color=[ROJO if i >= 5 else TINTA for i in range(7)],
                               hovertemplate="<b>%{x}</b><br>%{y:,} siniestros<extra></extra>"))
        st.plotly_chart(estilo(fig, 230), width="stretch", config=SIN_BARRA)
        nota(f"El fin de semana concentra el <b>{decimal((por_dia[6] + por_dia[7]) / por_dia.sum() * 100)} %</b> de los siniestros.")
    with col3.container(border=True):
        tarjeta_titulo("Por mes", "2017–2025")
        completos = df[df["Año"] < 2026] if zona == "Todas" else df[(df["Año"] < 2026) & (df["Zona"] == zona)]
        por_mes = completos.groupby("Mes_Num").size().reindex(range(1, 13))
        promedio = por_mes.mean()
        #solo años completos: 2026 llega hasta agosto y haria ver mas bajos los ultimos meses
        fig = go.Figure(go.Bar(x=MESES, y=por_mes.values, marker_cornerradius=2,
                               marker_color=[ROJO if v > promedio else CLARO for v in por_mes.values],
                               hovertemplate="<b>%{x}</b><br>%{y:,} siniestros<extra></extra>"))
        fig.add_hline(y=promedio, line_dash="dash", line_color=TINTA, annotation_text="promedio", annotation_position="top left")
        estilo(fig, 230)
        fig.update_xaxes(tickangle=-45)
        #los nombres de los meses se inclinan para que no se encimen
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
        mes_max = int(por_mes.idxmax())
        nota(f"Solo <b>{MESES[mes_max - 1].lower()}</b> sobresale (+{decimal((por_mes.max() / promedio - 1) * 100)} %). El mes pesa poco.")


# ============================================================
# 04 · CAUSAS Y PERFIL
# ============================================================

elif seccion == secciones[3]:

    encabezado("Causas y perfil", "Por qué ocurren, qué tan graves son y quiénes están involucrados.")

    col1, col2 = st.columns(2)
    with col1.container(border=True):
        tarjeta_titulo("Causas del siniestro", "agrupadas")
        causas = (df_filtrado["Familia_Causa"].value_counts(normalize=True) * 100).sort_values()
        fig = go.Figure(go.Bar(x=causas.values, y=causas.index, orientation="h", marker_cornerradius=2,
                               marker_color=[ROJO if v == causas.max() else TINTA for v in causas.values],
                               text=[decimal(v) + " %" for v in causas.values], textposition="outside",
                               hovertemplate="<b>%{y}</b><br>%{x:.1f} %<extra></extra>"))
        st.plotly_chart(estilo(fig, 320), width="stretch", config=SIN_BARRA)
        suma = causas[["Exceso de velocidad", "Irrespeto a señales", "Alcohol o drogas"]].sum()
        nota(f"Velocidad, señales y alcohol suman el <b>{decimal(suma)} %</b>.")
    with col2.container(border=True):
        tarjeta_titulo("Tipo de siniestro y gravedad", "ordenados por % mortal")
        tipos = pd.crosstab(df_filtrado["Tipo_Siniestro"], df_filtrado["Gravedad"], normalize="index") * 100
        tipos = tipos.loc[df_filtrado["Tipo_Siniestro"].value_counts().head(9).index].sort_values("Mortal")
        fig = go.Figure()
        for gravedad, color in [("Solo daños materiales", CLARO), ("Con lesionados", TINTA2), ("Mortal", ROJO)]:
            fig.add_trace(go.Bar(y=tipos.index, x=tipos[gravedad], name=gravedad, orientation="h", marker_color=color,
                                 hovertemplate="<b>%{y}</b><br>" + gravedad + ": %{x:.1f} %<extra></extra>"))
        estilo(fig, 320)
        fig.update_layout(barmode="stack", showlegend=True, legend=dict(orientation="h", y=-0.12))
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
        #barra apilada al 100 %: cuanto de cada tipo de siniestro es solo daños, con lesionados o mortal

    recientes = df[df["Año"] >= 2024]
    def separar(columna):
        return recientes[recientes[columna] != "N/D"][columna].str.split("|").explode()
    #sexo, edad y vehiculos solo existen desde 2024 y vienen varios por siniestro separados con "|"

    col1, col2, col3 = st.columns(3)
    with col1.container(border=True):
        tarjeta_titulo("Personas por sexo", "2024–2026")
        sexo = separar("Sexo").value_counts()
        fig = go.Figure(go.Bar(x=sexo.values, y=[s.title() for s in sexo.index], orientation="h", marker_cornerradius=2,
                               marker_color=[{"HOMBRE": TINTA, "MUJER": ROJO}.get(s, CLARO) for s in sexo.index], text=[miles(v) for v in sexo.values], textposition="outside"))
        st.plotly_chart(estilo(fig, 220), width="stretch", config=SIN_BARRA)
        nota(f"De los identificados, <b>{round(sexo['HOMBRE'] / (sexo['HOMBRE'] + sexo['MUJER']) * 100)} %</b> son hombres.")
    with col2.container(border=True):
        tarjeta_titulo("Personas por edad", "2024–2026")
        orden = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90+"]
        edad = separar("Grupo_Edad").value_counts().reindex(orden, fill_value=0)
        fig = go.Figure(go.Bar(x=edad.index, y=edad.values, marker_cornerradius=2,
                               marker_color=[ROJO if g in ("20-24", "25-29", "30-34") else TINTA for g in edad.index],
                               hovertemplate="<b>%{x} años</b><br>%{y:,} personas<extra></extra>"))
        estilo(fig, 220)
        fig.update_xaxes(tickvals=["0-4", "20-24", "40-44", "60-64", "80-84"])
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
        jovenes = edad[["20-24", "25-29", "30-34"]].sum() / edad.sum() * 100
        nota(f"El <b>{decimal(jovenes)} %</b> tiene entre 20 y 34 años.")
    with col3.container(border=True):
        tarjeta_titulo("Vehículos involucrados", "2024–2026")
        vehiculos = separar("Tipo_Vehiculo").replace({"SCOOTER ELECTRICO": "SCOOTER ELÉCTRICO", "VEHÍCULO DEPORTIVO UTILITARIO": "SUV"}).value_counts().head(8).sort_values()
        fig = go.Figure(go.Bar(x=vehiculos.values, y=[v.title() for v in vehiculos.index], orientation="h", marker_cornerradius=2,
                               marker_color=[ROJO if v == "MOTOCICLETA" else TINTA for v in vehiculos.index],
                               text=[miles(v) for v in vehiculos.values], textposition="outside"))
        st.plotly_chart(estilo(fig, 220), width="stretch", config=SIN_BARRA)


# ============================================================
# 05 · GRUPOS DE RIESGO (CLUSTERING)
# ============================================================

elif seccion == secciones[4]:

    encabezado("Grupos de riesgo (clustering)", "Las parroquias agrupadas por K-Means según su perfil de siniestralidad.", ubicacion=True)

    descripciones = {"Pocos siniestros, alta letalidad": "Las parroquias rurales con vías rápidas: pocos siniestros, pero muy graves.",
                     "Muchos siniestros": "Las tres con más tráfico: concentran el volumen de siniestros.",
                     "Riesgo típico": "El resto de la ciudad: cantidad media y letalidad baja."}
    columnas = st.columns(3)
    for col, grupo in zip(columnas, descripciones):
        p = perfil_clusters[perfil_clusters["grupo"] == grupo].iloc[0]
        miembros = sorted(df_clusters[df_clusters["grupo"] == grupo]["Parroquia_DMQ"].map(bonito))
        lista = " · ".join(miembros) if len(miembros) <= 8 else " · ".join(miembros[:8]) + f" · y {len(miembros) - 8} más"
        with col.container(border=True):
            tarjeta_titulo(grupo, f"{int(p['parroquias'])} parroquias")
            st.markdown(f'<div class="grande" style="font-size:56px;color:{ROJO if grupo.startswith("Pocos") else TINTA}">{decimal(p["letalidad"])}</div>'
                        f'<div style="font-size:11.5px;color:#6B6657">fallecidos por cada 100 siniestros</div>', unsafe_allow_html=True)
            nota(descripciones[grupo])
            datos = [("Siniestros", miles(p["siniestros"])), ("Fin de semana", decimal(p["pct_fin_de_semana"]) + "%"), ("Madrugada", decimal(p["pct_madrugada"]) + "%")]
            st.markdown('<div style="display:flex;gap:18px;border-top:1px solid #DDD7C8;padding-top:10px">' + "".join(
                f'<div><div class="etiqueta">{t}</div><div class="grande" style="font-size:30px">{v}</div></div>' for t, v in datos) + "</div>", unsafe_allow_html=True)
            st.caption(lista)

    col1, col2 = st.columns([2, 1])
    with col1.container(border=True):
        tarjeta_titulo("Cada parroquia según cantidad y gravedad", "47 parroquias · K-Means, K = 3")
        etiquetas = {"AMAGUAÑA": "← Yaruquí, Llano Chico, Guayllabamba y Amaguaña", "YARUQUI": "", "LLANO CHICO": "", "GUAYLLABAMBA": ""}
        fig = go.Figure(go.Scatter(
            x=df_clusters["siniestros"], y=df_clusters["letalidad"], mode="markers+text",
            marker=dict(size=13, color=df_clusters["grupo"].map(COLOR_GRUPO), line=dict(color=TARJETA, width=1.5)),
            text=[etiquetas.get(n, bonito(n)) if g != "Riesgo típico" else "" for n, g in zip(df_clusters["Parroquia_DMQ"], df_clusters["grupo"])],
            textposition=["middle left" if n == "QUITUMBE" else "middle right" for n in df_clusters["Parroquia_DMQ"]],
            textfont=dict(family="IBM Plex Mono", size=11.5, color=TINTA),
            customdata=np.stack([df_clusters["Parroquia_DMQ"].map(bonito), df_clusters["grupo"]], axis=-1),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{x} siniestros · letalidad %{y:.1f}<extra></extra>"))
        estilo(fig, 400)
        fig.update_xaxes(title="siniestros 2024–2026 →", showgrid=False)
        fig.update_yaxes(title="fallecidos por cada 100 siniestros", range=[0, 50])
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
    with col2.container(border=True):
        tarjeta_titulo("Cómo se formaron los grupos")
        evaluacion = pd.read_csv("resultados/evaluacion_kmeans.csv", sep=";")
        evaluacion = evaluacion[evaluacion["n_clusters"] <= 4]
        fig = go.Figure(go.Bar(x=evaluacion["silhouette"], y=["K = " + str(k) for k in evaluacion["n_clusters"]], orientation="h",
                               marker_cornerradius=2, marker_color=[ROJO if k == 3 else GRIS for k in evaluacion["n_clusters"]],
                               text=[decimal(v, 3) for v in evaluacion["silhouette"]], textposition="outside"))
        estilo(fig, 220)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
        nota("K = 3 obtuvo el mejor coeficiente de silhouette: los grupos quedan mejor separados.")
        st.caption("Variables usadas (8): siniestros · fallecidos · lesionados · víctimas promedio · letalidad · % mortales · % fin de semana · % madrugada")


# ============================================================
# 06 · SIMULADOR DE ESCENARIOS
# ============================================================

elif seccion == secciones[5]:

    encabezado("Simulador de escenarios", "Elige un día, una hora y una zona para ver el nivel de riesgo histórico.")

    col1, col2, col3 = st.columns(3)
    with col1.container(border=True):
        tarjeta_titulo("1 · Elige el escenario")
        hora = st.slider("Hora", 0, 23, 19, format="%d:00")
        dia = st.segmented_control("Día", DIAS, default="Sábado") or "Sábado"
        zona_sim = st.segmented_control("Zona del escenario", ["Urbana", "Rural"], default="Urbana") or "Urbana"

    base = df[(df["Zona"] == zona_sim)].dropna(subset=["Hora_Num"])
    conteo = base.groupby(["Dia_Semana_Num", "Hora_Num"]).size().unstack(fill_value=0).reindex(index=range(1, 8), columns=range(24), fill_value=0)
    indice = conteo / conteo.values.mean()
    #indice = siniestros de ese dia y hora / siniestros de una hora promedio en esa zona (1 = una hora normal)
    d = DIAS.index(dia) + 1
    valor = float(indice.loc[d, hora])
    puntaje = min(10, valor * 5)
    #se lleva a una escala de 0 a 10, donde 5 es una hora promedio
    franja = "Madrugada" if hora < 6 else "Mañana" if hora < 12 else "Tarde" if hora < 18 else "Noche"
    finde = "SI" if d >= 6 else "NO"
    escenario = base[(base["Franja_Horaria"] == franja) & (base["Fin_de_Semana"] == finde)]
    letalidad = escenario["Fallecidos"].sum() / len(escenario) * 100
    letalidad_quito = df["Fallecidos"].sum() / len(df) * 100
    nivel = "crítico" if puntaje >= 8 else "alto" if puntaje >= 6 else "medio" if puntaje >= 4 else "bajo"

    with col2.container(border=True):
        tarjeta_titulo("2 · Índice de riesgo", "0 a 10")
        st.markdown(f'<div class="grande" style="font-size:110px;color:{ROJO if puntaje >= 6 else TINTA}">{decimal(puntaje)}</div>', unsafe_allow_html=True)
        cuadros = "".join(f'<span style="display:inline-block;width:9%;height:22px;margin-right:1%;background:{(ROJO if i >= 6 else TINTA) if i < round(puntaje) else PALIDO}"></span>' for i in range(10))
        st.markdown(f'<div style="margin:10px 0 4px 0">{cuadros}</div>'
                    '<div style="display:flex;justify-content:space-between;font-size:10px;color:#6B6657"><span>bajo</span><span>medio</span><span>alto</span><span>crítico</span></div>', unsafe_allow_html=True)
        nota(f"Riesgo <b>{nivel}</b>: {decimal(valor)} veces una hora promedio en zona {zona_sim.lower()}. Letalidad esperada: <b>{decimal(letalidad)}</b> fallecidos por cada 100 siniestros.")

    with col3.container(border=True):
        tarjeta_titulo("3 · Qué lo explica")
        factores = pd.Series({"Hora del día": indice[hora].mean(), "Día de la semana": indice.loc[d].mean(), "Gravedad esperada": letalidad / letalidad_quito})
        fig = go.Figure(go.Bar(x=factores.values, y=factores.index, orientation="h", marker_cornerradius=2,
                               marker_color=[ROJO if v > 1.15 else TINTA for v in factores.values],
                               text=["×" + decimal(v, 2) for v in factores.values], textposition="outside"))
        estilo(fig, 150)
        fig.update_xaxes(range=[0, max(2, factores.max() * 1.3)], visible=False)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
        tarjeta_titulo("Parroquias más expuestas")
        expuestas = df[(df["Zona"] == zona_sim) & (df["Franja_Horaria"] == franja) & (df["Fin_de_Semana"] == finde) & (df["Parroquia_DMQ"] != "N/D")]
        top = expuestas["Parroquia_DMQ"].value_counts().head(3)
        st.markdown("".join(f'<div style="display:flex;justify-content:space-between;border-bottom:1px solid #DDD7C8;padding:6px 0">'
                            f'<span><b style="color:#6B6657">{i + 1}</b>&nbsp;&nbsp;<span style="font-family:Big Shoulders Display;font-weight:700;font-size:19px;text-transform:uppercase">{bonito(n)}</span></span>'
                            f'<span style="font-size:12px">{v} siniestros</span></div>' for i, (n, v) in enumerate(top.items())), unsafe_allow_html=True)

    with st.container(border=True):
        tarjeta_titulo(f"Riesgo hora por hora · {dia} · zona {zona_sim.lower()}")
        puntajes = (indice.loc[d] * 5).clip(upper=10)
        fig = go.Figure(go.Bar(x=[f"{h:02d}" for h in range(24)], y=puntajes.values, marker_cornerradius=2,
                               marker_color=[ROJO if h == hora else (TINTA2 if v >= 6 else CLARO) for h, v in zip(range(24), puntajes.values)],
                               hovertemplate="<b>%{x}:00</b><br>Índice %{y:.1f}<extra></extra>"))
        estilo(fig, 220)
        fig.update_yaxes(range=[0, 10], dtick=2)
        st.plotly_chart(fig, width="stretch", config=SIN_BARRA)
    nota("El índice compara la frecuencia histórica de siniestros (2017–2026) en ese día y hora con una hora promedio de la zona: 5 = una hora promedio. En la fase de modelado lo reemplazará el modelo predictivo.")


# ============================================================
# 07 · DATOS FILTRADOS
# ============================================================

else:

    encabezado("Datos filtrados", "Los registros que cumplen los filtros de la barra lateral.")

    columnas = ["ID_Registro", "Año", "Mes", "Fecha", "Dia_Semana", "Hora", "Zona", "Parroquia_DMQ", "Sector_o_Via",
                "Tipo_Siniestro", "Causa", "Gravedad", "Fallecidos", "Lesionados", "Fuente"]
    st.dataframe(df_filtrado[columnas].fillna("N/D"), width="stretch", height=560, hide_index=True)
    st.caption(f"{miles(len(df_filtrado))} registros.")

    # ============================================================
    # DESCARGAR DATOS
    # ============================================================

    csv = df_filtrado[columnas].to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        label="⬇️ Descargar datos filtrados",
        data=csv,
        file_name="siniestros_quito_filtrados.csv",
        mime="text/csv"
    )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.divider()
st.caption("Proyecto de Ciencia y Análisis de Datos | Análisis Predictivo de Accidentes de Tránsito en Quito para la Identificación de Zonas de Mayor Riesgo")
