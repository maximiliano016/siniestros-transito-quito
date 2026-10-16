import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import numpy as np
import os
archivo = "accidentes_transito_quito_transformado.csv"
df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', low_memory=False)
print ("**************************************")
print ("*  SINIESTROS POR PARROQUIA  *")
print ("**************************************")
#en este proyecto el "destino" es la PARROQUIA: la zona de Quito donde ocurrio el siniestro

os.makedirs('resultados', exist_ok=True)
#carpeta donde se guardan las tablas (.csv) y los graficos (.png)

cruces = pd.read_csv("cruces_clima_parroquia_quito_2024_2026.csv", sep=';', encoding='utf-8-sig', low_memory=False)
df = df.merge(cruces[['ID_Registro', 'Parroquia_DMQ']], on='ID_Registro')
#la base original casi siempre dice 'QUITO' como parroquia, sin decir cual.
#el archivo de cruces tiene la parroquia real de cada siniestro 

df = df[df['Parroquia_DMQ'] != 'N/D']
#se quitan los siniestros que no tienen coordenadas y por eso no tienen parroquia
#solo quedan siniestros de 2024 a 2026, que son los unicos con ubicacion

print (f"Registros :{len(df)}")
print (f"Parroquias analizadas: {df['Parroquia_DMQ'].nunique()}")

siniestros_parroquia = (
    df.groupby("Parroquia_DMQ")["Siniestros"]
    .sum()
    .sort_values(ascending=False)
)
print("**************************************")
print ("Siniestros por parroquia: ")
print("**************************************")
print (siniestros_parroquia)
#suma los siniestros de cada parroquia y los ordena de mayor a menor

victimas_parroquia = (
    df.groupby("Parroquia_DMQ")["Total_Victimas"]
    .sum()
    .sort_values(ascending=False)
)
print("**************************************")
print ("Total de victimas por parroquia: ")
print("**************************************")
print (victimas_parroquia)
#suma los fallecidos y lesionados de cada parroquia

fallecidos_parroquia = (
    df.groupby("Parroquia_DMQ")["Fallecidos"]
    .sum()
    .sort_values(ascending=False)
)
print("**************************************")
print ("Fallecidos por parroquia: ")
print("**************************************")
print (fallecidos_parroquia)

victimas_promedio_parroquia = (
    df.groupby("Parroquia_DMQ")["Total_Victimas"]
    .mean()
    .sort_values(ascending=False)
)
print("**************************************")
print ("Promedio de victimas por siniestro segun parroquia: ")
print("**************************************")
print (victimas_promedio_parroquia)
#cuantas victimas deja en promedio cada siniestro en esa parroquia

letalidad_parroquia = (
    (fallecidos_parroquia / siniestros_parroquia * 100)
    .sort_values(ascending=False)
)
print("**************************************")
print ("Fallecidos por cada 100 siniestros segun parroquia: ")
print("**************************************")
print (letalidad_parroquia)
#que tan mortales son los siniestros de cada parroquia

tipo_parroquia = (
    df.groupby(["Parroquia_DMQ", "Tipo_Siniestro"])
    .size()
    .reset_index(name="cantidad")
)
tipo_principal = (
    tipo_parroquia.sort_values(
        ["Parroquia_DMQ", "cantidad"],
        ascending=[True, False]
        )
        .drop_duplicates("Parroquia_DMQ")
)
print("**************************************")
print ("Tipo de siniestro principal por parroquia: ")
print("**************************************")
print (tipo_principal)
#cuenta cada tipo de siniestro por parroquia y se queda con el mas frecuente de cada una

