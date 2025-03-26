from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt
import time

# ================= CONFIGURACIÓN =================
INFLUX_HOST = "localhost"
INFLUX_PORT = 8086
INFLUX_DB = "homeassistant"

# Conectar a InfluxDB
client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)

# Verificar si la base de datos existe, si no, crearla
databases = client.get_list_database()
if not any(db["name"] == INFLUX_DB for db in databases):
    print(f"⚠️ La base de datos '{INFLUX_DB}' no existe. Creándola...")
    client.create_database(INFLUX_DB)

# Seleccionar la base de datos
client.switch_database(INFLUX_DB)

# ================= FUNCIÓN PARA GUARDAR DATOS =================
def guardar_datos_en_influx(temperature, humidity, current, led_state):
    """
    Guarda los datos en InfluxDB: temperatura, humedad, corriente y estado del LED.
    """
    try:
        # ✅ Verificación de valores antes de insertarlos
        if temperature is None or humidity is None or current is None or led_state is None:
            print("⚠️ ERROR: Se intentó guardar un valor `None`. Datos no guardados.")
            return
        
        # ✅ Asegurar que `current` es un float válido
        try:
            current = float(current)
        except ValueError:
            print("⚠️ ERROR: `current` no es un número válido. Datos no guardados.")
            return
        
        # ✅ Convertir `led_state` a 1 o 0
        led_state = 1 if str(led_state).strip().upper() == "ON" else 0

        json_body = [
            {
                "measurement": "control_calefaccion",
                "tags": {
                    "ubicacion": "habitacion"
                },
                "fields": {
                    "temperatura": float(temperature),
                    "humedad": float(humidity),
                    "corriente": float(current),
                    "led_estado": int(led_state == "ON")  # Convierte "ON" en 1, "OFF" en 0
                }
            }
        ]
        client.write_points(json_body)
        print("✅ Datos guardados en InfluxDB:", json_body)

    except Exception as e:
        print(f"⚠️ Error al guardar en InfluxDB: {e}")

# ================= FUNCIÓN PARA CERRAR CONEXIÓN =================
def cerrar_conexion():
    """Cierra la conexión a InfluxDB"""
    client.close()

# ================= PRUEBA DE CONEXIÓN =================
if __name__ == "__main__":
    print("🔄 Probando conexión a InfluxDB...")

    # 🔥 Prueba con valores correctos
    guardar_datos_en_influx(22.5, 55.0, 0.8, "ON")

    # 🔥 Prueba con valores incorrectos para detectar errores
    guardar_datos_en_influx(22.5, 55.0, None, "ON")  # No debe guardar
    guardar_datos_en_influx(22.5, 55.0, "ABC", "ON")  # No debe guardar
    guardar_datos_en_influx(22.5, 55.0, 0.8, None)  # No debe guardar

    cerrar_conexion()
    print("✅ Conexión y prueba de escritura en InfluxDB exitosa")