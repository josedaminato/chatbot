"""
Manejador de imágenes
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
    Maneja envío de imágenes

    Args:
        phone_number: Número de teléfono
        message: Mensaje del usuario
        entities: Entidades extraídas

    Returns:
        Respuesta sobre envío de imágenes
    """
    clinic_info = get_clinic_name_and_email()

    return (
        f"📸 Envío de Imágenes - {clinic_info['clinic_name']}:\n\n"
        f"Puedes enviar imágenes de:\n"
        f"• 📋 Documentos médicos\n"
        f"• 🦷 Radiografías\n"
        f"• 📝 Recetas\n"
        f"• 🏥 Resultados de análisis\n\n"
        f"Simplemente adjunta la imagen en tu mensaje y la revisaremos.\n\n"
        f"¿Qué tipo de imagen necesitas enviar?"
    )