resumen_parroquia = df.groupby("Parroquia_DMQ").agg(
    siniestros=("Siniestros", "sum"),
    fallecidos=("Fallecidos", "sum"),
    lesionados=("Lesionados", "sum"),
    total_victimas=("Total_Victimas", "sum"),
    victimas_promedio=("Total_Victimas", "mean"),
)
resumen_parroquia["fallecidos_por_100_siniestros"] = resumen_parroquia["fallecidos"] / resumen_parroquia["siniestros"] * 100
resumen_parroquia = resumen_parroquia.round(2).sort_values("siniestros", ascending=False)
print("**************************************")
print ("Resumen por parroquia: ")
print("**************************************")
print (resumen_parroquia)
#una sola tabla con todos los indicadores de cada parroquia

resumen_parroquia.to_csv(
    "resultados/resultado_parroquia.csv",
    sep=';',
    encoding="utf-8-sig",
    )
tipo_principal.to_csv(
    "resultados/tipo_siniestro_principal_parroquia.csv",
    sep=';',
    index=False,
    encoding="utf-8-sig",
    )

#son 65 parroquias, en los graficos solo se muestran las 10 primeras para que se puedan leer

plt.figure(figsize=(10,6))
siniestros_parroquia.head(10).plot(
    kind="bar", color="steelblue")
plt.title("10 parroquias con mas siniestros (2024 - 2026)")
plt.xlabel("Parroquia")
plt.ylabel("Cantidad de siniestros")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("resultados/05_siniestros_por_parroquia.png",
            dpi=300)
plt.close()

plt.figure(figsize=(10,6))
victimas_parroquia.head(10).plot(
    kind="bar", color="darkorange")
plt.title("10 parroquias con mas victimas (2024 - 2026)")
plt.xlabel("Parroquia")
plt.ylabel("Total de victimas")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("resultados/06_victimas_por_parroquia.png",
            dpi=300)
plt.close()

plt.figure(figsize=(10,6))
fallecidos_parroquia.head(10).plot(
    kind="bar", color="crimson")
plt.title("10 parroquias con mas fallecidos (2024 - 2026)")
plt.xlabel("Parroquia")
plt.ylabel("Fallecidos")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("resultados/07_fallecidos_por_parroquia.png",
            dpi=300)
plt.close()

promedio_top = resumen_parroquia.head(10)["victimas_promedio"].sort_values(ascending=False)
#promedio solo de las 10 parroquias con mas siniestros
#(una parroquia con 2 siniestros puede tener un promedio altisimo que engaña)
plt.figure(figsize=(10,6))
promedio_top.plot(
    kind="bar", color="seagreen")
plt.title("Victimas promedio por siniestro (10 parroquias con mas siniestros)")
plt.xlabel("Parroquia")
plt.ylabel("Victimas promedio por siniestro")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("resultados/08_victimas_promedio_por_parroquia.png",
            dpi=300)
plt.close()

letalidad_top = resumen_parroquia.head(10)["fallecidos_por_100_siniestros"].sort_values(ascending=False)
#letalidad solo de las 10 parroquias con mas siniestros
#(en parroquias con muy pocos siniestros un solo fallecido dispara el porcentaje)
plt.figure(figsize=(10,6))
letalidad_top.plot(
    kind="bar", color="mediumpurple")
plt.title("Fallecidos por cada 100 siniestros (10 parroquias con mas siniestros)")
plt.xlabel("Parroquia")
plt.ylabel("Fallecidos por cada 100 siniestros")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("resultados/09_letalidad_por_parroquia.png",
            dpi=300)
plt.close()
#plt.close() cierra cada grafico despues de guardarlo
#(si se quiere ver en pantalla, se puede poner plt.show() antes del close)

print("**************************************")
print ("*  ANALISIS POR PARROQUIA  *")
print ("**************************************")
print ("Archivos generados en la carpeta 'resultados': ")
print ("- resultado_parroquia.csv")
print ("- tipo_siniestro_principal_parroquia.csv")
print ("- 05_siniestros_por_parroquia.png")
print ("- 06_victimas_por_parroquia.png")
print ("- 07_fallecidos_por_parroquia.png")
print ("- 08_victimas_promedio_por_parroquia.png")
print ("- 09_letalidad_por_parroquia.png")