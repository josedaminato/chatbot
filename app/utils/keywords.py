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