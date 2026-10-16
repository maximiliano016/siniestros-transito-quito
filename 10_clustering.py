import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# 1. Cargar dataset estandarizado para clustering
archivo = "resultados/datos_clustering_estandarizados.csv"
df = pd.read_csv(archivo, sep=";", encoding="utf-8-sig", index_col=0)
#index_col=0 usa la primera columna (el nombre de la parroquia) como nombre de cada fila,
#asi el algoritmo solo recibe numeros pero no se pierde a que parroquia corresponde cada uno

originales = pd.read_csv("resultados/datos_clustering_originales.csv", sep=";", encoding="utf-8-sig", index_col=0)
#los mismos datos sin estandarizar: sirven al final para describir cada grupo con numeros reales

print("==============================================")
print("  MODELO DE CLUSTERING - SINIESTROS DE TRANSITO QUITO")
print("==============================================")
print(f"Parroquias : {len(df)}")
print(f"Variables : {len(df.columns)}")
print("Variables analizadas:")
for columna in df.columns:
    print("-", columna)

x = df.copy()

# 2. Evaluación de K (Inercia y Silhouette de 2 a 6 clusters)
#K-Means necesita que se le diga cuantos grupos (K) formar. Como no se sabe de antemano,
#se prueba con 2, 3, 4, 5 y 6 grupos y se mide que tan bien queda cada opcion
resultados = []
for k in range(2, 7):
    modelo = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )
    etiquetas = modelo.fit_predict(x)
    silhouette = silhouette_score(x, etiquetas)
    inercia = modelo.inertia_
    resultados.append([k, inercia, silhouette])
#inercia: que tan juntas estan las parroquias dentro de cada grupo (mientras mas baja, mejor)
#silhouette: que tan bien separados estan los grupos entre si, de -1 a 1 (mientras mas alto, mejor)
#random_state=42 hace que el resultado sea siempre el mismo cada vez que se corre

evaluacion = pd.DataFrame(
    resultados,
    columns=["n_clusters", "inercia", "silhouette"]
).round(3)
print("\nEvaluación de K:")
print(evaluacion)
evaluacion.to_csv("resultados/evaluacion_kmeans.csv", sep=";", index=False)

# 3. Selección del K óptimo (según mayor coeficiente de silhouette)
k_optimo = int(
    evaluacion.loc[evaluacion["silhouette"].idxmax(), "n_clusters"]
)
print(f"\nK óptimo seleccionado según Coeficiente Silhouette: {k_optimo}")

# 4. Ajuste del modelo K-Means final
kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(x)
originales["cluster"] = df["cluster"]
#cada parroquia recibe el numero del grupo al que pertenece (0, 1, 2...)

# 5. Estadísticas y porcentajes de los clusters
porcentaje_clusters = (
    df["cluster"]
    .value_counts(normalize=True)
    .sort_index() * 100
)
print("\nPorcentaje de parroquias por cluster:")
print(porcentaje_clusters.round(2))

perfil_clusters = originales.groupby("cluster").mean().round(2)
perfil_clusters.insert(0, "parroquias", originales["cluster"].value_counts().sort_index())
#perfil: el promedio de cada variable en cada grupo, con los numeros reales (no estandarizados),
#para poder leerlo: cuantos siniestros, que letalidad, etc. tiene en promedio cada grupo

print("\n==============================================")
print("PERFIL DE LOS CLUSTERS (valores reales)")
print("==============================================")
print(perfil_clusters.to_string())
#to_string muestra todas las columnas (si no, pandas esconde las del medio con '...')

print("\n==============================================")
print("PARROQUIAS DE CADA CLUSTER")
print("==============================================")
for cluster in sorted(df["cluster"].unique()):
    nombres = df[df["cluster"] == cluster].index.tolist()
    print(f"\nCluster {cluster} ({len(nombres)} parroquias):")
    print(", ".join(nombres))

perfil_clusters.to_csv("resultados/perfil_clusters.csv", sep=";", encoding="utf-8-sig")
originales.round(2).to_csv("resultados/dataset_clustering.csv", sep=";", encoding="utf-8-sig")
#dataset_clustering.csv: cada parroquia con sus variables reales y el cluster al que pertenece

