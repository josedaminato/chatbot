"""
Manejador de urgencias
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
    Maneja consultas de urgencia
    
    Args:
        phone_number: Número de teléfono
        message: Mensaje del usuario
        entities: Entidades extraídas
        
    Returns:
        Respuesta sobre urgencias
    """
    clinic_info = get_clinic_name_and_email()
    
    return (
        f"🚨 Información de Urgencias - {clinic_info['clinic_name']}:\n\n"
        f"Para casos de URGENCIA MÉDICA:\n"
        f"📞 Llama al 911 o acude al hospital más cercano\n\n"
        f"Para consultas urgentes en nuestra clínica:\n"
        f"📞 Teléfono: [Número de urgencias]\n"
        f"🕐 Horario de urgencias: 24/7\n\n"
        f"¿Tu consulta es realmente urgente o puede esperar al próximo turno disponible?"
    ) 