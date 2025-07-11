"""
Helpers para procesamiento y análisis de mensajes
"""
import re
import unicodedata

def normalize_text(text):
    """Normaliza el texto a minúsculas, sin tildes y espacios simples."""
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def match_keywords(text, keywords):
    """Busca coincidencias exactas de palabras clave en el texto normalizado."""
    norm_text = normalize_text(text)
    for kw in keywords:
        norm_kw = normalize_text(kw)
        # Coincidencia exacta de palabra o frase, usando regex de palabra completa
        pattern = r'\b' + re.escape(norm_kw) + r'\b'
        if re.search(pattern, norm_text):
            return True
    return False 