# 6. Gráficos de Evaluación (Inercia / Codo y Silhouette)
plt.figure(figsize=(9, 6))
plt.plot(
    evaluacion["n_clusters"],
    evaluacion["inercia"],
    marker="o",
    color="#1565C0",
    linewidth=2
)
plt.title("Método del Codo (Inercia vs K) - Siniestros Quito", fontweight='bold')
plt.xlabel("Número de Clusters (K)")
plt.ylabel("Inercia")
plt.xticks(evaluacion["n_clusters"])
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("resultados/26_inercia_vs_k.png", dpi=300)
plt.close()
#metodo del codo: se busca el punto donde la linea deja de bajar rapido y se "dobla"

plt.figure(figsize=(9, 6))
plt.plot(
    evaluacion["n_clusters"],
    evaluacion["silhouette"],
    marker="o",
    color="#1565C0",
    linewidth=2
)
plt.title("Coeficiente Silhouette según Número de Clusters", fontweight='bold')
plt.xlabel("Número de Clusters (K)")
plt.ylabel("Silhouette Score")
plt.xticks(evaluacion["n_clusters"])
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("resultados/27_silueta_vs_k.png", dpi=300)
plt.close()

# 7. Reducción de dimensionalidad con PCA (2 componentes) para visualización
#cada parroquia tiene 8 variables y no se pueden dibujar 8 ejes.
#PCA las resume en 2 (pca1 y pca2) para poder ver los grupos en un grafico
pca = PCA(n_components=2, random_state=42)
x_pca = pca.fit_transform(x)
pca_df = pd.DataFrame(x_pca, columns=["pca1", "pca2"], index=df.index)
pca_df["cluster"] = df["cluster"].values
varianza = pca.explained_variance_ratio_.sum() * 100
print(f"\nLos 2 componentes del PCA conservan el {varianza:.1f} % de la información original")

colores = ["#1565C0", "#E53935", "#F9A825", "#2E7D32", "#6A1B9A", "#00838F"]
plt.figure(figsize=(10, 6))
for cluster in sorted(pca_df["cluster"].unique()):
    datos = pca_df[pca_df["cluster"] == cluster]
    plt.scatter(
        datos["pca1"],
        datos["pca2"],
        label=f"Cluster {cluster} ({len(datos)} parroquias)",
        color=colores[cluster],
        alpha=0.8,
        edgecolors='black',
        s=60
    )
    if len(datos) <= 8:
        for parroquia, fila in datos.iterrows():
            plt.annotate(parroquia.title(), (fila["pca1"], fila["pca2"]),
                         xytext=(6, 4), textcoords="offset points", fontsize=8)
#en los grupos pequeños se escribe el nombre de cada parroquia junto a su punto

plt.title("Clusters de parroquias según su siniestralidad (PCA)", fontweight='bold')
plt.margins(x=0.1)
#deja un poco de espacio a los lados para que no se corten los nombres
plt.xlabel("Componente Principal 1 (PCA 1)")
plt.ylabel("Componente Principal 2 (PCA 2)")
plt.grid(True, alpha=0.3, linestyle="--")
plt.legend()
plt.tight_layout()
plt.savefig("resultados/28_pca_clusters.png", dpi=300)
plt.close()

# 8. Cálculo de Centroides y Exportación
centroides = pd.DataFrame(
    kmeans.cluster_centers_,
    columns=x.columns
)
centroides.index.name = "cluster"
centroides = centroides.round(2)
#centroide: el "centro" de cada grupo, en valores estandarizados.
#positivo = el grupo esta sobre el promedio en esa variable; negativo = por debajo

print("\n==============================================")
print("CENTROIDES FINALES DE LOS CLUSTERS")
print("==============================================")
print(centroides.to_string())
centroides.to_csv("resultados/centroides.csv", sep=";", encoding="utf-8-sig")

print("\n==============================================")
print("CLUSTERING DE SINIESTROS FINALIZADO EXITOSAMENTE")
print("==============================================")
print("Archivos CSV generados en la carpeta 'resultados':")
print(" - evaluacion_kmeans.csv")
print(" - perfil_clusters.csv")
print(" - dataset_clustering.csv")
print(" - centroides.csv")
print("\nGráficos PNG generados:")
print(" - 26_inercia_vs_k.png")
print(" - 27_silueta_vs_k.png")
print(" - 28_pca_clusters.png")
