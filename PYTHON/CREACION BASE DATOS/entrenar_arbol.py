from influxdb import InfluxDBClient
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

# === CONEXIÓN A INFLUXDB ===
client = InfluxDBClient(host='localhost', port=8086, database='homeassistant')
query = 'SELECT * FROM control_calefaccion'
result = client.query(query)
points = list(result.get_points())

# === CONVERTIR A DATAFRAME ===
df = pd.DataFrame(points)
df['time'] = pd.to_datetime(df['time'])
df['hora'] = df['time'].dt.hour
df['dia_semana'] = df['time'].dt.weekday

# === VARIABLES DE ENTRADA Y SALIDA ===
features = ['temperatura', 'humedad', 'hora', 'dia_semana']
X = df[features]
y = df['led_estado']  # 1: ON, 0: OFF

# === DIVIDIR Y ENTRENAR ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = DecisionTreeClassifier(max_depth=5, random_state=0)
modelo.fit(X_train, y_train)

# === EVALUACIÓN ===
y_pred = modelo.predict(X_test)
print(classification_report(y_test, y_pred))

# === GUARDAR MODELO ===
with open('modelo_calefaccion.pkl', 'wb') as f:
    pickle.dump(modelo, f)

print("Modelo entrenado y guardado como modelo_calefaccion.pkl")