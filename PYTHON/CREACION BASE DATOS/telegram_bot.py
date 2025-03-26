import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

# ================= CONFIGURACIÓN TELEGRAM =================
TOKEN = "8080806121:AAF9pPF52JB4SxP9T71YE2jwug5HCz58xec"  # Token de tu bot
CHAT_ID = "7248296961"  # Tu Chat ID real
DATA_FILE = "/home/alejandro/Documents/CursoRaspberrypiconPython/homeassistant/temperature_data.csv"
HORA_ENVIO = "22:00"  # Hora programada para enviar el informe

# ================= FUNCIONES =================
def enviar_mensaje(mensaje):
    """Envía un mensaje de texto a Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

def enviar_imagen(imagen_path):
    """Envía una imagen a Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    files = {"photo": open(imagen_path, "rb")}
    data = {"chat_id": CHAT_ID}
    requests.post(url, files=files, data=data)

def enviar_alerta(mensaje):
    """Envía una alerta a Telegram (para temperaturas bajas)."""
    enviar_mensaje(mensaje)

def generar_grafica():
    """Genera una gráfica de la temperatura y corriente del día y la guarda."""
    try:
        # Definir los nombres de las columnas esperadas
        columnas = ["timestamp", "temperatura", "humedad", "corriente", "estado"]
        df = pd.read_csv(DATA_FILE, names=columnas, delimiter=",", header=None, on_bad_lines="skip")
        df["timestamp"] = df["timestamp"].astype(str).str.strip()  # Elimina espacios en blanco
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d/%m/%Y %H:%M:%S", errors="coerce")

        hoy = datetime.now().date()
        df_hoy = df[df["timestamp"].dt.date == hoy]

        if df_hoy.empty:
            enviar_mensaje("📊 No hay datos registrados para hoy.")
            return None  
        
        df_hoy["hora"] = df_hoy["timestamp"].dt.strftime("%H:00")

        # Asegurar que temperatura y corriente son numéricas
        df_hoy["temperatura"] = pd.to_numeric(df_hoy["temperatura"], errors="coerce")
        df_hoy["corriente"] = pd.to_numeric(df_hoy["corriente"], errors="coerce")

        df_horas = df_hoy.groupby("hora")[["temperatura", "corriente"]].mean().reset_index()
        
        plt.figure(figsize=(10, 5))
        plt.plot(df_horas["hora"], df_horas["temperatura"], label="Temperatura (°C)", linestyle="-", marker="o")
        plt.plot(df_horas["hora"], df_horas["corriente"], label="Corriente (A)", linestyle="--", marker="s")
        plt.xlabel("Hora")
        plt.ylabel("Valores")
        plt.title(f"📊 Evolución de Temperatura y Corriente - {hoy.strftime('%d/%m/%Y')}")
        plt.legend()
        plt.xticks(rotation=45, fontsize=8)
        plt.grid(True)

        imagen_path = "/home/alejandro/temperature_plot.png"
        plt.savefig(imagen_path)
        plt.close()

        return imagen_path  

    except Exception as e:
        enviar_mensaje(f"⚠️ Error al generar la gráfica: {e}")
        return None

def enviar_resumen():
    """Genera el resumen diario con estadísticas y gráfica."""
    try:
        columnas = ["timestamp", "temperatura", "humedad", "corriente", "estado"]
        df = pd.read_csv(DATA_FILE, names=columnas, delimiter=",", header=None, on_bad_lines="skip")

        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d/%m/%Y %H:%M:%S", errors="coerce")

        hoy = datetime.now().date()
        df_hoy = df[df["timestamp"].dt.date == hoy]

        if df_hoy.empty:
            enviar_mensaje("📊 No hay datos registrados para hoy.")
            return

        temperatura_media = df_hoy["temperatura"].mean()
        temperatura_max = df_hoy["temperatura"].max()
        temperatura_min = df_hoy["temperatura"].min()
        corriente_media = df_hoy["corriente"].mean()

        mensaje = (f"📊 **Informe Diario de Consumo y Temperatura**\n"
                   f"📅 Fecha: {hoy}\n"
                   f"🌡️ Temperatura promedio: {temperatura_media:.1f}°C\n"
                   f"🔥 Temperatura máxima: {temperatura_max:.1f}°C\n"
                   f"❄️ Temperatura mínima: {temperatura_min:.1f}°C\n"
                   f"⚡ Corriente media consumida: {corriente_media:.2f}A")

        enviar_mensaje(mensaje)

        imagen_path = generar_grafica()
        if imagen_path:
            enviar_imagen(imagen_path)

    except Exception as e:
        enviar_mensaje(f"⚠️ Error al generar el informe: {e}")

def iniciar_envio_diario():
    """Bucle infinito para enviar el informe diario a la hora programada."""
    while True:
        hora_actual = datetime.now().strftime("%H:%M")
        if hora_actual == HORA_ENVIO:
            enviar_resumen()
            time.sleep(60)  
        time.sleep(30) 