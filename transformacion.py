import pandas as pd
import numpy as np
# cargar el dataset limpio (el que genera 01_limpieza_datos.py)
archivo = ('accidentes_transito_quito_limpio.csv')
print ("**************************************")
print ("*  TRANSFORMACION Y REPARACION DE DATOS  *")
print ("**************************************")
df = pd.read_csv(archivo, sep=';', encoding='utf-8-sig', low_memory=False)
print (f"Registros iniciales: {len(df)}")
print (f"Variables iniciales: {len(df.columns)}")

print ("\n**********************************************")
print ("*         1. VARIABLES DE FECHA Y HORA       *")
print ("**********************************************")
df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%d', errors='coerce')
#convierte la fecha a tipo fecha (de 2017 a 2023 no hay fecha exacta, quedan vacias)

meses = {'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
         'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}
df['Mes_Num'] = df['Mes'].map(meses)
#convierte el nombre del mes a numero, sirve para ordenar y para el modelo

dias = {'Lunes': 1, 'Martes': 2, 'Miércoles': 3, 'Jueves': 4, 'Viernes': 5, 'Sábado': 6, 'Domingo': 7}
df['Dia_Semana_Num'] = df['Dia_Semana'].map(dias)
#convierte el dia de la semana a numero (Lunes = 1 y Domingo = 7)

df['Fin_de_Semana'] = np.where(df['Dia_Semana_Num'] >= 6, 'SI', 'NO')
#si es sabado (6) o domingo (7) es fin de semana

df['Hora_Num'] = pd.to_numeric(df['Hora'].str[:2], errors='coerce')
#toma los 2 primeros caracteres de la hora ('07:30' -> 7, '07:00 A 07:59' -> 7)
#funciona para todos los años; si la hora es nd queda vacia

df['Dia'] = df['Fecha'].dt.day
#dia del mes (1 a 31), solo existe desde 2024 porque antes no hay fecha exacta

print ("Variables creadas: Mes_Num, Dia_Semana_Num, Fin_de_Semana, Hora_Num, Dia")

print ("\n**********************************************")
print ("*      2. ESTANDARIZACION DE TEXTOS          *")
print ("**********************************************")
columnas_texto = [
    'Parroquia',
    'Causa',
    'Tipo_Siniestro',
]

for columna in columnas_texto:
    df[columna] = (
        df[columna].astype(str)
        .str.strip()
        #quita espacios al inicio y al final
        .str.replace(r'\s+', ' ', regex=True)
        #ambia espacios dobles por uno solo (ej: 'IMPRUDENCIA  DEL PEATON')
        .str.title()
        #pone la primera letra de cada palabra en mayuscula
    )
    
    print (f"Columna estandarizada: {columna} ({df[columna].nunique()} categorias)")

print ("\n**********************************************")
print ("*      3. REPARACION DE CATEGORIAS           *")
print ("**********************************************")
antes = df['Tipo_Siniestro'].nunique()
df['Tipo_Siniestro'] = df['Tipo_Siniestro'].replace({
    'Caída De Pasajero': 'Caída De Pasajeros',
})
#la misma categoria venia escrita en singular y en plural, se unifica en una sola
print (f"Categorias de Tipo_Siniestro: antes {antes} -> despues {df['Tipo_Siniestro'].nunique()}")

print ("\n**********************************************")
print ("*      4. CLASIFICACION DE GRAVEDAD          *")
print ("**********************************************")
def clasificar_gravedad(fallecidos, lesionados):
    if fallecidos > 0:
        return 'Mortal'
    elif lesionados > 0:
        return 'Con lesionados'
    else:
        return 'Solo daños materiales'
#clasifica cada siniestro segun sus consecuencias

df['Gravedad'] = df.apply(lambda fila: clasificar_gravedad(fila['Fallecidos'], fila['Lesionados']), axis=1)
print (df['Gravedad'].value_counts())

df['Tiene_Coordenadas'] = np.where(df['Latitud'] == 'N/D', 'NO', 'SI')
#marca si el siniestro se puede ubicar en el mapa (SI) o no (NO)
print ("\nSiniestros con coordenadas:")
print (df['Tiene_Coordenadas'].value_counts())

print ("\n**********************************************")
print ("*      GUARDAR DATOS TRANSFORMADOS           *")
print ("**********************************************")
df.to_csv(
    'accidentes_transito_quito_transformado.csv',
    sep=';',
    encoding='utf-8-sig',
    index=False,
    date_format='%Y-%m-%d')
#guarda el resultado en un archivo nuevo, sin tocar el archivo limpio
print ("Archivo guardado: accidentes_transito_quito_transformado.csv")
print (f"Registros finales: {len(df)}")
print (f"Variables finales: {len(df.columns)}")