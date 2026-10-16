import pandas as pd
import folium
from folium.plugins import HeatMap

archivo = "accidentes_transito_quito_transformado.csv"
df = pd.read_csv(archivo, sep=";", encoding="utf-8-sig", low_memory=False)
print("==============================================")
print("ANALISIS GEOGRAFICO DE SINIESTROS DE TRANSITO")
print("==============================================")
print(f"Registros : {len(df)}")

# ============================================================
# 1. SINIESTROS CON Y SIN COORDENADAS
# ============================================================
#en el ejemplo de clase las coordenadas de cada ciudad se escribian a mano en un diccionario.
#en este proyecto no hace falta: cada siniestro ya trae su latitud y longitud real (fuente ANT)

print("==============================================")
print("Siniestros sin coordenadas")
print("==============================================")
sin_coordenadas = df[df["Tiene_Coordenadas"] == "NO"]
print(f"Siniestros sin coordenadas: {len(sin_coordenadas)}")
print(sin_coordenadas["Año"].value_counts().sort_index())
#de 2017 a 2023 la fuente no publica ubicacion; en 2024 hay 318 con coordenadas erroneas

df = df[df["Tiene_Coordenadas"] == "SI"].copy()
df["Latitud"] = pd.to_numeric(df["Latitud"])
df["Longitud"] = pd.to_numeric(df["Longitud"])
print(f"\nSiniestros que se pueden ubicar en el mapa: {len(df)}")
#las coordenadas venian como texto (por los N/D); se convierten a numero para el mapa
todos_con_coordenadas = df.copy()
#copia con todos los siniestros ubicables, para el mapa de calor

# ============================================================
# 2. RESUMEN POR PARROQUIA
# ============================================================
#el "destino" de este proyecto es la parroquia. Se agrega la parroquia real de cada siniestro

cruces = pd.read_csv("cruces_clima_parroquia_quito_2024_2026.csv", sep=";", encoding="utf-8-sig", low_memory=False)
df = df.merge(cruces[["ID_Registro", "Parroquia_DMQ"]], on="ID_Registro")
df = df[df["Parroquia_DMQ"] != "N/D"]

print("==============================================")
print("Parroquias")
print("==============================================")
print(df["Parroquia_DMQ"].value_counts())

parroquias = (
    df.groupby("Parroquia_DMQ")
    .agg(
        siniestros=("Siniestros", "sum"),
        fallecidos=("Fallecidos", "sum"),
        lesionados=("Lesionados", "sum"),
        latitud=("Latitud", "mean"),
        longitud=("Longitud", "mean"),
    )
    .reset_index()
)
parroquias["letalidad"] = (
    parroquias["fallecidos"] / parroquias["siniestros"] * 100
).round(2)
#latitud y longitud = el promedio de las coordenadas de todos los siniestros de esa parroquia,
#es decir, el punto donde se concentran sus siniestros (asi no hay que escribirlas a mano)

# ============================================================
# 3. AGREGAR EL CLUSTER DE CADA PARROQUIA (resultado de 10_clustering.py)
# ============================================================
clusters = pd.read_csv("resultados/dataset_clustering.csv", sep=";", encoding="utf-8-sig")
perfil = pd.read_csv("resultados/perfil_clusters.csv", sep=";", encoding="utf-8-sig")

grupo_letal = perfil.loc[perfil["letalidad"].idxmax(), "cluster"]
grupo_grande = perfil.loc[perfil["siniestros"].idxmax(), "cluster"]
def nombrar_cluster(cluster):
    if pd.isna(cluster):
        return "Sin cluster (menos de 30 siniestros)"
    elif cluster == grupo_letal:
        return "Pocos siniestros, alta letalidad"
    elif cluster == grupo_grande:
        return "Muchos siniestros"
    else:
        return "Riesgo típico"
#a cada grupo se le pone un nombre segun su perfil: el de mayor letalidad, el de mas siniestros y el resto.
#asi el nombre no depende del numero (0, 1, 2) que le haya puesto el algoritmo

parroquias = parroquias.merge(clusters[["Parroquia_DMQ", "cluster"]], on="Parroquia_DMQ", how="left")
parroquias["grupo"] = parroquias["cluster"].map(nombrar_cluster)
#how="left" conserva tambien las parroquias que no entraron al clustering (tienen menos de 30 siniestros)

colores = {
    "Pocos siniestros, alta letalidad": "red",
    "Muchos siniestros": "orange",
    "Riesgo típico": "blue",
    "Sin cluster (menos de 30 siniestros)": "gray",
}

print("==============================================")
print("Resumen por Parroquia")
print("==============================================")
print(parroquias.sort_values("siniestros", ascending=False).to_string(index=False))

