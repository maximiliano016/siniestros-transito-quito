import os
import matplotlib.pyplot as plt
import pandas as pd

archivo = "accidentes_transito_quito_transformado.csv"
df = pd.read_csv(archivo, sep=";", encoding="utf-8-sig", low_memory=False)

os.makedirs("resultados", exist_ok=True)
#carpeta donde se guardan las tablas (.csv) y los graficos (.png)

print("**************************************")
print("*  CAUSAS Y PERFIL DE LOS SINIESTROS  *")
print("**************************************")
print(f"Archivo usado: {archivo}")
print(f"Registros: {len(df)}")

causa = (
    df.groupby("Causa")["Siniestros"]
    .sum()
    .sort_values(ascending=False)
)

print("**************************************")
print("*  Siniestros por causa  *")
print("**************************************")
print(causa)
#suma los siniestros de cada causa y los ordena de mayor a menor

zona = (
    df.groupby("Zona")["Siniestros"]
    .sum()
    .sort_values(ascending=False)
)
#siniestros en zona urbana y en zona rural

orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes = (
    df[df["Año"] < 2026]
    .groupby("Mes")["Siniestros"]
    .sum()
    .reindex(orden_meses)
)
#siniestros por mes, ordenados de enero a diciembre
#no se incluye 2026 porque solo tiene datos de enero a agosto y haria ver mas bajos los ultimos meses

#las 3 variables siguientes solo existen desde 2024
#un siniestro puede tener varios vehiculos y varias personas, y vienen separados con '|'
#split los separa y explode pone cada uno en su propia fila

vehiculos = df[df["Tipo_Vehiculo"] != "N/D"]["Tipo_Vehiculo"].str.split("|").explode()
vehiculos = vehiculos.replace("SCOOTER ELECTRICO", "SCOOTER ELÉCTRICO")
#la misma categoria venia escrita con tilde y sin tilde, se unifica
tipo_vehiculo = vehiculos.value_counts()
#cuantos vehiculos de cada tipo participaron en siniestros

personas_sexo = df[df["Sexo"] != "N/D"]["Sexo"].str.split("|").explode()
sexo = personas_sexo.value_counts()
#cuantas personas involucradas son hombres, mujeres o no identificadas

orden_edades = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49",
                "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90+"]
personas_edad = df[df["Grupo_Edad"] != "N/D"]["Grupo_Edad"].str.split("|").explode()
grupo_edad = personas_edad.value_counts().reindex(orden_edades)
#personas involucradas por grupo de edad, ordenadas de menor a mayor
#no se incluyen las personas con edad no identificada

tipo_gravedad = pd.pivot_table(
    df,
    values="Siniestros",
    index="Tipo_Siniestro",
    columns="Gravedad",
    aggfunc="sum",
    fill_value=0,
)
#tabla cruzada: cuantos siniestros de cada tipo fueron mortales, con lesionados o solo daños

perfil = (
    df.groupby("Zona")
    .agg(
        siniestros=("Siniestros", "sum"),
        fallecidos=("Fallecidos", "sum"),
        lesionados=("Lesionados", "sum"),
        victimas_promedio=("Total_Victimas", "mean"),
        hora_promedio=("Hora_Num", "mean"),
    )
    .round(2)
)

perfil["fallecidos_por_100_siniestros"] = (
    df.groupby("Zona")["Fallecidos"].sum()
    / df.groupby("Zona")["Siniestros"].sum()
    * 100
)
perfil = perfil.round(2)
#perfil de los siniestros en zona urbana y rural: cuantos son, cuantas victimas dejan y que tan mortales son

print("**************************************")
print("*  Perfil por zona  *")
print("**************************************")
print(perfil)

causa.to_csv("resultados/siniestros_por_causa.csv", sep=";", encoding="utf-8-sig")
zona.to_csv("resultados/siniestros_por_zona.csv", sep=";", encoding="utf-8-sig")
mes.to_csv("resultados/siniestros_por_mes.csv", sep=";", encoding="utf-8-sig")
tipo_vehiculo.to_csv("resultados/vehiculos_por_tipo.csv", sep=";", encoding="utf-8-sig")
sexo.to_csv("resultados/personas_por_sexo.csv", sep=";", encoding="utf-8-sig")
grupo_edad.to_csv("resultados/personas_por_grupo_edad.csv", sep=";", encoding="utf-8-sig")
tipo_gravedad.to_csv("resultados/tipo_siniestro_gravedad.csv", sep=";", encoding="utf-8-sig")
perfil.to_csv("resultados/perfil_por_zona.csv", sep=";", encoding="utf-8-sig")

causa_top = causa.head(10).sort_values()
causa_top.index = causa_top.index.str[:45]
#solo las 10 causas principales; str[:45] recorta los nombres a 45 letras para que entren en el grafico
plt.figure(figsize=(12, 6))
causa_top.plot(kind="barh", color="skyblue")
plt.xlabel("Siniestros")
plt.ylabel("Causa")
plt.title("10 causas mas frecuentes de siniestros")
plt.tight_layout()
plt.savefig("resultados/10_siniestros_por_causa.png", dpi=300)
plt.close()
#barh hace las barras horizontales, porque los nombres de las causas son muy largos

plt.figure(figsize=(10, 6))
tipo_vehiculo.plot(kind="bar", color="lightgreen")
plt.xlabel("Tipo de vehiculo")
plt.ylabel("Vehiculos involucrados")
plt.title("Vehiculos involucrados en siniestros por tipo (2024 - 2026)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("resultados/11_vehiculos_por_tipo.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
sexo.plot(kind="bar", color="salmon")
plt.xlabel("Sexo")
plt.ylabel("Personas involucradas")
plt.title("Personas involucradas en siniestros por sexo (2024 - 2026)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("resultados/12_personas_por_sexo.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
grupo_edad.plot(kind="bar", color="mediumpurple")
plt.xlabel("Grupo de edad")
plt.ylabel("Personas involucradas")
plt.title("Personas involucradas en siniestros por grupo de edad (2024 - 2026)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("resultados/13_personas_por_grupo_edad.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
zona.plot(kind="bar", color="gold")
plt.xlabel("Zona")
plt.ylabel("Siniestros")
plt.title("Siniestros por zona")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("resultados/14_siniestros_por_zona.png", dpi=300)
plt.close()

plt.figure(figsize=(10, 6))
mes.plot(kind="bar", color="lightcoral")
plt.xlabel("Mes")
plt.ylabel("Siniestros")
plt.title("Siniestros por mes (2017 - 2025)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("resultados/15_siniestros_por_mes.png", dpi=300)
plt.close()
#plt.close() cierra cada grafico despues de guardarlo
#(si se quiere ver en pantalla, se puede poner plt.show() antes del close)

print("**************************************")
print("Análisis de causas y perfil")
print("***************************************")
print("Archivos generados en la carpeta 'resultados': ")
print("- siniestros_por_causa.csv")
print("- siniestros_por_zona.csv")
print("- siniestros_por_mes.csv")
print("- vehiculos_por_tipo.csv")
print("- personas_por_sexo.csv")
print("- personas_por_grupo_edad.csv")
print("- tipo_siniestro_gravedad.csv")
print("- perfil_por_zona.csv")

print("\nGraficos generados: ")
print("- 10_siniestros_por_causa.png")
print("- 11_vehiculos_por_tipo.png")
print("- 12_personas_por_sexo.png")
print("- 13_personas_por_grupo_edad.png")
print("- 14_siniestros_por_zona.png")
print("- 15_siniestros_por_mes.png")
