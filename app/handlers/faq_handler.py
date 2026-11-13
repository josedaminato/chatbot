"""
Manejador de preguntas frecuentes
"""

from app.config import CLINIC_NAME


def get_clinic_name_and_email():
    """Obtiene nombre de la clínica y email del profesional"""
    return {
        "clinic_name": CLINIC_NAME,
        "professional_email": "profesional@clinica.com",  # Valor por defecto
    }


def handle(phone_number: str, message: str, entities: dict) -> str:
    """
    Maneja preguntas frecuentes

    Args:
        phone_number: Número de teléfono
        message: Mensaje del usuario
        entities: Entidades extraídas

    Returns:
        Respuesta con información frecuente
    """
    clinic_info = get_clinic_name_and_email()

    return (
        f"📋 Información de {clinic_info['clinic_name']}:\n\n"
        f"🕐 Horarios de atención:\n"
        f"   Lunes a Viernes: 9:00 - 18:00\n"
        f"   Sábados: 9:00 - 13:00\n\n"
        f"📍 Ubicación: [Dirección de la clínica]\n\n"
        f"📞 Teléfono: [Número de contacto]\n\n"
        f"💳 Formas de pago:\n"
        f"   • Efectivo\n"
        f"   • Tarjeta de crédito/débito\n"
        f"   • Transferencia bancaria\n\n"
        f"¿Necesitas agendar un turno o tienes otra consulta?"
    )