parroquias.to_csv(
    "resultados/parroquias_geograficas.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# 4. MAPA 1: PARROQUIAS (tamaño = siniestros, color = cluster)
# ============================================================
mapa = folium.Map(
    location=[-0.20, -78.49],
    zoom_start=11,
    tiles="OpenStreetMap"
)
#location es el centro de Quito y zoom_start=11 muestra el Distrito completo
#IMPORTANTE: el fondo del mapa (OpenStreetMap) no carga si el HTML se abre con doble clic
#(sale "403 Access blocked"). Hay que abrirlo con un servidor local:
#   python -m http.server 8000   y entrar a   http://localhost:8000/resultados/mapa_parroquias.html

for _, fila in parroquias.iterrows():
    radio = max(
        5,
        min(
            30,
            fila["siniestros"] / parroquias["siniestros"].max() * 30
        )
    )
    #el circulo es mas grande mientras mas siniestros tiene la parroquia (minimo 5, maximo 30)

    popup = f"""
    <b>Parroquia:</b> {fila['Parroquia_DMQ'].title()}<br>
    <b>Grupo:</b> {fila['grupo']}<br>
    <b>Siniestros:</b> {fila['siniestros']:,.0f}<br>
    <b>Fallecidos:</b> {fila['fallecidos']:,.0f}<br>
    <b>Lesionados:</b> {fila['lesionados']:,.0f}<br>
    <b>Letalidad:</b> {fila['letalidad']:.2f} fallecidos por cada 100 siniestros
    """
    #popup: la ventana que aparece al hacer clic en el circulo

    folium.CircleMarker(
        location=[
            fila["latitud"],
            fila["longitud"]
        ],
        radius=radio,
        color=colores[fila["grupo"]],
        popup=folium.Popup(popup, max_width=300),
        tooltip=fila["Parroquia_DMQ"].title(),
        fill=True,
        fill_color=colores[fila["grupo"]],
        fill_opacity=0.6
    ).add_to(mapa)
    #tooltip: el nombre que aparece al pasar el mouse por encima

leyenda = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999; background: white;
            padding: 10px 14px; border: 1px solid #999; border-radius: 6px; font-size: 13px;">
<b>Grupos de parroquias (clustering)</b><br>
<span style="color:red;">&#9679;</span> Pocos siniestros, alta letalidad<br>
<span style="color:orange;">&#9679;</span> Muchos siniestros<br>
<span style="color:blue;">&#9679;</span> Riesgo típico<br>
<span style="color:gray;">&#9679;</span> Sin cluster (menos de 30 siniestros)<br>
<i>Tamaño del círculo = número de siniestros</i>
</div>
"""
mapa.get_root().html.add_child(folium.Element(leyenda))
#la leyenda es un recuadro en HTML que explica que significa cada color

mapa.save("resultados/mapa_parroquias.html")

# ============================================================
# 5. MAPA 2: MAPA DE CALOR DE TODOS LOS SINIESTROS
# ============================================================
datos_calor = []
for _, fila in todos_con_coordenadas.iterrows():
    datos_calor.append([
        fila["Latitud"],
        fila["Longitud"]
    ])
#a diferencia del ejemplo de clase (un punto por destino), aqui va un punto por cada siniestro real

mapa_calor = folium.Map(
    location=[-0.20, -78.49],
    zoom_start=11,
    tiles="OpenStreetMap"
)
HeatMap(
    datos_calor,
    radius=12,
    blur=15,
    min_opacity=0.4
).add_to(mapa_calor)
#las zonas rojas son donde se juntan mas siniestros; las azules, donde hay pocos
mapa_calor.save("resultados/mapa_calor_siniestros.html")

# ============================================================
# 6. MAPA 3: SINIESTROS MORTALES
# ============================================================
mortales = df[df["Fallecidos"] > 0]

mapa_mortales = folium.Map(
    location=[-0.20, -78.49],
    zoom_start=11,
    tiles="OpenStreetMap"
)
for _, fila in mortales.iterrows():
    popup = f"""
    <b>Fecha:</b> {fila['Fecha']} {fila['Hora']}<br>
    <b>Lugar:</b> {fila['Sector_o_Via']}<br>
    <b>Parroquia:</b> {fila['Parroquia_DMQ'].title()}<br>
    <b>Tipo:</b> {fila['Tipo_Siniestro']}<br>
    <b>Fallecidos:</b> {fila['Fallecidos']}
    """
    folium.CircleMarker(
        location=[fila["Latitud"], fila["Longitud"]],
        radius=4,
        color="darkred",
        fill=True,
        fill_color="red",
        fill_opacity=0.7,
        popup=folium.Popup(popup, max_width=300)
    ).add_to(mapa_mortales)
#un punto rojo por cada siniestro con al menos un fallecido, con su fecha, hora y direccion
mapa_mortales.save("resultados/mapa_siniestros_mortales.html")

print("==============================================")
print("Mapas de siniestros")
print("==============================================")
print(f"Siniestros en el mapa de calor: {len(datos_calor)}")
print(f"Siniestros mortales en el mapa: {len(mortales)}")
print("\nArchivos generados en la carpeta 'resultados':")
print(" - parroquias_geograficas.csv")
print(" - mapa_parroquias.html")
print(" - mapa_calor_siniestros.html")
print(" - mapa_siniestros_mortales.html")

print("\nAbre en tu navegador:")
print(" - mapa_parroquias.html")
print(" - mapa_calor_siniestros.html")
print(" - mapa_siniestros_mortales.html")
