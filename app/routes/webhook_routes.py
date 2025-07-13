"""
Rutas de webhook para manejo de mensajes de WhatsApp
Integración con Twilio y procesamiento de mensajes
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from app.services import ai_service, agenda_service, notification_service
from app.utils.validators import is_valid_phone
from app.handlers import (
    greeting_handler, appointment_handler, cancellation_handler,
    confirmation_handler, faq_handler, image_handler, default_handler
)
from app.schemas.mensaje_entrada_schema import MensajeEntradaSchema

logger = logging.getLogger('asistente_salud')

# Crear blueprint para webhook
webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal para recibir mensajes de WhatsApp via Twilio
    """
    try:
        # Obtener datos del request
        data = request.form.to_dict()
        # Validar datos entrantes con Pydantic
        try:
            mensaje = MensajeEntradaSchema(**data)
        except Exception as e:
            logger.warning(f"Datos de webhook inválidos: {e}")
            return jsonify({'error': f'Datos inválidos: {e}'}), 400
        # Extraer información del mensaje
        phone_number = mensaje.From.replace('whatsapp:', '')
        message_body = mensaje.Body.strip()
        message_type = mensaje.MediaContentType0 or 'text'
        
        # Validar número de teléfono
        if not is_valid_phone(phone_number):
            logger.warning(f"Número de teléfono inválido: {phone_number}")
            return jsonify({'error': 'Invalid phone number'}), 400
        
        # Log del request
        logger.info(f"Webhook request - Phone: {phone_number}, Message: {message_body}")
        
        # Procesar según el tipo de mensaje
        if message_type.startswith('image/'):
            response = _handle_image_message(phone_number, data)
        else:
            response = _handle_text_message(phone_number, message_body)
        
        # Log de la respuesta
        logger.info(f"Webhook response - Phone: {phone_number}, Response: {response}")
        
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

def _handle_text_message(phone_number: str, message: str) -> str:
    """
    Maneja mensajes de texto usando IA y handlers
    
    Args:
        phone_number: Número de teléfono
        message: Mensaje del usuario
        
    Returns:
        Respuesta generada
    """
    try:
        # Analizar mensaje con IA
        analysis = ai_service.analyze_message(phone_number, message)
        intention = analysis.get('intention', 'unknown')
        entities = analysis.get('entities', {})
        confidence = analysis.get('confidence', 0.0)
        
        logger.info(f"Mensaje analizado - Intención: {intention}, Confianza: {confidence}")
        
        # Derivar a handler específico según la intención
        if intention == 'greeting':
            return greeting_handler.handle(phone_number, message, entities)
        
        elif intention == 'appointment_request':
            return appointment_handler.handle(phone_number, message, entities)
        
        elif intention == 'cancellation':
            return cancellation_handler.handle(phone_number, message, entities)
        
        elif intention == 'appointment_confirmation':
            return confirmation_handler.handle(phone_number, message, entities)
        
        elif intention == 'faq':
            return faq_handler.handle(phone_number, message, entities)
        
        elif intention == 'image_upload':
            return image_handler.handle(phone_number, message, entities)
        
        else:
            # Usar IA para generar respuesta contextual
            ai_response = ai_service.generate_response(phone_number, intention, entities)
            if ai_response and ai_response != "unknown":
                return ai_response
            else:
                return default_handler.handle(phone_number, message, entities)
                
    except Exception as e:
        logger.error(f"Error procesando mensaje de texto: {str(e)}", exc_info=True)
        return "Disculpa, hubo un error procesando tu mensaje. ¿Podrías intentar nuevamente?"

def _handle_image_message(phone_number: str, data: dict) -> str:
    """
    Maneja mensajes con imágenes
    
    Args:
        phone_number: Número de teléfono
        data: Datos del request de Twilio
        
    Returns:
        Respuesta generada
    """
    try:
        # Procesar imagen
        image_url = data.get('MediaUrl0')
        image_type = data.get('MediaContentType0')
        
        if not image_url:
            return "No se pudo procesar la imagen. ¿Podrías enviarla nuevamente?"
        
        # Guardar imagen y enviar notificación
        filename = image_handler.save_image(phone_number, image_url, image_type)
        
        if filename:
            # Enviar notificación al profesional
            notification_result = notification_service.send_image_notification(phone_number, filename)
            
            if notification_result['success']:
                return "📸 ¡Imagen recibida! Un profesional la revisará y te contactará pronto."
            else:
                return "📸 Imagen recibida. Gracias por enviarla."
        else:
            return "No se pudo guardar la imagen. ¿Podrías intentar nuevamente?"
            
    except Exception as e:
        logger.error(f"Error procesando imagen: {str(e)}", exc_info=True)
        return "Error procesando la imagen. ¿Podrías intentar nuevamente?"

@webhook_bp.route('/webhook/status', methods=['POST'])
def webhook_status():
    """
    Endpoint para recibir actualizaciones de estado de mensajes
    """
    try:
        data = request.form.to_dict()
        message_sid = data.get('MessageSid')
        message_status = data.get('MessageStatus')
        
        logger.info(f"Status update - SID: {message_sid}, Status: {message_status}")
        
        # Aquí podrías actualizar el estado en la base de datos
        # si necesitas tracking de delivery
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        logger.error(f"Error procesando status webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook_bp.route('/webhook/health', methods=['GET'])
def webhook_health():
    """
    Endpoint de health check para webhook
    """
    try:
        # Verificar servicios críticos
        services_status = {
            'ai_service': ai_service.api_key is not None,
            'agenda_service': True,  # No requiere configuración especial
            'notification_service': notification_service.whatsapp_provider is not None
        }
        
        all_healthy = all(services_status.values())
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'unhealthy',
            'services': services_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500 