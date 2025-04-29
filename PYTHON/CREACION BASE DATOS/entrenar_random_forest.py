from influxdb import InfluxDBClient
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from datetime import datetime



#  CONEXIÓN A INFLUXDB 
client = InfluxDBClient(host='localhost', port=8086, database='homeassistant')
query = 'SELECT * FROM control_calefaccion'
result = client.query(query)
points = list(result.get_points())

# CONVERTIR A DATAFRAME 
df = pd.DataFrame(points)

# Verificar contenido del DataFrame
print("DataFrame cargado desde InfluxDB:")
print(df.head())
print("\nColumnas disponibles:", df.columns.tolist())

# 3. Procesar columna 'time'
if not df.empty and 'time' in df.columns:
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df['hora'] = df['time'].dt.hour
    df['dia_semana'] = df['time'].dt.weekday
    df=df.dropna(subset=['temperatura', 'humedad', 'hora', 'dia_semana', 'led_estado'])  # Eliminar filas con NaT en 'hora' o 'dia_semana'
else:
    print("ERROR: No hay datos o falta la columna 'time'. Verifica la consulta a InfluxDB.")
    exit()

# 4. Variables de entrada y salida
features = ['temperatura', 'humedad', 'hora', 'dia_semana']
X = df[features]
y = df['led_estado']  # 1: ON, 0: OFF

# 5. Dividir en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Crear y entrenar el modelo
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 7. Evaluar el modelo
y_pred = modelo.predict(X_test)
print("\nPrecisión en datos de prueba:", accuracy_score(y_test, y_pred))
print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred))

# 8. Guardar el modelo
fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
nombre_modelo = f'modelo_random_forest3_{fecha}.pkl'

joblib.dump(modelo, nombre_modelo)
print("\nModelo guardado como '{nombre_modelo}'")

# 9. Mostrar importancia de características
importancias = modelo.feature_importances_
caracteristicas = X.columns
print("\nImportancia de cada característica:")
for feature, importance in zip(caracteristicas, importancias):
    print(f"{feature}: {importance:.4f}")