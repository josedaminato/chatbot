"""
Funciones auxiliares para manejo de fechas y tiempos
"""
from datetime import datetime

DATE_FORMAT = "%d/%m/%Y"
def is_valid_date(date_str):
    """Valida que la fecha esté en formato DD/MM/YYYY."""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False 