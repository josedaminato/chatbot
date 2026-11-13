"""
Servicio de email para envío de notificaciones
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT

logger = logging.getLogger('asistente_salud')

def send_email_notification(to_email: str, subject: str, body: str):
    """
    Envía email de notificación simple
    
    Args:
        to_email: Email del destinatario
        subject: Asunto del email
        body: Cuerpo del mensaje
    """
    try:
        # Verificar configuración de email
        if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT]):
            logger.error("Configuración de email incompleta")
            return False
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = str(EMAIL_USER)
        msg['To'] = str(to_email)
        msg['Subject'] = str(subject)
        
        # Agregar cuerpo
        msg.attach(MIMEText(body, 'plain'))
        
        # Enviar email
        server = smtplib.SMTP(str(EMAIL_HOST), int(str(EMAIL_PORT)))
        server.starttls()
        server.login(str(EMAIL_USER), str(EMAIL_PASSWORD))
        text = msg.as_string()
        server.sendmail(str(EMAIL_USER), str(to_email), text)
        server.quit()
        
        logger.info(f"Email de notificación enviado exitosamente a {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email de notificación: {str(e)}")
        return False

def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str = None):
    """
    Envía email con archivo adjunto
    
    Args:
        to_email: Email del destinatario
        subject: Asunto del email
        body: Cuerpo del mensaje
        attachment_path: Ruta del archivo adjunto
    """
    try:
        # Verificar configuración de email
        if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT]):
            logger.error("Configuración de email incompleta")
            return False
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = str(EMAIL_USER)
        msg['To'] = str(to_email)
        msg['Subject'] = str(subject)
        
        # Agregar cuerpo
        msg.attach(MIMEText(body, 'plain'))
        
        # Agregar archivo adjunto si existe
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEText(attachment.read().decode('utf-8'), _subtype="octet-stream")
                part.add_header('Content-Disposition', 'attachment', filename=attachment_path.split('/')[-1])
                msg.attach(part)
        
        # Enviar email
        server = smtplib.SMTP(str(EMAIL_HOST), int(str(EMAIL_PORT)))
        server.starttls()
        server.login(str(EMAIL_USER), str(EMAIL_PASSWORD))
        text = msg.as_string()
        server.sendmail(str(EMAIL_USER), str(to_email), text)
        server.quit()
        
        logger.info(f"Email enviado exitosamente a {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email: {str(e)}")
        return False 