import os

import pandas as pd
from sklearn.preprocessing import StandardScaler

# ============================================================
# 1. CARGAR DATASET
# ============================================================

archivo = "accidentes_transito_quito_transformado.csv"

df = pd.read_csv(archivo, sep=";", encoding="utf-8-sig", low_memory=False)

os.makedirs("resultados", exist_ok=True)
#carpeta donde se guardan los archivos generados

print("==============================================")
print("PREPARACIÓN PARA CLUSTERING")
print("==============================================")

print(f"Registros originales: {len(df)}")



#el clustering agrupa elementos parecidos. 
#agrupar las PARROQUIAS, para encontrar grupos de zonas con un riesgo parecido.
#por eso primero se pasa de "una fila por siniestro" a "una fila por parroquia"

cruces = pd.read_csv("cruces_clima_parroquia_quito_2024_2026.csv", sep=";", encoding="utf-8-sig", low_memory=False)
df = df.merge(cruces[["ID_Registro", "Parroquia_DMQ"]], on="ID_Registro")
df = df[df["Parroquia_DMQ"] != "N/D"]
#se agrega la parroquia real de cada siniestro (igual que en 05 y 08)
#solo quedan los siniestros de 2024 a 2026, que son los que tienen ubicacion

df["es_fin_de_semana"] = (df["Fin_de_Semana"] == "SI") * 100
df["es_madrugada"] = (df["Franja_Horaria"] == "Madrugada") * 100
df["es_mortal"] = (df["Gravedad"] == "Mortal") * 100
#columnas de apoyo: valen 100 si el siniestro cumple la condicion y 0 si no.
#al sacar el promedio por parroquia se obtiene directamente el porcentaje

parroquias = df.groupby("Parroquia_DMQ").agg(
    siniestros=("Siniestros", "sum"),
    fallecidos=("Fallecidos", "sum"),
    lesionados=("Lesionados", "sum"),
    victimas_promedio=("Total_Victimas", "mean"),
    pct_mortales=("es_mortal", "mean"),
    pct_fin_de_semana=("es_fin_de_semana", "mean"),
    pct_madrugada=("es_madrugada", "mean"),
)
parroquias["letalidad"] = parroquias["fallecidos"] / parroquias["siniestros"] * 100
#letalidad = fallecidos por cada 100 siniestros

parroquias = parroquias[parroquias["siniestros"] >= 30]
#solo parroquias con al menos 30 siniestros (igual que en las correlaciones):
#con muy pocos siniestros los porcentajes no son confiables

print(f"Parroquias a agrupar: {len(parroquias)}")


# ============================================================
# 3. SELECCIONAR VARIABLES PARA CLUSTERING
# ============================================================

variables_clustering = [
    "siniestros",
    "fallecidos",
    "lesionados",
    "victimas_promedio",
    "letalidad",
    "pct_mortales",
    "pct_fin_de_semana",
    "pct_madrugada"
]

# Verificar qué variables existen
variables_disponibles = [
    columna
    for columna in variables_clustering
    if columna in parroquias.columns
]

print("\n==============================================")
print("VARIABLES SELECCIONADAS")
print("==============================================")

for columna in variables_disponibles:
    print("-", columna)
#las 3 primeras miden CUANTOS siniestros hay, las 3 siguientes que tan GRAVES son
#y las 2 ultimas CUANDO ocurren


# ============================================================
# 4. CREAR DATASET PARA CLUSTERING
# ============================================================

datos_clustering = parroquias[variables_disponibles].copy()


# ============================================================
# 5. CONVERTIR A NUMÉRICO
# ============================================================

for columna in variables_disponibles:

    datos_clustering[columna] = pd.to_numeric(
        datos_clustering[columna],
        errors="coerce"
    )


# ============================================================
# 6. REVISAR VALORES FALTANTES
# ============================================================

print("\n==============================================")
print("VALORES FALTANTES")
print("==============================================")

print(
    datos_clustering.isnull().sum()
)


