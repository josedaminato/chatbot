# Listas de palabras clave: saludos, urgencias, cancelación, etc. 

import re
import unicodedata

SALUDOS = [
    'hola', 'buenos días', 'buenas tardes', 'buenas noches', 'buen dia', 'buenas', 'saludos'
]

CANCEL_KEYWORDS = [
    'cancelar', 'anular', 'borrar'
]

CONFIRM_KEYWORDS = [
    'si', 'sí', 'confirmo'
]

URGENCY_KEYWORDS = [
    'urgente', 'urgencia', 'mucho dolor', 'me duele', 'me sangra', 'sangrado', 'no aguanto', 'no soporto', 'emergencia', 'dolor fuerte', 'no puedo más', 'no puedo mas'
]

PREGUNTAS_OBRA_SOCIAL = [
    'obra social', 'aceptan', 'atienden', 'prepaga', 'cobertura'
]

PREGUNTAS_COSTO = [
    'costo', 'cuánto sale', 'precio', 'valor', 'cuanto cuesta'
]

PREGUNTAS_UBICACION = [
    'dónde están', 'ubicación', 'dirección', 'cómo llego', 'donde queda'
]

PREGUNTAS_GRATIS = [
    'es gratis', 'sin costo', 'no cobran', 'no tiene costo', 'gratuito'
]

def normalize_text(text):
    """Normaliza el texto a minúsculas, sin tildes y espacios simples.

    Args:
        text (str): Texto a normalizar.

    Returns:
        str: Texto normalizado.
    """
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def match_keywords(text, keywords):
    """Busca coincidencias exactas de palabras clave en el texto normalizado.

    Args:
        text (str): Texto a analizar.
        keywords (list): Lista de palabras/frases clave.

    Returns:
        bool: True si hay coincidencia, False si no.
    """
    norm_text = normalize_text(text)
    for kw in keywords:
        norm_kw = normalize_text(kw)
        # Coincidencia exacta de palabra o frase, usando regex de palabra completa
        pattern = r'\b' + re.escape(norm_kw) + r'\b'
        if re.search(pattern, norm_text):
            return True
    return False 