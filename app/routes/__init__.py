"""
Rutas del proyecto Asistente de Salud
Endpoints para webhook, dashboard y API REST
"""

from .webhook_routes import webhook_bp
from .dashboard_routes import dashboard_bp
from .api_routes import api_bp

__all__ = [
    'webhook_bp',
    'dashboard_bp', 
    'api_bp'
]
