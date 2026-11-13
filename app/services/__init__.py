# Servicios de negocio

from .agenda_service import AgendaService
from .notification_service import NotificationService, notification_service
from .ai_service import AIService
from .whatsapp_service import send_whatsapp_message
from .email_service import send_email_with_attachment
from .image_handler import save_image, get_clinic_name_and_email

# Instancias de servicios
agenda_service = AgendaService()
ai_service = AIService()

__all__ = [
    'AgendaService', 'agenda_service',
    'NotificationService', 'notification_service',
    'AIService', 'ai_service',
    'send_whatsapp_message',
    'send_email_with_attachment',
    'save_image', 'get_clinic_name_and_email'
]