# ============================================================
# 7. ELIMINAR REGISTROS CON VALORES FALTANTES
# ============================================================

registros_antes = len(datos_clustering)

datos_clustering = datos_clustering.dropna()

registros_despues = len(datos_clustering)

print("\n==============================================")
print("LIMPIEZA")
print("==============================================")

print(
    f"Registros antes: {registros_antes}"
)

print(
    f"Registros después: {registros_despues}"
)

print(
    f"Registros eliminados: "
    f"{registros_antes - registros_despues}"
)


# ============================================================
# 8. ESTANDARIZAR VARIABLES
# ============================================================
#las variables estan en escalas muy distintas: siniestros va de 30 a 680
#y victimas_promedio va de 0,5 a 1,2. Sin estandarizar, el clustering solo
#le haria caso a la variable con numeros mas grandes.
#StandardScaler deja todas las variables con media 0 y desviacion 1

scaler = StandardScaler()

datos_estandarizados = scaler.fit_transform(
    datos_clustering
)


# ============================================================
# 9. CONVERTIR A DATAFRAME
# ============================================================

df_estandarizado = pd.DataFrame(
    datos_estandarizados,
    columns=variables_disponibles,
    index=datos_clustering.index
)


# ============================================================
# 10. MOSTRAR DATOS ESTANDARIZADOS
# ============================================================

print("\n==============================================")
print("DATOS ESTANDARIZADOS")
print("==============================================")

print(
    df_estandarizado.head()
)
#un valor positivo significa que la parroquia esta sobre el promedio en esa variable,
#y un valor negativo, que esta por debajo


# ============================================================
# 11. COMPROBAR MEDIA Y DESVIACIÓN ESTÁNDAR
# ============================================================

print("\n==============================================")
print("COMPROBACIÓN DE ESTANDARIZACIÓN")
print("==============================================")

print("\nMedia:")
print(
    df_estandarizado.mean().round(4)
)

print("\nDesviación estándar:")
print(
    df_estandarizado.std().round(4)
)
#si la media da 0 y la desviacion da cerca de 1, la estandarizacion se hizo bien
#(da 1,01 y no 1 exacto porque pandas y StandardScaler dividen de forma un poco distinta; es normal)


# ============================================================
# 12. GUARDAR DATOS PREPARADOS
# ============================================================
#se guarda el nombre de la parroquia (index=True) para saber despues
#a que parroquia corresponde cada fila

df_estandarizado.to_csv(
    "resultados/datos_clustering_estandarizados.csv",
    sep=";",
    encoding="utf-8-sig"
)

datos_clustering.round(2).to_csv(
    "resultados/datos_clustering_originales.csv",
    sep=";",
    encoding="utf-8-sig"
)


# ============================================================
# 13. GUARDAR INFORMACIÓN DE LAS VARIABLES
# ============================================================

informacion_variables = pd.DataFrame({
    "variable": variables_disponibles,
    "media_original": [
        datos_clustering[columna].mean()
        for columna in variables_disponibles
    ],
    "desviacion_original": [
        datos_clustering[columna].std()
        for columna in variables_disponibles
    ],
    "minimo": [
        datos_clustering[columna].min()
        for columna in variables_disponibles
    ],
    "maximo": [
        datos_clustering[columna].max()
        for columna in variables_disponibles
    ]
})

informacion_variables = informacion_variables.round(2)

print("\n==============================================")
print("INFORMACIÓN DE LAS VARIABLES")
print("==============================================")

print(informacion_variables)

informacion_variables.to_csv(
    "resultados/informacion_variables_clustering.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 14. FINAL
# ============================================================

print("\n==============================================")
print("PREPARACIÓN PARA CLUSTERING FINALIZADA")
print("==============================================")

print("\nArchivos generados en la carpeta 'resultados':")

print("- datos_clustering_estandarizados.csv")
print("- datos_clustering_originales.csv")
print("- informacion_variables_clustering.csv")

print("\nLos datos están preparados para aplicar")
print("el algoritmo de clustering.")
