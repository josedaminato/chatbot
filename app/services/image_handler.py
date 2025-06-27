# Funciones para guardar imágenes y notificar al profesional por email 
import os
import base64
import uuid
import requests
from datetime import datetime
from app.db.queries import get_last_appointment_id_by_phone, insert_attachment
from app.services.email_service import send_email_with_attachment
from app.utils.config import get_clinic_name_and_email
from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
import logging

UPLOADS_DIR = 'uploads'

# IMPORTANTE: En producción, protege la carpeta uploads/ con .htaccess (Apache) o reglas de nginx para evitar acceso público a archivos sensibles.
def ensure_uploads_dir():
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    if not os.access(UPLOADS_DIR, os.W_OK):
        raise PermissionError(f"No hay permisos de escritura en la carpeta {UPLOADS_DIR}")

def save_image_and_notify(phone_number, image_data=None, media_url=None):
    ensure_uploads_dir()
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    filename = f"patient_{phone_number}_{timestamp}_{unique_id}.jpg"
    file_path = os.path.join(UPLOADS_DIR, filename)
    # Guardar imagen
    try:
        if image_data:
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
        elif media_url:
            response = requests.get(media_url)
            with open(file_path, 'wb') as f:
                f.write(response.content)
        # Buscar turno asociado al paciente
        appointment_id = get_last_appointment_id_by_phone(phone_number)
        # Guardar referencia en base de datos
        insert_attachment(appointment_id, phone_number, filename, file_path)
        # Notificar al profesional
        clinic_name, professional_email = get_clinic_name_and_email()
        subject = f"Nueva imagen recibida de paciente en {clinic_name}"
        body = f"Un paciente ha enviado una imagen:\n\nTeléfono: {phone_number}\nArchivo: {filename}\n\nLa imagen está guardada en el servidor. Revisa el archivo adjunto."
        send_email_with_attachment(professional_email, subject, body, file_path)
        return True
    except Exception as e:
        logging.error(f"Error guardando imagen: {e}")
        return False 

def get_connection():
    return psycopg2.connect(
        dbname="asistente_salud",
        user="asistente_user",
        password="tu_password_segura",
        host="localhost"
    ) 