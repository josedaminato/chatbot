"""
Manejador de saludos y bienvenida
"""

from app.config import CLINIC_NAME

def get_clinic_name_and_email():
    """Obtiene nombre de la clínica y email del profesional"""
    return {
        'clinic_name': CLINIC_NAME,
        'professional_email': 'profesional@clinica.com'  # Valor por defecto
    }

def handle(phone_number: str, message: str, entities: dict) -> str:
    """
    Maneja saludos y mensajes de bienvenida
    
    Args:
        phone_number: Número de teléfono
        message: Mensaje del usuario
        entities: Entidades extraídas
        
    Returns:
        Respuesta de bienvenida
    """
    clinic_info = get_clinic_name_and_email()
    
    return (
        f"¡Hola! 👋\n\n"
        f"Bienvenido a {clinic_info['clinic_name']}.\n\n"
        f"¿En qué puedo ayudarte?\n\n"
        f"• 📅 Agendar un turno\n"
        f"• ❌ Cancelar o reprogramar\n"
        f"• ❓ Consultas generales\n"
        f"• 📸 Enviar una imagen\n\n"
        f"Escribe tu consulta y te ayudo 😊"
    ) 