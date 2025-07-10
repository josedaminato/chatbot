"""
Configuración de logging profesional para el Asistente de Salud
Soporta formato JSON para escalabilidad en producción
"""

import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from app.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE, ERROR_LOG_FILE

class JSONFormatter(logging.Formatter):
    """Formateador personalizado para logs en formato JSON"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar campos adicionales si existen
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'phone_number'):
            log_entry['phone_number'] = record.phone_number
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
            
        return json.dumps(log_entry)

def setup_logging():
    """Configura el sistema de logging profesional"""
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Configurar logger raíz
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    if LOG_FORMAT.lower() == 'json':
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo de logs generales
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    
    # Handler para archivo de errores
    error_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    logger.addHandler(error_handler)
    
    # Logger específico para la aplicación
    app_logger = logging.getLogger('asistente_salud')
    app_logger.setLevel(logging.INFO)
    
    return app_logger

def log_with_context(logger, level, message, **context):
    """Log con contexto adicional (user_id, phone_number, etc.)"""
    
    extra = {}
    for key, value in context.items():
        if value is not None:
            extra[key] = value
    
    if level.upper() == 'INFO':
        logger.info(message, extra=extra)
    elif level.upper() == 'ERROR':
        logger.error(message, extra=extra)
    elif level.upper() == 'WARNING':
        logger.warning(message, extra=extra)
    elif level.upper() == 'DEBUG':
        logger.debug(message, extra=extra)

def log_webhook_request(logger, phone_number, message, response):
    """Log específico para requests de webhook"""
    log_with_context(
        logger, 'INFO',
        f"Webhook request processed - Phone: {phone_number}, Message: {message[:50]}..., Response: {response[:100]}...",
        phone_number=phone_number,
        message_length=len(message),
        response_length=len(response)
    )

def log_appointment_created(logger, phone_number, appointment_date, appointment_time):
    """Log específico para creación de turnos"""
    log_with_context(
        logger, 'INFO',
        f"Appointment created - Phone: {phone_number}, Date: {appointment_date}, Time: {appointment_time}",
        phone_number=phone_number,
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )

def log_error_with_context(logger, error, phone_number=None, user_id=None):
    """Log de errores con contexto"""
    log_with_context(
        logger, 'ERROR',
        f"Error occurred: {str(error)}",
        phone_number=phone_number,
        user_id=user_id,
        error_type=type(error).__name__
    ) 