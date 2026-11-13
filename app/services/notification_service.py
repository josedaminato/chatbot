"""
Servicio de notificaciones para email, WhatsApp y recordatorios
Centraliza toda la lógica de envío de mensajes
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from app.config import (
    CLINIC_NAME,
    EMAIL_HOST,
    EMAIL_PASSWORD,
    EMAIL_PORT,
    EMAIL_USER,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
)
from app.schemas.notification_schema import NotificacionCreate, RecordatorioSchema

logger = logging.getLogger("asistente_salud")


class NotificationService:
    """Servicio para gestión de notificaciones"""

    def __init__(self):
        self.clinic_name = CLINIC_NAME
        self.whatsapp_provider = "twilio"  # Proveedor por defecto

    def send_whatsapp(
        self, phone_number: str, message: str, priority: str = "normal"
    ) -> Dict[str, Any]:
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
            # Enviar según el proveedor configurado
            if self.whatsapp_provider == "twilio":
                result = self._send_via_twilio(phone_number, message)
            else:
                result = {
                    "success": False,
                    "error": f"Proveedor no soportado: {self.whatsapp_provider}",
                }

            if result["success"]:
                logger.info(f"WhatsApp enviado exitosamente a {phone_number}")
            else:
                logger.error(
                    f"Error enviando WhatsApp a {phone_number}: {result.get('error')}"
                )

            return result

        except Exception as e:
            logger.error(f"Error en send_whatsapp: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        attachments: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
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
            from email import encoders
            from email.mime.base import MIMEBase
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            # Verificar que las variables de email estén configuradas
            if not all([EMAIL_USER, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT]):
                return {"success": False, "error": "Configuración de email incompleta"}

            # Crear mensaje
            msg = MIMEMultipart()
            msg["From"] = EMAIL_USER
            msg["To"] = to_email
            msg["Subject"] = subject

            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(message, "plain"))

            # Agregar archivos adjuntos si existen
            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f'attachment; filename= {filepath.split("/")[-1]}',
                        )
                        msg.attach(part)
                    except Exception as e:
                        logger.warning(f"No se pudo adjuntar {filepath}: {str(e)}")

            # Enviar email
            server = smtplib.SMTP(EMAIL_HOST, int(EMAIL_PORT))
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, to_email, text)
            server.quit()

            logger.info(f"Email enviado exitosamente a {to_email}")
            return {"success": True, "message": "Email enviado exitosamente"}

        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_appointment_confirmation(
        self,
        phone_number: str,
        appointment_date: date,
        appointment_time: str,
        patient_name: str = None,
    ) -> Dict[str, Any]:
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
            return {"success": False, "error": str(e)}

    def send_appointment_reminder(
        self,
        phone_number: str,
        appointment_date: date,
        appointment_time: str,
        patient_name: str = None,
    ) -> Dict[str, Any]:
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
                f"📅 Fecha: {appointment_date.strftime('%d/%m/%Y')}\n"
                f"🕐 Hora: {appointment_time}\n"
                f"🏥 {self.clinic_name}\n\n"
                f"Te esperamos mañana. ¡No olvides tu cita!"
            )

            return self.send_whatsapp(phone_number, message, priority="high")

        except Exception as e:
            logger.error(f"Error enviando recordatorio de turno: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_absence_followup(
        self,
        phone_number: str,
        appointment_date: date,
        appointment_time: str,
        patient_name: str = None,
    ) -> Dict[str, Any]:
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
                f"Hola{patient_text}, notamos que no asististe a tu turno del "
                f"{appointment_date.strftime('%d/%m/%Y')} a las {appointment_time}.\n\n"
                f"¿Te gustaría reprogramar tu cita? Estamos aquí para ayudarte.\n"
                f"🏥 {self.clinic_name}"
            )

            return self.send_whatsapp(phone_number, message, priority="normal")

        except Exception as e:
            logger.error(f"Error enviando seguimiento por ausencia: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_image_notification(
        self, phone_number: str, filename: str
    ) -> Dict[str, Any]:
        """
        Envía notificación de imagen recibida

        Args:
            phone_number: Número de teléfono
            filename: Nombre del archivo de imagen

        Returns:
            Dict con el resultado del envío
        """
        try:
            message = (
                f"📸 ¡Imagen recibida!\n\n"
                f"Hemos recibido tu imagen: {filename}\n"
                f"Un profesional la revisará y te contactará pronto.\n\n"
                f"🏥 {self.clinic_name}"
            )

            return self.send_whatsapp(phone_number, message, priority="normal")

        except Exception as e:
            logger.error(f"Error enviando notificación de imagen: {str(e)}")
            return {"success": False, "error": str(e)}

    def _send_via_twilio(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Envía mensaje usando Twilio

        Args:
            phone_number: Número de teléfono
            message: Mensaje a enviar

        Returns:
            Dict con el resultado del envío
        """
        try:
            from twilio.rest import Client

            if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
                return {"success": False, "error": "Configuración de Twilio incompleta"}

            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=message, from_=TWILIO_PHONE_NUMBER, to=f"whatsapp:{phone_number}"
            )

            return {"success": True, "message_id": message.sid}

        except Exception as e:
            logger.error(f"Error enviando WhatsApp con Twilio: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """
        Obtiene notificaciones pendientes

        Returns:
            Lista de notificaciones pendientes
        """
        # Implementación simplificada - retorna lista vacía
        return []

    def retry_failed_notifications(self) -> Dict[str, Any]:
        """
        Reintenta notificaciones fallidas

        Returns:
            Dict con el resultado del reintento
        """
        # Implementación simplificada
        return {
            "success": True,
            "retried_count": 0,
            "message": "No hay notificaciones fallidas para reintentar",
        }


# Instancia global del servicio
notification_service = NotificationService()
