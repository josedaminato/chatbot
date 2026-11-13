"""
Conexión a PostgreSQL
Configuración básica para desarrollo
"""

import logging
from typing import Optional

logger = logging.getLogger('asistente_salud')

# Para desarrollo, usamos la simulación en memoria
# En producción, aquí iría la conexión real a PostgreSQL

def get_connection():
    """Obtiene conexión a la base de datos"""
    # Por ahora retornamos None para usar la simulación en memoria
    return None

def close_connection(connection):
    """Cierra la conexión a la base de datos"""
    if connection:
        try:
            connection.close()
        except Exception as e:
            logger.error(f"Error cerrando conexión: {str(e)}")

def test_connection() -> bool:
    """Prueba la conexión a la base de datos"""
    try:
        # Por ahora siempre retorna True para desarrollo
        return True
    except Exception as e:
        logger.error(f"Error probando conexión: {str(e)}")
        return False
