import os

import pandas as pd
import matplotlib.pyplot as plt
archivo = "accidentes_transito_quito_transformado.csv"
df = pd.read_csv(archivo, sep=";", encoding="utf-8-sig", low_memory=False)
print("====================")
print("VARIABLES DE SINIESTRALIDAD Y CORRELACIONES")
print("====================")

os.makedirs("resultados", exist_ok=True)
#carpeta donde se guardan las tablas (.csv) y los graficos (.png)

#la correlacion mide si dos variables numericas se mueven juntas.
#en este dataset cada fila es UN siniestro, y asi casi no hay nada que comparar.
#por eso primero se arma una tabla por PARROQUIA: cada parroquia tiene su numero de
#siniestros, fallecidos y lesionados, y esas columnas si se pueden correlacionar

cruces = pd.read_csv("cruces_clima_parroquia_quito_2024_2026.csv", sep=";", encoding="utf-8-sig", low_memory=False)
df = df.merge(cruces[["ID_Registro", "Parroquia_DMQ"]], on="ID_Registro")
df = df[df["Parroquia_DMQ"] != "N/D"]
#se agrega la parroquia real de cada siniestro (igual que en 05_accidentes_por_destino.py)
#solo quedan los siniestros de 2024 a 2026, que son los que tienen ubicacion

parroquias = df.groupby("Parroquia_DMQ").agg(
    siniestros=("Siniestros", "sum"),
    fallecidos=("Fallecidos", "sum"),
    lesionados=("Lesionados", "sum"),
    victimas_promedio=("Total_Victimas", "mean"),
)
parroquias["letalidad"] = parroquias["fallecidos"] / parroquias["siniestros"] * 100
#letalidad = fallecidos por cada 100 siniestros

parroquias = parroquias[parroquias["siniestros"] >= 30]
#solo parroquias con al menos 30 siniestros.
#en una parroquia con 1 o 2 siniestros, un solo fallecido da 50% o 100% de letalidad y distorsiona todo

print(f"Parroquias analizadas: {len(parroquias)}")
print(parroquias.round(2))

print("\n========================")
print("MATRIZ DE CORRELACION")
print("========================")
correlaciones = parroquias.corr().round(2)
print(correlaciones)
#corr() compara todas las columnas entre si. El resultado va de -1 a 1:
#cerca de 1  = cuando una sube, la otra tambien sube
#cerca de -1 = cuando una sube, la otra baja
#cerca de 0  = no tienen relacion

print("\n========================")
print("CORRELACION CON FALLECIDOS")
print("========================")
correlacion_fallecidos = (
    correlaciones["fallecidos"]
    .drop("fallecidos")
    .sort_values(ascending=False)
)
print(correlacion_fallecidos)
#que tan relacionada esta cada variable con el numero de fallecidos

def interpretar_correlacion(valor):
    valor_abs = abs(valor)
    if valor_abs >= 0.80:
        fuerza = "muy fuerte"
    elif valor_abs >= 0.60:
        fuerza = "fuerte"
    elif valor_abs >= 0.40:
        fuerza = "moderada"
    elif valor_abs >= 0.20:
        fuerza = "debil"
    else:
        fuerza = "muy debil o inexistente"

    if valor > 0:
        direccion = "positiva"
    elif valor < 0:
        direccion = "negativa"
    else:
        direccion = "sin direccion"

    return f"{fuerza} y {direccion}"
#convierte el numero de la correlacion en palabras (fuerte, debil, positiva, negativa)

print("\n========================")
print("INTERPRETACION DE CORRELACIONES")
print("========================")
relaciones = [
    ("siniestros", "fallecidos"),
    ("siniestros", "lesionados"),
    ("siniestros", "letalidad"),
    ("siniestros", "victimas_promedio"),
    ("lesionados", "fallecidos"),
    ("victimas_promedio", "letalidad"),
]
#pares de variables que interesa comparar

filas = []
for variable_1, variable_2 in relaciones:
    valor = correlaciones.loc[variable_1, variable_2]
    interpretacion = interpretar_correlacion(valor)
    filas.append([variable_1, variable_2, valor, interpretacion])
    print(f"{variable_1} vs {variable_2}: {valor} -> {interpretacion}")

interpretaciones = pd.DataFrame(
    filas,
    columns=["variable_1", "variable_2", "correlacion", "interpretacion"]
)

