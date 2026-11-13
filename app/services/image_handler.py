"""
Manejo de imágenes enviadas por WhatsApp
Procesamiento y almacenamiento de imágenes
"""

import os
import requests
import logging
from datetime import datetime
from app.db.queries import get_last_appointment_id_by_phone, insert_attachment
from app.config import CLINIC_NAME
from .email_service import send_email_notification

logger = logging.getLogger('asistente_salud')

def save_image(phone_number: str, image_url: str, image_type: str) -> str:
    """
    Guarda una imagen desde URL
    
    Args:
        phone_number: Número de teléfono
        image_url: URL de la imagen
        image_type: Tipo de imagen
        
    Returns:
        Nombre del archivo guardado
    """
    try:
        # Crear directorio si no existe
        upload_dir = "uploads/images"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{phone_number}_{timestamp}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        # Descargar imagen
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Guardar archivo
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Guardar en base de datos
        attachment_data = {
            'phone_number': phone_number,
            'filename': filename,
            'filepath': filepath,
            'file_type': image_type,
            'appointment_id': get_last_appointment_id_by_phone(phone_number)
        }
        
        insert_attachment(attachment_data)
        
        logger.info(f"Imagen guardada: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error guardando imagen: {str(e)}")
        return ""

def save_image_and_notify(phone_number: str, image_data: str, media_url: str = None) -> bool:
    """
    Guarda una imagen y envía notificación por email
    
    Args:
        phone_number: Número de teléfono
        image_data: Datos de la imagen (base64 o URL)
        media_url: URL de la imagen (opcional)
        
    Returns:
        True si se guardó y notificó correctamente
    """
    try:
        # Guardar imagen
        image_url = media_url if media_url else image_data
        filename = save_image(phone_number, image_url, "image/jpeg")
        
        if filename and filename != "":
            # Obtener información de la clínica
            clinic_info = get_clinic_name_and_email()
            
            # Enviar notificación por email
            subject = f"Nueva imagen recibida - {clinic_info['clinic_name']}"
            body = f"""
            Se ha recibido una nueva imagen del paciente con número {phone_number}.
            
            Archivo: {filename}
            Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            
            Esta es una notificación automática del sistema de asistente virtual.
            """
            
            send_email_notification(clinic_info['professional_email'], subject, body)
            logger.info(f"Notificación enviada por imagen de {phone_number}")
            return True
        else:
            logger.error(f"No se pudo guardar la imagen de {phone_number}")
            return False
            
    except Exception as e:
        logger.error(f"Error en save_image_and_notify: {str(e)}")
        return False

def get_clinic_name_and_email():
    """Obtiene nombre de la clínica y email del profesional"""
    return {
        'clinic_name': CLINIC_NAME,
        'professional_email': 'profesional@clinica.com'  # Valor por defecto
    } 