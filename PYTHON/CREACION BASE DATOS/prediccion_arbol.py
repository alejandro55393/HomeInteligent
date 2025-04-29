import time
import joblib
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from influxdb import InfluxDBClient
from datetime import datetime
import pytz

# ========== CONFIGURACIÓN ==========

MQTT_BROKER = "192.168.0.104"
MQTT_PORT = 1883
TOPIC_DATOS = "/home/data"
TOPIC_CONTROL = "cmnd/home/heater/POWER"

INFLUX_HOST = "localhost"
INFLUX_PORT = 8086
INFLUX_DB = "homeassistant"

modelo = joblib.load("modelo_calefaccion.pkl")
client_influx = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
client_influx.switch_database(INFLUX_DB)

# Timestamp del último procesamiento
ultimo_procesamiento = 0

print("✅ Sistema listo. Escuchando datos...")

# ========== CALLBACK MQTT ==========

def on_message(client, userdata, msg):

    global ultimo_procesamiento
    
    ahora = time.time()
    if ahora - ultimo_procesamiento < 40:  # Esperar 40 segundos entre mensajes
        return
    ultimo_procesamiento = ahora

    try:
        datos = msg.payload.decode().strip().split(',')
        if len(datos) < 4:
            print("❌ Formato incorrecto:", datos)
            return
        
        temperatura = float(datos[0].replace(',', '.'))
        humedad = float(datos[1].replace(',', '.'))
        corriente = float(datos[2].replace(',', '.'))
        timestamp_str = datos[3]
        hora_local = datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S").astimezone(pytz.timezone("Europe/Madrid"))

        hora = hora_local.hour + hora_local.minute / 60
        dia_semana = hora_local.weekday()

        # Guardar en InfluxDB como datos brutos
        json_data = [
            {
                "measurement": "control_calefaccion",
                "time": hora_local.isoformat(),
                "fields": {
                    "temperatura": temperatura,
                    "humedad": humedad,
                    "corriente": corriente
                }
            }
        ]
        client_influx.write_points(json_data)

        # Predicción
        X = [[temperatura, humedad, hora, dia_semana]]
        prediccion = modelo.predict(X)[0]
        estado = "ON" if prediccion == 1 else "OFF"

         # ❄️ NO ENCENDER entre las 00:00 y las 07:15
        if 0 <= hora < 7.25:
            print("🌙 Es horario nocturno (00:00-07:15), forzando calefacción a OFF")
            estado = "OFF"


        # Enviar comando al enchufe
        publish.single(TOPIC_CONTROL, estado, hostname=MQTT_BROKER, port=MQTT_PORT)

        if estado == "OFF":
            corriente = 0.0
        # Mostrar en consola
        print(f"📊 {hora_local.strftime('%Y-%m-%d %H:%M:%S')} -> "
              f"Temp={temperatura}°C, Hum={humedad}%, Corriente={corriente}A, "
              f"Hora={hora:.2f}, Día={dia_semana} => Calefacción: {estado}")

        # Guardar en InfluxDB
        json_body = [
            {
                "measurement": "predicciones_calefaccion",
                "tags": {
                    "modelo": "arbol_decision"
                },
                "time": hora_local.isoformat(),
                "fields": {
                    "temperatura": float(temperatura),
                    "humedad": float(humedad),
                    "corriente": float(corriente),
                    "hora": float(hora),
                    "dia_semana": int(dia_semana),
                    "prediccion": int(prediccion),
                    "estado": 1 if estado == "ON" else 0
                }
            }
        ]
        client_influx.write_points(json_body)

    except Exception as e:
        print(f"❌ Error al procesar mensaje: {e}")

# ========== SUSCRIPCIÓN MQTT ==========

client = mqtt.Client()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(TOPIC_DATOS)
client.loop_forever()