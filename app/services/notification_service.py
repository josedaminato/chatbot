"""
Servicio de notificaciones para email, WhatsApp y recordatorios
Centraliza toda la lógica de envío de mensajes
"""

import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.config import (
    SMTP_USER, SMTP_PASS, SMTP_SERVER, SMTP_PORT,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER,
    DIALOG_API_KEY, DIALOG_PHONE_NUMBER, WHATSAPP_PROVIDER,
    CLINIC_NAME, PROFESSIONAL_EMAIL
)
from app.schemas.notification_schema import NotificacionCreate, RecordatorioSchema
from app.db.queries import (
    create_notification, update_notification_status,
    get_pending_notifications, get_notifications_by_phone
)

logger = logging.getLogger('asistente_salud')

class NotificationService:
    """Servicio para gestión de notificaciones"""
    
    def __init__(self):
        self.clinic_name = CLINIC_NAME
        self.professional_email = PROFESSIONAL_EMAIL
        self.whatsapp_provider = WHATSAPP_PROVIDER.lower()
    
    def send_whatsapp(self, phone_number: str, message: str, priority: str = "normal") -> Dict[str, Any]:
        """
        Envía mensaje por WhatsApp
        
        Args:
            phone_number: Número de teléfono
            message: Mensaje a enviar
            priority: Prioridad del mensaje
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Registrar notificación en BD
            notification_id = create_notification(
                phone_number=phone_number,
                message=message,
                notification_type="whatsapp",
                priority=priority
            )
            
            # Enviar según el proveedor configurado
            if self.whatsapp_provider == "twilio":
                result = self._send_via_twilio(phone_number, message)
            elif self.whatsapp_provider == "dialog":
                result = self._send_via_dialog(phone_number, message)
            else:
                result = {
                    'success': False,
                    'error': f'Proveedor no soportado: {self.whatsapp_provider}'
                }
            
            # Actualizar estado en BD
            status = "enviada" if result['success'] else "fallida"
            update_notification_status(notification_id, status, result.get('error'))
            
            if result['success']:
                logger.info(f"WhatsApp enviado exitosamente a {phone_number}")
            else:
                logger.error(f"Error enviando WhatsApp a {phone_number}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en send_whatsapp: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_email(self, to_email: str, subject: str, message: str, attachments: List[str] = None) -> Dict[str, Any]:
        """
        Envía email
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            message: Mensaje del email
            attachments: Lista de archivos adjuntos
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(message, 'plain'))
            
            # Agregar archivos adjuntos si existen
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filepath.split("/")[-1]}'
                        )
                        msg.attach(part)
                    except Exception as e:
                        logger.warning(f"No se pudo adjuntar {filepath}: {str(e)}")
            
            # Enviar email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            text = msg.as_string()
            server.sendmail(SMTP_USER, to_email, text)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return {
                'success': True,
                'message': 'Email enviado exitosamente'
            }
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_appointment_confirmation(self, phone_number: str, appointment_date: date, 
                                    appointment_time: str, patient_name: str = None) -> Dict[str, Any]:
        """
        Envía confirmación de turno
        
        Args:
            phone_number: Número de teléfono
            appointment_date: Fecha del turno
            appointment_time: Hora del turno
            patient_name: Nombre del paciente
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Crear mensaje de confirmación
            patient_text = f" {patient_name}" if patient_name else ""
            message = (
                f"✅ Tu turno está confirmado{patient_text}!\n\n"
                f"📅 Fecha: {appointment_date.strftime('%d/%m/%Y')}\n"
                f"🕐 Hora: {appointment_time}\n"
                f"🏥 {self.clinic_name}\n\n"
                f"Por favor, llega 10 minutos antes de tu horario.\n"
                f"Si necesitas cancelar o reprogramar, contáctanos."
            )
            
            return self.send_whatsapp(phone_number, message, priority="high")
            
        except Exception as e:
            logger.error(f"Error enviando confirmación de turno: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_appointment_reminder(self, phone_number: str, appointment_date: date, 
                                appointment_time: str, patient_name: str = None) -> Dict[str, Any]:
        """
        Envía recordatorio de turno
        
        Args:
            phone_number: Número de teléfono
            appointment_date: Fecha del turno
            appointment_time: Hora del turno
            patient_name: Nombre del paciente
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Crear mensaje de recordatorio
            patient_text = f" {patient_name}" if patient_name else ""
            message = (
                f"⏰ Recordatorio de turno{patient_text}!\n\n"
                f"📅 Mañana tienes turno:\n"
                f"🕐 {appointment_date.strftime('%d/%m/%Y')} a las {appointment_time}\n"
                f"🏥 {self.clinic_name}\n\n"
                f"Por favor, confirma tu asistencia respondiendo 'SÍ'."
            )
            
            return self.send_whatsapp(phone_number, message, priority="normal")
            
        except Exception as e:
            logger.error(f"Error enviando recordatorio de turno: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_absence_followup(self, phone_number: str, appointment_date: date, 
                             appointment_time: str, patient_name: str = None) -> Dict[str, Any]:
        """
        Envía seguimiento por ausencia
        
        Args:
            phone_number: Número de teléfono
            appointment_date: Fecha del turno
            appointment_time: Hora del turno
            patient_name: Nombre del paciente
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Crear mensaje de seguimiento
            patient_text = f" {patient_name}" if patient_name else ""
            message = (
                f"❓ No pudimos confirmar tu asistencia{patient_text}.\n\n"
                f"📅 Turno: {appointment_date.strftime('%d/%m/%Y')} a las {appointment_time}\n"
                f"🏥 {self.clinic_name}\n\n"
                f"¿Te gustaría reprogramar tu turno? "
                f"Responde con una nueva fecha y horario."
            )
            
            return self.send_whatsapp(phone_number, message, priority="normal")
            
        except Exception as e:
            logger.error(f"Error enviando seguimiento por ausencia: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_image_notification(self, phone_number: str, filename: str) -> Dict[str, Any]:
        """
        Envía notificación de imagen recibida
        
        Args:
            phone_number: Número de teléfono
            filename: Nombre del archivo
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Enviar confirmación al paciente
            patient_message = (
                f"📸 Imagen recibida!\n\n"
                f"Gracias por enviar la imagen. "
                f"Un profesional la revisará y te contactará pronto.\n\n"
                f"🏥 {self.clinic_name}"
            )
            
            # Enviar notificación al profesional
            professional_message = (
                f"📸 Nueva imagen recibida\n\n"
                f"📱 Teléfono: {phone_number}\n"
                f"📁 Archivo: {filename}\n\n"
                f"La imagen está guardada en el servidor."
            )
            
            # Enviar mensajes
            patient_result = self.send_whatsapp(phone_number, patient_message)
            email_result = self.send_email(
                to_email=self.professional_email,
                subject="Nueva imagen recibida",
                message=professional_message
            )
            
            return {
                'success': patient_result['success'] and email_result['success'],
                'patient_message': patient_result,
                'email_notification': email_result
            }
            
        except Exception as e:
            logger.error(f"Error enviando notificación de imagen: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_via_twilio(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Envía mensaje via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=message,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=f"whatsapp:{phone_number}"
            )
            
            return {
                'success': True,
                'message_id': message.sid
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_via_dialog(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Envía mensaje via 360Dialog"""
        try:
            import requests
            
            url = "https://waba-v2.360dialog.io/messages"
            headers = {
                "D360-API-KEY": DIALOG_API_KEY,
                "Content-Type": "application/json"
            }
            
            data = {
                "recipient_type": "individual",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response.json().get('messages', [{}])[0].get('id')
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """Obtiene notificaciones pendientes"""
        try:
            notifications = get_pending_notifications()
            return notifications
        except Exception as e:
            logger.error(f"Error obteniendo notificaciones pendientes: {str(e)}")
            return []
    
    def retry_failed_notifications(self) -> Dict[str, Any]:
        """Reintenta notificaciones fallidas"""
        try:
            failed_notifications = get_pending_notifications()
            success_count = 0
            error_count = 0
            
            for notification in failed_notifications:
                if notification['notification_type'] == 'whatsapp':
                    result = self.send_whatsapp(
                        notification['phone_number'],
                        notification['message'],
                        notification.get('priority', 'normal')
                    )
                    
                    if result['success']:
                        success_count += 1
                    else:
                        error_count += 1
            
            return {
                'success': True,
                'retried': len(failed_notifications),
                'successful': success_count,
                'failed': error_count
            }
            
        except Exception as e:
            logger.error(f"Error reintentando notificaciones: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 