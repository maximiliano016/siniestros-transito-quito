import pandas as pd
import numpy as np
# cargar el dataset
archivo = ('accidentes_transito_quito_2017_2026.csv')
df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', low_memory=False)
#el archivo usa ';' como separador y tiene tildes (utf-8), por eso se indican sep y encoding
print ("**************************************")
print ("*  LIMPIEZA Y PREPARACION DE DATOS  *")
print ("**************************************")
print ("\nDataSet cargado correctamente con exito")
print (f"filas: {df.shape[0]}")
#imprimir el numero de filas 

print (f"columnas: {df.shape[1]}")
#imprimir el numero de columnas

print ("\n**********************************************")
print ("*         INFORMACION INICIAL              *")
print ("**********************************************")
print (df.info())
#imprime toda la informacion del dataset (num filas, culumnas, tipos de datos, valores nulos, etc.)

print ("\n**********************************************")
print ("*         VALORES NULOS          *")
print ("**********************************************")
nulos = df.isnull().sum()
print (nulos)
#suma de valores nulos por columna

print (nulos)
print("\n**********************************************")
print ("*         TOTAL DE VALORES NULOS          *")
print ("**********************************************")
print (df.isnull().sum().sum())
#imprime el total de valores nulos en todo el dataset

print("\n**********************************************")
print ("*         REGISTRO DE DUPLICADOS          *")
print ("**********************************************")
duplicados = df.duplicated().sum()
#suma de registros duplicados en el dataset
print (duplicados)

if duplicados > 0:
    df = df.drop_duplicates()
    #si hay registros duplicados, se eliminan del dataset
    print("\n**********************************************")
    print ("*         DUPLICADOS ELIMINADOS           *")
    print ("**********************************************")
    print (f"Registros duplicados eliminados: {duplicados}")
else:
    print("\n**********************************************")
    print ("*         NO HAY DUPLICADOS                *")
    print ("**********************************************")

df['Fecha'] = pd.to_datetime(
    df['Fecha'],
    format='%Y-%m-%d',
    errors='coerce')
#sirve para convertir la columna 'fecha' a tipo datetime, si hay errores se convierten a NaT

print ("\n Conversion de fechas completada correctamente")

print ("\n**********************************************")
print ("*              VALIDACIONES                  *")
print ("**********************************************")

print ("\n1. DATOS NO DISPONIBLES (N/D) POR COLUMNA")
nd = (df == 'N/D').sum()
print (nd)
#en este dataset los datos que faltan vienen escritos como N/D, no vacios,
#por eso isnull() no los detecta y se cuentan aparte
print (f"\nFechas sin dato (quedaron vacias al convertir): {df['Fecha'].isnull().sum()}")
#la columna Fecha ya se convirtio antes, asi que los N/D ahora son vacios 

print ("\n2. SINIESTROS SIN UBICACION (SIN COORDENADAS)")
sin_ubicacion = df[df['Latitud'] == 'N/D']
print (f"Siniestros sin coordenadas: {len(sin_ubicacion)}")
print (f"Siniestros con coordenadas: {len(df) - len(sin_ubicacion)}")
print ("\nSiniestros sin coordenadas por año:")
print (sin_ubicacion['Año'].value_counts().sort_index())
#de 2017 a 2023 la fuente (INEC) no publica ubicacion, desde 2024 (ANT) si

print ("\n3. SOLO SINIESTROS DE QUITO")
print (f"Provincias: {df['Provincia'].unique().tolist()}")
print (f"Cantones: {df['Cantón'].unique().tolist()}")
#si solo aparece Pichincha y Quito, no hay siniestros de otras ciudades

print ("\n4. TOTAL DE VICTIMAS = FALLECIDOS + LESIONADOS")
errores_victimas = df[df['Fallecidos'] + df['Lesionados'] != df['Total_Victimas']]
print (f"Registros donde no cuadra el total: {len(errores_victimas)}")
#si da 0, todos los totales de victimas estan bien sumados

print ("\n5. SINIESTROS POR AÑO")
print (df['Año'].value_counts().sort_index())
#2026 tiene menos siniestros porque solo hay datos de enero a agosto (año parcial)

print ("\n**********************************************")
print ("*         GUARDAR DATOS LIMPIOS              *")
print ("**********************************************")
df.to_csv(
    'accidentes_transito_quito_limpio.csv',
    sep=';',
    encoding='utf-8-sig',
    index=False,
    date_format='%Y-%m-%d')
#guarda el dataset limpio en un archivo nuevo, sin tocar el original
#sep=';' y utf-8-sig para que se abra bien en Excel con tildes
#index=False para que no agregue una columna extra con el numero de fila
print ("Archivo limpio guardado: accidentes_transito_quito_limpio.csv")
print (f"filas: {df.shape[0]} | columnas: {df.shape[1]}")