"""
Aplicación principal del Asistente de Salud
Inicialización de Flask y registro de rutas
"""

from flask import Flask
import logging
from app.config import (
    SECRET_KEY, DEBUG, HOST, PORT, 
    validate_config, CLINIC_NAME
)
from app.logging_config import setup_logging
from app.routes import webhook_bp, dashboard_bp, api_bp
from app.utils.error_handler import ErrorHandler

def create_app():
    """
    Factory function para crear la aplicación Flask
    """
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configurar aplicación
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    
    # Configurar logging
    logger = setup_logging()
    
    # Validar configuración
    if not validate_config():
        logger.warning("⚠️  Configuración incompleta. Algunas funciones pueden no funcionar correctamente.")
    
    # Registrar manejador global de errores
    app.register_error_handler(Exception, ErrorHandler.handle_exception)
    
    # Registrar blueprints
    app.register_blueprint(webhook_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp)
    
    # Ruta de bienvenida
    @app.route('/')
    def welcome():
        return {
            'message': f'Bienvenido a {CLINIC_NAME}',
            'service': 'Asistente Virtual de Salud',
            'version': '2.0.0',
            'endpoints': {
                'webhook': '/webhook',
                'dashboard': '/dashboard',
                'api': '/api/v1'
            }
        }
    
    # Ruta de health check general
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'Asistente de Salud',
            'clinic_name': CLINIC_NAME,
            'timestamp': logging.time.time()
        }
    
    logger.info(f"🚀 Aplicación {CLINIC_NAME} inicializada correctamente")
    
    return app

def run_app():
    """
    Ejecutar la aplicación Flask
    """
    app = create_app()
    
    try:
        app.run(
            host=HOST,
            port=PORT,
            debug=DEBUG
        )
    except Exception as e:
        logging.error(f"Error ejecutando la aplicación: {str(e)}")
        raise

if __name__ == '__main__':
    run_app() 