# Evaluación Ambiental de la Recolección de Residuos Reciclables en Corrientes
#
# Renzo Nahuel Vallejos
#
#
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import folium
from folium.plugins import HeatMap
import numpy as np
from scipy.spatial.distance import pdist, squareform
from math import radians, sin, cos, sqrt, atan2

# Análisis de cantidad recolectada en contenedores Puntos Verdes

df_main = pd.read_csv('recoleccion_puntos_verdes.csv')

# Figura 1
df_main['fecha'] = pd.to_datetime(df_main['fecha'], format='%Y/%m/%d', errors='coerce')
fig1, ax1 = plt.subplots(figsize=(8, 6))
df_main.plot.line(x='fecha', y='kg_residuos_secos_reciclables', ax=ax1)
ax1.set_title('Evolución en el tiempo de la cantidad de material reciclable recolectado de Puntos Verdes', size=12)
ax1.set_xlabel('Tiempo')
ax1.set_ylabel('Material seco reciclable (kg)')
ax1.annotate('Festival del Chamamé 2019', xy=('17/01/2019', 301), rotation=90)
ax1.annotate('Festival del Chamamé 2020', xy=('30/12/2019', 461), rotation=90)
ax1.annotate('Corsos', xy=('15/02/2019', 62), rotation=90)
ax1.get_legend().set_visible(False)
date_format = mdates.DateFormatter('%d/%m/%Y')
ax1.xaxis.set_major_formatter(date_format)
ax1.xaxis.set_tick_params(rotation=45)

# Figura 2
fig2, ax2 = plt.subplots(figsize=(8, 6))
df_puntosverdes = df_main[['punto_verde', 'kg_residuos_secos_reciclables']]
df_puntosverdes.groupby(['punto_verde']).sum().plot.pie(y='kg_residuos_secos_reciclables', autopct='%1.0f%%', ax=ax2, labels='')
ax2.set_title('Cantidad de material reciclable por Punto Verde')
ax2.set_xlabel(None)
ax2.set_ylabel(None)
ax2.legend(loc='upper right', bbox_to_anchor=(1.23, 1)) 


# Distribución geográfica
df_geo_puntosverdes = pd.read_csv('puntos_verdes_geo.csv')

m = folium.Map(location=[-27.5, -58.8], zoom_start=12.5)

for index, row in df_geo_puntosverdes.iterrows():
    folium.Marker(
        location=[row['lat'], row['lng']],
        popup=row['ubicacion']).add_to(m)
    
m.save("mapa_puntos_verdes.html")

# Densidad de Puntos Verdes (heatmap)
m_heatmap = folium.Map(location=[-27.5, -58.8], zoom_start=12.5)

heat_data = [[row['lat'], row['lng']] for index, row in df_geo_puntosverdes.iterrows()]
HeatMap(heat_data, radius=100).add_to(m_heatmap)

m_heatmap.save("densidad_puntos_verdes.html")

# Cálculo de distancias entre Puntos Verdes
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Fórmula Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c
    return distance
coordinates = df_geo_puntosverdes[['lat', 'lng']].values
distancias = squareform(pdist(coordinates, lambda u, v: haversine(u[0], u[1], v[0], v[1])))

# Distancia promedio entre Puntos Verdes
total_distance = np.sum(distancias)  
n = len(df_geo_puntosverdes)
average_distance = total_distance / (n * (n - 1) / 2)
print(f'Distancia promedio entre Puntos Verdes: {average_distance:.2f} Km.')

# Total Kg. de material reciclable recolectado
total_material = df_main['kg_residuos_secos_reciclables'].sum()
df_main['fecha'] = pd.to_datetime(df_main['fecha'], errors='coerce')
df_main.dropna(subset=['fecha'], inplace=True)
min_date = df_main['fecha'].min()
max_date = df_main['fecha'].max()
date_range = max_date - min_date
print(' \n Recolección desde Puntos Verdes')
print('Total de material reciclable recolectado:', total_material)
print('Desde:', min_date)
print('Hasta:', max_date)
print('Rango:', date_range)

# Análisis de recolección por zona via ruleros o a puerta
df_ruleros = pd.read_csv('recoleccion_puntos_verdes_ruleros.csv')

# Limpieza de fechas
df_ruleros['fecha'] = pd.to_datetime(df_ruleros['fecha'], format='%Y/%m/%d', errors='coerce')
df_ruleros.dropna(subset=['fecha'], inplace=True)

# Figura 3
fig1, ax1 = plt.subplots(figsize=(8, 6))
df_ruleros.plot.line(x='fecha', y='kg_residuos_secos_reciclables', ax=ax1)
ax1.set_title('Evolución de cantidad de material reciclable recolectado \n por el programa Reciclando Juntos', size=13)
ax1.set_xlabel('Tiempo')
ax1.set_ylabel('Residuos secos reciclables (kg)')
ax1.get_legend().set_visible(False)
ax1.tick_params(axis='x', labelsize=8)
date_format = mdates.DateFormatter('%d/%m/%Y')
ax1.xaxis.set_major_formatter(date_format)
plt.xticks(rotation=45)
# Top 5 fechas con más recolecciones
top5_dates = df_ruleros.nlargest(5, 'kg_residuos_secos_reciclables')
ax1.scatter(top5_dates['fecha'], top5_dates['kg_residuos_secos_reciclables'], color='red')
print('\n Fechas y Zonas con mayor recolección: \n % s' % top5_dates)

# Figura 4
fig2, ax2 = plt.subplots(figsize=(8, 6))
df_zonas = df_ruleros[['zona', 'kg_residuos_secos_reciclables']]
# Filtración de zonas con menor porcentaje
df_filtro_zonas = df_zonas[df_zonas['zona'] != 'Delegacion San Gerónimo']
df_filtro_zonas.groupby(['zona']).sum().plot.pie(y='kg_residuos_secos_reciclables', autopct='%1.0f%%', ax=ax2, fontsize=8.4)
ax2.set_title('Cantidad de material reciclable recolectado por zona', size=12)
ax2.set_xlabel(None)
ax2.set_ylabel(None)
ax2.legend(loc='lower left', bbox_to_anchor=(-.27, 0)) 

plt.show()

# Total Kg. de material reciclable recolectado
total_material = df_ruleros['kg_residuos_secos_reciclables'].sum()
df_ruleros['fecha'] = pd.to_datetime(df_ruleros['fecha'], errors='coerce')
df_ruleros.dropna(subset=['fecha'], inplace=True)
min_date = df_ruleros['fecha'].min()
max_date = df_ruleros['fecha'].max()
date_range = max_date - min_date
print(' \n Recolección del programa Reciclando Juntos')
print('Total de material reciclable recolectado:', total_material)
print('Desde:', min_date)
print('Hasta:', max_date)
print('Rango:', date_range)

