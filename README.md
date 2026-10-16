# Análisis Predictivo de Accidentes de Tránsito en Quito

Proyecto de **Ciencia y Análisis de Datos** del Instituto Superior Tecnológico Quito (ITQ) para la identificación de zonas de mayor riesgo.

**Integrantes:** Maximiliano Parra, Jonathan Larraga, Ariel Pilliza
**Docente:** Eldis Gabriel Nicolalde Navarrete

Se analizan **44.982 siniestros de tránsito** del cantón Quito, de enero de 2017 a agosto de 2026 (2026 es parcial), construidos únicamente con datos oficiales: INEC (2017–2023), Agencia Nacional de Tránsito (2024–2026), GeoQuito (límites de parroquias), REMMAQ y Open-Meteo (clima).

## Dashboard

```bash
pip install -r requirements.txt
streamlit run 12_dashboard.py
```

Se abre en `http://localhost:8501`. Tiene siete secciones: resumen, mapa de riesgo, cuándo ocurren, causas y perfil, grupos de riesgo (clustering), simulador de escenarios y datos.

## Estructura

| Archivo | Qué hace |
|---|---|
| `accidentes_transito_quito_2017_2026.csv` | Base original (44.982 registros, 32 variables) |
| `01_limpieza_datos.py` | Limpieza y validaciones → `accidentes_transito_quito_limpio.csv` |
| `transformacion.py` | Variables derivadas → `accidentes_transito_quito_transformado.csv` |
| `cruces_clima_parroquia_quito_2024_2026.csv` | Parroquia y clima de cada siniestro con coordenadas |
| `03_estadistica_descriptiva.py` | Estadística descriptiva |
| `05_accidentes_por_destino.py` | Análisis por parroquia |
| `06_perfil_de_siniestros.py` | Causas, vehículos, sexo, edad y zona |
| `07_estacionalidad_de_siniestros.py` | Patrones por mes, trimestre y temporada |
| `08_correlaciones.py` | Correlación de Pearson por parroquia |
| `09_preparacion_clustering.py` · `10_clustering.py` | K-Means de parroquias (K = 3) |
| `11_mapa_siniestros.py` | Mapas con folium |
| `12_dashboard.py` | Dashboard en Streamlit |
| `parroquias_dmq.geojson` | Límites oficiales de las 65 parroquias (GeoQuito) |
| `resultados/` | Gráficos, tablas y mapas generados por los scripts |
| `diapositivas/` | Presentaciones del proyecto |
| `Proyecto final - Siniestros de transito Quito (APA).docx` | Informe escrito en normas APA |

Los scripts se ejecutan en orden desde la carpeta del proyecto. Los mapas de folium deben abrirse con un servidor local (`python -m http.server 8000`) para que cargue el mapa base.

## Principales hallazgos

- Los siniestros bajaron de 8.810 (2017) a 3.987 (2025), pero la letalidad pasó de 31 a 85 fallecidos por cada 1.000 siniestros.
- Dos horas pico (07:00 y 19:00); el fin de semana concentra el 34,5 % de los siniestros.
- En la zona rural un siniestro es 2,3 veces más mortal; Pifo registra 44,9 fallecidos por cada 100 siniestros.
- El comportamiento del conductor explica el 85,5 % de los siniestros; la lluvia no aumenta su gravedad.
