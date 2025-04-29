
from flask import Flask, render_template, redirect, request
import paho.mqtt.publish as publish
from influxdb import InfluxDBClient
from datetime import datetime
import pytz
import requests

app = Flask(__name__)

MQTT_BROKER = "192.168.0.101"
MQTT_TOPIC = "cmnd/home/heater/POWER"
INFLUX_DB = "homeassistant"

API_KEY = "TU_API_KEY"
CIUDAD = "Madrid"
UNIDADES = "metric"

client = InfluxDBClient(host="localhost", port=8086)
client.switch_database(INFLUX_DB)

@app.route('/')
def index():
    result = client.query('SELECT * FROM control_calefaccion ORDER BY time DESC LIMIT 1')
    punto = list(result.get_points())[0]
    temperatura = punto["temperatura"]
    humedad = punto["humedad"]
    corriente = punto["corriente"]
    hora = datetime.fromisoformat(punto["time"].replace("Z", "+00:00")).astimezone(pytz.timezone("Europe/Madrid"))
    return render_template("index.html",
                           temperatura=temperatura,
                           humedad=humedad,
                           corriente=corriente,
                           estado="ON" if corriente > 0.1 else "OFF",
                           hora=hora.strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/encender', methods=["POST"])
def encender():
    publish.single(MQTT_TOPIC, "ON", hostname=MQTT_BROKER)
    return redirect('/')

@app.route('/apagar', methods=["POST"])
def apagar():
    publish.single(MQTT_TOPIC, "OFF", hostname=MQTT_BROKER)
    return redirect('/')

@app.route('/graficas')
def graficas():
    return render_template("graficas.html")

@app.route('/meteorologia')
def meteo():
    
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/retrievebulkdataset?&key=F2JACZFX6KBXZBHFQ4DYFQYUF&taskId=9cd11369bd0eebb4ae5b33301353dafa&zip=false&unitGroup=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        datos_meteorologia = response.json()
        print(datos_meteorologia['days'][0]['tempmax'])
        dias = datos_meteorologia.get('days', [])[:15]
        ubicacion = datos_meteorologia.get('resolvedAddress', 'Ubicación desconocida')

        return render_template("meteorologia.html", datos=dias, ubicacion=ubicacion)  # Solo 7 días
    else:
        return "Error al obtener los datos meteorológicos"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

