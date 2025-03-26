import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import csv
from cliente import guardar_datos_en_influx  
from telegram_bot import enviar_alerta, iniciar_envio_diario  # Importar la función enviar_alerta

# ================= CONFIGURACIÓN =================
MQTT_BROKER = "192.168.0.104"
MQTT_PORT = 1883
MQTT_TOPIC_DATA = "/home/data"
MQTT_TOPIC_HEATER = "/home/heater"

DATA_FILE = "/home/alejandro/Documents/CursoRaspberrypiconPython/homeassistant/temperature_data.csv"

GPIO.setwarnings(False)
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

calefaccion_encendida = False
UMBRAL_ALERTA = 18.5 # Umbral de temperatura para encender la calefacción
alerta_enviada = False # Bandera para evitar enviar múltiples alertas

# ================= FUNCIÓN PARA PROCESAR MENSAJES MQTT =================
def on_message(client, userdata, message):
    global calefaccion_encendida, alerta_enviada

    try:
        # Decodificar el mensaje recibido
        data = message.payload.decode("utf-8").split(',')

        # Extraer los valores del mensaje
        timeStamp = data[0].split(": ")[1]
        temperature = float(data[1].split(": ")[1][:-2])
        humidity = float(data[2].split(": ")[1][:-1])
        current = float(data[3].split(": ")[1][:-2])
        led_state = data[4].split(": ")[1]

        # Mostrar los valores recibidos
        print(f"Tiempo: {timeStamp}, Temp: {temperature}°C, Hum: {humidity}%, Corriente: {current}A, LED: {led_state}")

        # Guardar en CSV
        with open(DATA_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timeStamp, temperature, humidity, current, led_state])
        
        print(f"✅ Datos guardados en CSV: {DATA_FILE}")

        # Guardar en InfluxDB
        guardar_datos_en_influx(temperature, humidity, current, led_state)

        # Control de la calefacción
        if temperature < 18.5 and not calefaccion_encendida:
            print("🔥 Encendiendo la calefacción...")
            GPIO.output(RELAY_PIN, GPIO.HIGH)  
            calefaccion_encendida = True
            client.publish(MQTT_TOPIC_HEATER, "ON")

        elif temperature >= 18.5 and calefaccion_encendida:
            print("❄️ Apagando la calefacción...")
            GPIO.output(RELAY_PIN, GPIO.LOW)
            calefaccion_encendida = False
            client.publish(MQTT_TOPIC_HEATER, "OFF")

  # **Enviar alerta SOLO UNA VEZ cuando la temperatura baja del umbral**
        if temperature < UMBRAL_ALERTA and not alerta_enviada:
            mensaje_alerta = f"⚠️ ¡Alerta! La temperatura ha bajado a {temperature}°C. Revisa la calefacción."
            enviar_alerta(mensaje_alerta)
            #print(f"📩 Resultado de la alerta: {respuesta}")
            alerta_enviada = True  # Marcar que la alerta ya fue enviada

        # **Resetear alerta cuando la temperatura vuelva a subir**
        if temperature >= UMBRAL_ALERTA and alerta_enviada:
            print("✅ La temperatura ha subido por encima del umbral. Se puede enviar una nueva alerta en el futuro.")
            alerta_enviada = False  # Resetear alerta para futuras bajadas de temperatura

    except Exception as e:
        print(f"⚠️ Error al procesar el mensaje: {e}")

# ================= CONFIGURACIÓN DEL CLIENTE MQTT =================
client = mqtt.Client()

client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC_DATA)
client.loop_start()

try:
    iniciar_envio_diario()  # Iniciar el envío diario de resúmenes
    while True:
        estado = "Encendida" if calefaccion_encendida else "Apagada"
        print(f"🔥 Estado calefacción: {estado}")
        time.sleep(10)

except KeyboardInterrupt:
    print("\n⏳ Cerrando programa...")

finally:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()
