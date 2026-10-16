import pandas as pandas
import matplotlib.pyplot as plt
archivo = ('accidentes_transito_quito_transformado.csv')
df = pandas.read_csv(archivo, sep=';', encoding='utf-8-sig', parse_dates=['Fecha'])
print ("\n**********************************************")
print ("*      3. ESTADISTICA DESCRIPTIVA             *")
print ("**********************************************")

print (f"Registro: {len(df)}")
print (f"Variables: {len(df.columns)}")
print ("\n**********************************************")
print ("* INFORMACION GENERAL *")
print ("**********************************************")
print (df.info())

print ("\n**********************************************")
print ("* ESTADISTICA DESCRIPTIVA *")
print ("**********************************************")

estadisticas = df.describe()
print (estadisticas)

print ("\n**********************************************")
print ("* MEDIANA *")
print ("**********************************************")
columnas_numericas = ['Fallecidos', 'Lesionados', 'Vehiculos']

for columna in columnas_numericas:
    if columna in df.columns:
        mediana = df[columna].median() #solo 2 decimales
        print (f"Mediana de {columna}: {mediana:.2f}")

print ("\n**********************************************")
print ("* PROMEDIOS *")
print ("**********************************************")

for columna in columnas_numericas:
    if columna in df.columns:
        promedio = df[columna].mean() #solo 2 decimales
        print (f"Promedio de {columna}: {promedio:.2f}")

print ("\n**********************************************")
print ("* MODA DE LAS VARIABLES CATEGORICAS *")
print ("**********************************************")

columnas_categoricas = ['Tipo_Vehiculo', 'Condicion_Climatica', 'Situacion_Via']

for columna in columnas_categoricas:
    if columna in df.columns:
        moda = df[columna].mode().iloc[0] if not df[columna].mode().empty else "No hay moda"
        print (f"Moda de {columna}: {moda}")
import os
os.makedirs('resultados', exist_ok=True)
#crea la carpeta 'resultados' donde se guardan las tablas (.csv) y los graficos (.png)

print ("\n**********************************************")
print ("* MODA DE LAS VARIABLES DEL SINIESTRO *")
print ("**********************************************")
columnas_siniestro = ['Dia_Semana', 'Franja_Horaria', 'Tipo_Siniestro', 'Causa', 'Gravedad']

for columna in columnas_siniestro:
    moda = df[columna].mode().iloc[0]
    print (f"Moda de {columna}: {moda}")
#la moda es el valor que mas se repite: el dia, la franja, el tipo y la causa mas frecuentes

print ("\n**********************************************")
print ("* TABLA 1: RESUMEN ESTADISTICO *")
print ("**********************************************")
resumen = df[['Fallecidos', 'Lesionados', 'Total_Victimas', 'Hora_Num']].describe().round(2)
print (resumen)
resumen.to_csv('resultados/resumen_estadistico.csv', sep=';', encoding='utf-8-sig')
#describe() va a calcula cantidad, promedio, desviacion, minimo, maximo y cuartiles de cada columna

print ("\n**********************************************")
print ("* TABLA 2: SINIESTROS POR AÑO *")
print ("**********************************************")
por_anio = df.groupby('Año')[['Siniestros', 'Fallecidos', 'Lesionados']].sum()
print (por_anio)
por_anio.to_csv('resultados/siniestros_por_anio.csv', sep=';', encoding='utf-8-sig')
#agrupa por año y suma los siniestros, fallecidos y lesionados de cada uno
#2026 es un año parcial (solo enero a agosto)

print ("\n**********************************************")
print ("* TABLA 3: PROMEDIO DE VICTIMAS POR TIPO DE SINIESTRO *")
print ("**********************************************")
por_tipo = df.groupby('Tipo_Siniestro').agg(
    Siniestros=('Siniestros', 'sum'),
    Promedio_Victimas=('Total_Victimas', 'mean'),
)
por_tipo['Promedio_Victimas'] = por_tipo['Promedio_Victimas'].round(2)
por_tipo = por_tipo.sort_values('Siniestros', ascending=False)
print (por_tipo)
por_tipo.to_csv('resultados/victimas_por_tipo_siniestro.csv', sep=';', encoding='utf-8-sig')
#cuantos siniestros hay de cada tipo y cuantas victimas deja en promedio cada uno

print ("\n**********************************************")
print ("* GRAFICOS *")
print ("**********************************************")

#GRAFICO 1: barras - siniestros por año
plt.figure(figsize=(9, 5))
plt.bar(por_anio.index.astype(str), por_anio['Siniestros'], color='orange')
plt.title('Siniestros de transito por año en Quito')
plt.xlabel('Año')
plt.ylabel('Numero de siniestros')
plt.savefig('resultados/grafico_barras_siniestros_por_anio.png')
plt.close()
#savefig guarda el grafico como imagen y close lo cierra para empezar el siguiente

#GRAFICO 2: barras - siniestros por dia de la semana
orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
por_dia = df['Dia_Semana'].value_counts().reindex(orden_dias)
#reindex ordena los dias de lunes a domingo (si no, salen ordenados por cantidad)
plt.figure(figsize=(9, 5))
plt.bar(por_dia.index, por_dia.values, color=['steelblue', 'steelblue', 'steelblue', 'steelblue', 'steelblue', 'red', 'red'])
plt.title('Siniestros por dia de la semana')
plt.xlabel('Dia de la semana')
plt.ylabel('Numero de siniestros')
plt.savefig('resultados/grafico_barras_siniestros_por_dia.png')
plt.close()
#el fin de semana se pinta de rojo para resaltarlo

#GRAFICO 3: torta - gravedad de los siniestros
por_gravedad = df['Gravedad'].value_counts()
plt.figure(figsize=(7, 7))
plt.pie(por_gravedad.values, labels=por_gravedad.index, autopct='%1.1f%%', colors=['lightgray', 'orange', 'red'])
plt.title('Gravedad de los siniestros')
plt.savefig('resultados/grafico_torta_gravedad.png')
plt.close()
#autopct muestra el porcentaje de cada parte de la torta

#GRAFICO 4: torta - siniestros por franja horaria
por_franja = df[df['Franja_Horaria'] != 'N/D']['Franja_Horaria'].value_counts()
#se quitan los 2 siniestros que no tienen hora (N/D)
plt.figure(figsize=(7, 7))
colores_franja = {'Madrugada': 'slategray', 'Mañana': 'gold', 'Tarde': 'darkorange', 'Noche': 'steelblue'}
plt.pie(por_franja.values, labels=por_franja.index, autopct='%1.1f%%', colors=[colores_franja[f] for f in por_franja.index])
#cada franja tiene su propio color, sin importar el orden en que salga
plt.title('Siniestros por franja horaria')
plt.savefig('resultados/grafico_torta_franja_horaria.png')
plt.close()

#GRAFICO 5: histograma - siniestros por hora del dia
plt.figure(figsize=(10, 5))
plt.hist(df['Hora_Num'].dropna(), bins=24, range=(0, 24), color='seagreen', edgecolor='white')
plt.title('Distribucion de siniestros por hora del dia')
plt.xlabel('Hora del dia (0 a 23)')
plt.ylabel('Numero de siniestros')
plt.xticks(range(0, 24))
plt.savefig('resultados/grafico_histograma_hora.png')
plt.close()
#bins=24 crea una barra por cada hora; dropna quita los siniestros sin hora

print ("Tablas (.csv) y graficos (.png) guardados en la carpeta 'resultados'")
