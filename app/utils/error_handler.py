"""
Middleware para manejo centralizado de errores
Captura errores comunes y responde con mensajes amigables
"""

import logging
import traceback
from functools import wraps
from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException
from app.logging_config import log_error_with_context

logger = logging.getLogger('asistente_salud')

class ErrorHandler:
    """Clase para manejo centralizado de errores"""
    
    @staticmethod
    def handle_exception(e):
        """
        Manejador global de excepciones
        
        Args:
            e: Excepción capturada
            
        Returns:
            Respuesta JSON con información del error
        """
        # Log del error con contexto
        log_error_with_context(
            logger, e,
            user_id=getattr(request, 'user_id', None),
            phone_number=getattr(request, 'phone_number', None),
            endpoint=request.endpoint,
            method=request.method,
            url=request.url
        )
        
        # Determinar tipo de error
        if isinstance(e, HTTPException):
            # Errores HTTP conocidos
            error_code = e.code
            error_message = e.description
        elif isinstance(e, ValueError):
            # Errores de validación
            error_code = 400
            error_message = f"Error de validación: {str(e)}"
        elif isinstance(e, KeyError):
            # Errores de clave faltante
            error_code = 400
            error_message = f"Campo requerido faltante: {str(e)}"
        elif isinstance(e, TypeError):
            # Errores de tipo
            error_code = 400
            error_message = f"Error de tipo de datos: {str(e)}"
        else:
            # Errores desconocidos
            error_code = 500
            error_message = "Error interno del servidor"
        
        # En desarrollo, incluir más detalles
        if current_app.config.get('DEBUG', False):
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()
            }
        else:
            error_details = {
                'error_type': type(e).__name__,
                'error_message': error_message
            }
        
        return jsonify({
            'success': False,
            'error': error_message,
            'error_code': error_code,
            'details': error_details
        }), error_code
    
    @staticmethod
    def handle_validation_error(e):
        """
        Manejador específico para errores de validación Pydantic
        
        Args:
            e: Error de validación
            
        Returns:
            Respuesta JSON con detalles de validación
        """
        errors = []
        for error in e.errors():
            field = '.'.join(str(loc) for loc in error['loc'])
            errors.append({
                'field': field,
                'message': error['msg'],
                'type': error['type']
            })
        
        log_error_with_context(
            logger, e,
            validation_errors=errors,
            endpoint=request.endpoint
        )
        
        return jsonify({
            'success': False,
            'error': 'Error de validación',
            'error_code': 422,
            'validation_errors': errors
        }), 422
    
    @staticmethod
    def handle_database_error(e):
        """
        Manejador específico para errores de base de datos
        
        Args:
            e: Error de base de datos
            
        Returns:
            Respuesta JSON con información del error
        """
        log_error_with_context(
            logger, e,
            error_type='database_error',
            endpoint=request.endpoint
        )
        
        # En producción, no exponer detalles de BD
        if current_app.config.get('DEBUG', False):
            error_message = f"Error de base de datos: {str(e)}"
        else:
            error_message = "Error de base de datos"
        
        return jsonify({
            'success': False,
            'error': error_message,
            'error_code': 500
        }), 500
    
    @staticmethod
    def handle_external_api_error(e):
        """
        Manejador específico para errores de APIs externas
        
        Args:
            e: Error de API externa
            
        Returns:
            Respuesta JSON con información del error
        """
        log_error_with_context(
            logger, e,
            error_type='external_api_error',
            endpoint=request.endpoint
        )
        
        return jsonify({
            'success': False,
            'error': 'Error de servicio externo',
            'error_code': 503
        }), 503

def error_handler(f):
    """
    Decorador para manejo de errores en funciones
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada con manejo de errores
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return ErrorHandler.handle_exception(e)
    return decorated_function

def validation_error_handler(f):
    """
    Decorador específico para errores de validación
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada con manejo de errores de validación
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return ErrorHandler.handle_validation_error(e)
        except Exception as e:
            return ErrorHandler.handle_exception(e)
    return decorated_function

def database_error_handler(f):
    """
    Decorador específico para errores de base de datos
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada con manejo de errores de BD
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Detectar errores de BD por el tipo de excepción
            if 'database' in str(e).lower() or 'sql' in str(e).lower():
                return ErrorHandler.handle_database_error(e)
            else:
                return ErrorHandler.handle_exception(e)
    return decorated_function

def api_error_handler(f):
    """
    Decorador específico para errores de APIs externas
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada con manejo de errores de API
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Detectar errores de API externa
            if any(keyword in str(e).lower() for keyword in ['api', 'http', 'request', 'timeout']):
                return ErrorHandler.handle_external_api_error(e)
            else:
                return ErrorHandler.handle_exception(e)
    return decorated_function

# Funciones de utilidad para logging de errores específicos
def log_webhook_error(error, phone_number=None, message=None):
    """Log específico para errores de webhook"""
    log_error_with_context(
        logger, error,
        error_type='webhook_error',
        phone_number=phone_number,
        message_length=len(message) if message else 0
    )

def log_dashboard_error(error, user_id=None, action=None):
    """Log específico para errores del dashboard"""
    log_error_with_context(
        logger, error,
        error_type='dashboard_error',
        user_id=user_id,
        action=action
    )

def log_api_error(error, endpoint=None, method=None):
    """Log específico para errores de API"""
    log_error_with_context(
        logger, error,
        error_type='api_error',
        endpoint=endpoint,
        method=method
    )

def log_service_error(error, service_name=None, operation=None):
    """Log específico para errores de servicios"""
    log_error_with_context(
        logger, error,
        error_type='service_error',
        service_name=service_name,
        operation=operation
    ) 