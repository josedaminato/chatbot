"""
Manejador de nombres de pacientes
"""

def is_valid_name(name: str) -> bool:
    """
    Valida si un nombre es válido
    
    Args:
        name: Nombre a validar
        
    Returns:
        True si es válido, False si no
    """
    if not name or len(name.strip()) < 2:
        return False
    return True

def handle(phone_number: str, message: str, entities: dict) -> str:
    """
    Maneja nombres de pacientes
    
    Args:
        phone_number: Número de teléfono
        message: Mensaje del usuario
        entities: Entidades extraídas
        
    Returns:
        Respuesta sobre el nombre
    """
    name = entities.get('nombre', '').strip()
    
    if not name:
        return "Por favor, dime tu nombre completo para continuar con el agendamiento."
    
    if not is_valid_name(name):
        return "El nombre debe tener al menos 2 caracteres. ¿Podrías escribirlo nuevamente?"
    
    return f"Perfecto {name}! Ahora dime qué fecha te gustaría para tu turno." 