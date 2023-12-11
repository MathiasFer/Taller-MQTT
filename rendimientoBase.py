import paho.mqtt.client as mqtt
import sqlite3
import smtplib
from email.mime.text import MIMEText

# Configuración MQTT
mqtt_broker = "broker.hivemq.com"
mqtt_topic = "rendimiento_M"

# Configuración SQLite
db_path = "rendimiento.db"

# Configuración de correo electrónico
email_sender = "tu_correo@gmail.com"
email_password = "tu_contraseña"

# Conexión a la base de datos SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla si no existe
#cursor.execute('''
#   CREATE TABLE  rendimiento (
#      id INTEGER PRIMARY KEY AUTOINCREMENT,
#     usuario TEXT,
#    rendimiento INTEGER
#    )
#''')
conn.commit()

# Función para manejar mensajes entrantes de MQTT
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    usuario, rendimiento = payload.split(',')
    
    # Almacenar en la base de datos
    cursor.execute("INSERT INTO rendimiento (usuario, rendimiento) VALUES (?, ?)", (usuario, rendimiento))
    conn.commit()
    
    # Verificar si el rendimiento es mayor al 40%
    if int(rendimiento) > 40:
        enviar_alerta(usuario, rendimiento)

# Función para enviar alerta por correo electrónico
def enviar_alerta(usuario, rendimiento):
    destinatario = f"{usuario}@dominio.com"
    mensaje = MIMEText(f"¡Alerta! El rendimiento de tu PC ({rendimiento}%) es mayor al 40%.")
    mensaje["Subject"] = "Alerta de rendimiento"
    mensaje["From"] = email_sender
    mensaje["To"] = destinatario
    
    # Conexión al servidor SMTP y envío del correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, destinatario, mensaje.as_string())

# Configuración del cliente MQTT
client = mqtt.Client()
client.on_message = on_message

# Conexión al broker MQTT
client.connect(mqtt_broker, 1883, 60)
client.subscribe(mqtt_topic, qos=1)

# Bucle principal de MQTT
client.loop_start()

# Mantener el programa en ejecución
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Programa detenido.")
    client.disconnect()
    conn.close()