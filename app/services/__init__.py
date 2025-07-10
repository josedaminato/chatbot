"""
Servicios del proyecto Asistente de Salud
Lógica de negocio centralizada y modular
"""

from .agenda_service import AgendaService
from .notification_service import NotificationService
from .ai_service import AIService

# Instancias singleton de los servicios
agenda_service = AgendaService()
notification_service = NotificationService()
ai_service = AIService()

__all__ = [
    'AgendaService',
    'NotificationService', 
    'AIService',
    'agenda_service',
    'notification_service',
    'ai_service'
] 