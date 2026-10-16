import os

import pandas as pd
import matplotlib.pyplot as plt
archivo = "accidentes_transito_quito_transformado.csv"
df = pd.read_csv(archivo, sep=";", encoding="utf-8-sig", low_memory=False)
print("====================")
print("ANALISIS DE TEMPORADAS Y ESTACIONALIDAD DE SINIESTROS")
print("====================")

os.makedirs("resultados", exist_ok=True)
#carpeta donde se guardan las tablas (.csv) y los graficos (.png)

df = df[df["Año"] < 2026]
#solo se usan los años completos (2017 a 2025).
#2026 tiene datos solo de enero a agosto y haria ver mas bajos los ultimos meses del año

print(f"Registros analizados: {len(df)}")
nombres_meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}
#el dataset ya tiene la columna Mes_Num (numero del mes), creada en la transformacion

siniestros_mes = (
    df.groupby("Mes_Num")["Siniestros"]
    .sum()
    .reindex(range(1, 13))
)
siniestros_mes.index = [
    nombres_meses[i]
    for i in siniestros_mes.index
]
#suma los siniestros de cada mes y cambia el numero del mes por su nombre
print("\n========================")
print("SINIESTROS POR MES")
print("========================")
print(siniestros_mes)

fallecidos_mes = (
    df.groupby("Mes_Num")["Fallecidos"]
    .sum()
    .reindex(range(1, 13))
)
fallecidos_mes.index = [
    nombres_meses[i]
    for i in fallecidos_mes.index
]
print("\n========================")
print("FALLECIDOS POR MES")
print("========================")
print(fallecidos_mes)

victimas_promedio_mes = (
    df.groupby("Mes_Num")["Total_Victimas"]
    .mean()
    .reindex(range(1, 13))
)
victimas_promedio_mes.index = [
    nombres_meses[i]
    for i in victimas_promedio_mes.index
]
#cuantas victimas deja en promedio cada siniestro segun el mes
print("\n**************************************")
print("*  Victimas promedio por siniestro segun el mes  *")
print("**************************************")
print(victimas_promedio_mes.round(2))

siniestros_trimestre = (
    df.groupby("Trimestre")["Siniestros"]
    .sum()
    .sort_index()
)
siniestros_trimestre.index = [
    "Primer trimestre",
    "Segundo trimestre",
    "Tercer trimestre",
    "Cuarto trimestre"
]
#los trimestres vienen como I, II, III y IV; se les pone el nombre completo
print("\n========================")
print("SINIESTROS POR TRIMESTRE")
print("========================")
print(siniestros_trimestre)

mes_mayor = siniestros_mes.idxmax()
cantidad_mayor = siniestros_mes.max()
mes_menor = siniestros_mes.idxmin()
cantidad_menor = siniestros_mes.min()
#idxmax da el nombre del mes con mas siniestros y max da la cantidad
print("\n========================")
print("MESES CON MAYOR Y MENOR SINIESTRALIDAD")
print("========================")

print(
    f"Mayor cantidad de siniestros: "
    f"{mes_mayor} ({cantidad_mayor})"
)
print(
    f"Menor cantidad de siniestros: "
    f"{mes_menor} ({cantidad_menor})"
)
promedio_mensual = siniestros_mes.mean()
print(
    f"Promedio mensual de siniestros: "
    f"{promedio_mensual:.2f}"
)

def clasificar_temporada(valor, promedio):
    if valor > promedio:
        return "Alta"
    elif valor < promedio:
        return "Baja"
    else:
        return "Media"
#un mes es de temporada Alta si tiene mas siniestros que el promedio mensual, y Baja si tiene menos

temporadas = siniestros_mes.apply(
    lambda x: clasificar_temporada(
        x,
        promedio_mensual)
)
print("\n========================")
print("CLASIFICACION DE TEMPORADAS")
print("========================")
print(temporadas)