print("\n========================")
print("RELACIONES PRINCIPALES")
print("========================")
interpretaciones["fuerza"] = interpretaciones["correlacion"].abs()
principales = interpretaciones.sort_values("fuerza", ascending=False).drop(columns="fuerza")
interpretaciones = interpretaciones.drop(columns="fuerza")
print(principales.head(3))
#las 3 relaciones mas fuertes (se ordena por el valor sin signo, por eso se usa abs)

correlaciones.to_csv("resultados/matriz_correlacion.csv", sep=";", encoding="utf-8-sig")
correlacion_fallecidos.to_csv("resultados/correlacion_con_fallecidos.csv", sep=";", encoding="utf-8-sig")
interpretaciones.to_csv("resultados/interpretacion_correlaciones.csv", sep=";", encoding="utf-8-sig", index=False)
parroquias.round(2).to_csv("resultados/indicadores_por_parroquia.csv", sep=";", encoding="utf-8-sig")

#GRAFICO 21: matriz de correlacion (mapa de calor)
plt.figure(figsize=(9, 7))
plt.imshow(correlaciones, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(label="Correlacion")
plt.xticks(range(len(correlaciones.columns)), correlaciones.columns, rotation=45, ha="right")
plt.yticks(range(len(correlaciones.columns)), correlaciones.columns)
for fila in range(len(correlaciones)):
    for columna in range(len(correlaciones.columns)):
        plt.text(columna, fila, correlaciones.iloc[fila, columna], ha="center", va="center")
plt.title("Matriz de correlacion entre variables de siniestralidad")
plt.tight_layout()
plt.savefig("resultados/21_matriz_correlacion.png", dpi=300)
plt.close()
#imshow pinta cada casilla segun su valor: rojo = positiva, azul = negativa
#los dos for escriben el numero dentro de cada casilla

#GRAFICO 22: correlacion de cada variable con los fallecidos
plt.figure(figsize=(9, 6))
correlacion_fallecidos.plot(kind="bar", color="firebrick")
plt.axhline(0, color="black", linewidth=1)
plt.title("Correlacion de cada variable con el numero de fallecidos")
plt.xlabel("Variable")
plt.ylabel("Correlacion")
plt.ylim(-1, 1)
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("resultados/22_correlacion_con_fallecidos.png", dpi=300)
plt.close()

#GRAFICO 23: siniestros vs fallecidos
plt.figure(figsize=(9, 6))
plt.scatter(parroquias["siniestros"], parroquias["fallecidos"], color="steelblue")
plt.title(f"Siniestros vs fallecidos por parroquia (correlacion = {correlaciones.loc['siniestros', 'fallecidos']})")
plt.xlabel("Siniestros")
plt.ylabel("Fallecidos")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("resultados/23_siniestros_vs_fallecidos.png", dpi=300)
plt.close()
#scatter dibuja un punto por cada parroquia: si los puntos suben en diagonal, hay correlacion positiva

#GRAFICO 24: siniestros vs lesionados
plt.figure(figsize=(9, 6))
plt.scatter(parroquias["siniestros"], parroquias["lesionados"], color="darkorange")
plt.title(f"Siniestros vs lesionados por parroquia (correlacion = {correlaciones.loc['siniestros', 'lesionados']})")
plt.xlabel("Siniestros")
plt.ylabel("Lesionados")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("resultados/24_siniestros_vs_lesionados.png", dpi=300)
plt.close()

#GRAFICO 25: siniestros vs letalidad
plt.figure(figsize=(9, 6))
plt.scatter(parroquias["siniestros"], parroquias["letalidad"], color="seagreen")
plt.title(f"Siniestros vs letalidad por parroquia (correlacion = {correlaciones.loc['siniestros', 'letalidad']})")
plt.xlabel("Siniestros")
plt.ylabel("Fallecidos por cada 100 siniestros")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("resultados/25_siniestros_vs_letalidad.png", dpi=300)
plt.close()
#plt.close() cierra cada grafico despues de guardarlo
#(si se quiere ver en pantalla, se puede poner plt.show() antes del close)

print("\n==============================")
print("ANALISIS DE CORRELACIONES FINALIZADO")
print("==============================")
print("Archivos generados en la carpeta 'resultados': ")
print("matriz_correlacion.csv")
print("correlacion_con_fallecidos.csv")
print("interpretacion_correlaciones.csv")
print("indicadores_por_parroquia.csv")
print("\nGraficos: ")
print("21_matriz_correlacion.png")
print("22_correlacion_con_fallecidos.png")
print("23_siniestros_vs_fallecidos.png")
print("24_siniestros_vs_lesionados.png")
print("25_siniestros_vs_letalidad.png")
