#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <math.h>
#include <time.h>

// ================= Configuración de Sensores y Conexiones =================
#define DHTPIN 4           // Pin del DHT22
#define DHTTYPE DHT22      // Tipo de sensor DHT
#define LED_PIN 2          // Pin del LED indicador
#define ACS712_PIN 34     // Pin ADC de la ESP32 para la señal del SCT‑013


#define WIFI_SSID "sagemcomF240_EXT"
#define WIFI_PASSWORD "ZWYZEZYXYMZ5MW"
#define MQTT_SERVER "192.168.0.104"
#define MQTT_PORT 1883
#define MQTT_TOPIC "/home/data" // Tópico para publicar datos

// Umbral de temperatura para encender el LED (por ejemplo, si la temperatura es menor a 18.5°C)
#define TEMP_THRESHOLD 18.5

// Parámetros del ACS712 (5A)
#define VCC 5.0  // Voltaje de referencia de la ESP32
#define OFFSET 3.65  // Punto medio del sensor en reposo
#define SENSIBILIDAD 0.185  // Sensibilidad del ACS712 5A en V/A (185 mV/A)
#define NUM_MUESTRAS 500

// Instancias de objetos
DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

// ================= Funciones de Conexión =================
void setupWifi() {
  Serial.print("Conectando a ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println(" Conectado a MQTT");
    } else {
      Serial.print("Fallo, rc=");
      Serial.print(client.state());
      Serial.println(" Reintentando en 5 segundos...");
      delay(5000);
    }
  }
}

// ================= Función para Obtener Fecha y Hora =================
String getTimeString() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "Sin tiempo";
  }
  char timeStr[64];
  // Formato: día/mes/año hora:minuto:segundo
  strftime(timeStr, sizeof(timeStr), "%d/%m/%Y %H:%M:%S", &timeinfo);
  return String(timeStr);
}

// ================= Función para Leer la Corriente desde el ACS712 =================
float readCurrent() {
  float suma = 0;
  for (int i = 0; i < NUM_MUESTRAS; i++) {
      suma += analogRead(ACS712_PIN);
      delayMicroseconds(100);
  }
  float promedio = suma / NUM_MUESTRAS;
  float voltaje = (promedio / 4095.0) * VCC;  // Convertir ADC a voltaje

  // Calcular corriente en amperios
  float corriente = (voltaje - OFFSET) / SENSIBILIDAD;
  return fabs(corriente);
}


// ================= Setup =================
void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // Configurar el pin del LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Conectar a WiFi
  setupWifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);

  // Configurar NTP para obtener la hora (usa servidores públicos)
  configTime(3600, 0, "pool.ntp.org", "time.nist.gov");
  Serial.println("Esperando sincronización NTP...");
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Fallo al obtener el tiempo");
  } else {
    Serial.println("Tiempo sincronizado");
  }
}

// ================= Loop =================
void loop() {

  // Reconectar a MQTT si es necesario
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  // Obtener la fecha y hora actual
  String timeStamp = getTimeString();
  

  // Lectura del sensor DHT (temperatura y humedad)
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Error leyendo el DHT");
  } else {
    // Control del LED: se enciende si la temperatura es menor al umbral
    if (temperature < TEMP_THRESHOLD) {
      digitalWrite(LED_PIN, HIGH);
    } else {
      digitalWrite(LED_PIN, LOW);
    }
  }

  // Lectura de la corriente con el ACS712
  float current = readCurrent();
   // Mostrar valores en Serial Monitor
  Serial.print("Voltaje medido: ");
  Serial.print((current * SENSIBILIDAD) + OFFSET, 3);
  Serial.print(" V | Corriente: ");
  Serial.print(current, 3);
  Serial.println(" A");
  // Construir el mensaje con todos los datos
  String message = "Fecha/Hora: " + timeStamp;
  message += ", Temp: " + String(temperature, 1) + "°C";
  message += ", Hum: " + String(humidity, 1) + "%";
  message += ", Corriente: " + String(current, 4) + " A";
  message += ", LED: " + String((temperature < TEMP_THRESHOLD) ? "ON" : "OFF");

  // Mostrar el mensaje en el Serial Monitor
  Serial.println(message);

  // Publicar el mensaje en el broker MQTT
  client.publish(MQTT_TOPIC, message.c_str());

  // Esperar 10 segundos antes de la siguiente lectura
  delay(10000);
}