estacionalidad = pd.DataFrame({
    "siniestros": siniestros_mes,
    "fallecidos": fallecidos_mes,
    "victimas_promedio": victimas_promedio_mes.round(2),
    "temporada": temporadas
})
estacionalidad["variacion_vs_promedio"] = (
    estacionalidad["siniestros"]
    / promedio_mensual
      * 100
)
estacionalidad["variacion_vs_promedio"] = (
    estacionalidad["variacion_vs_promedio"]
    .round(2)
)
#variacion_vs_promedio: 100 significa igual al promedio; 112 significa 12% mas que el promedio
print("\n==============================")
print("TABLA DE ESTACIONALIDAD")
print("==============================")
print(estacionalidad)

estacionalidad.to_csv(
    "resultados/estacionalidad_siniestros.csv",
    sep=";",
    encoding="utf-8-sig"
)
siniestros_trimestre.to_csv(
    "resultados/siniestros_por_trimestre.csv",
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(12, 6))
plt.plot(
    siniestros_mes.index,
    siniestros_mes.values,
    marker="o",
    linewidth=2,
    color="steelblue"
)
plt.title("Evolucion mensual de siniestros (2017 - 2025)")
plt.xlabel("Mes")
plt.ylabel("Cantidad de siniestros")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "resultados/16_siniestros_por_mes.png",
    dpi=300
)
plt.close()

plt.figure(figsize=(12, 6))
plt.plot(
    fallecidos_mes.index,
    fallecidos_mes.values,
    marker="o",
    linewidth=2,
    color="darkorange"
)
plt.title("Evolucion mensual de fallecidos (2017 - 2025)")
plt.xlabel("Mes")
plt.ylabel("Fallecidos")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "resultados/17_fallecidos_por_mes.png",
    dpi=300
)
plt.close()

plt.figure(figsize=(12, 6))
plt.plot(
    victimas_promedio_mes.index,
    victimas_promedio_mes.values,
    marker="o",
    linewidth=2,
    color="seagreen"
)
plt.title("Victimas promedio por siniestro segun el mes")
plt.xlabel("Mes")
plt.ylabel("Victimas promedio por siniestro")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    "resultados/18_victimas_promedio_por_mes.png",
    dpi=300
)
plt.close()

plt.figure(figsize=(9, 6))
siniestros_trimestre.plot(
    kind="bar",
    color="mediumpurple"
)
plt.title("Cantidad de siniestros por trimestre (2017 - 2025)")
plt.xlabel("Trimestre")
plt.ylabel("Cantidad de siniestros")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(
    "resultados/19_siniestros_por_trimestre.png",
    dpi=300
)
plt.close()

colores = []
for temporada in temporadas:
    if temporada == "Alta":
        colores.append("firebrick")
    elif temporada == "Baja":
        colores.append("steelblue")
    else:
        colores.append("darkorange")
#cada barra toma su color segun la temporada: rojo = Alta, azul = Baja

plt.figure(figsize=(12, 6))
plt.bar(
    temporadas.index,
    siniestros_mes.values,
    color=colores
)
plt.axhline(
    promedio_mensual,
    color="black",
    linestyle="--",
    label="promedio mensual"
)
#axhline dibuja la linea punteada del promedio para ver que meses la superan
plt.title("Estacionalidad de los siniestros (rojo = temporada alta, azul = temporada baja)")
plt.xlabel("Mes")
plt.ylabel("Cantidad de siniestros")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(
    "resultados/20_estacionalidad.png",
    dpi=300
)
plt.close()
#plt.close() cierra cada grafico despues de guardarlo
#(si se quiere ver en pantalla, se puede poner plt.show() antes del close)

print("\n==============================")
print("ANALISIS DE TEMPORADAS FINALIZADO")
print("==============================")

print("Archivos generados en la carpeta 'resultados': ")
print("estacionalidad_siniestros.csv")
print("siniestros_por_trimestre.csv")
print("\nGraficos: ")
print("16_siniestros_por_mes.png")
print("17_fallecidos_por_mes.png")
print("18_victimas_promedio_por_mes.png")
print("19_siniestros_por_trimestre.png")
print("20_estacionalidad.png")
