from twilio.twiml.messaging_response import MessagingResponse
from app.services.ai_service import classify_intent, extract_appointment_details, generate_contextual_response
from app.db.queries import get_last_appointment, get_conversation_state, update_conversation_state, clear_conversation_state
import logging

def handle_with_ai(phone_number, incoming_msg):
    """Procesa mensajes usando IA para clasificar intenciones y delegar a handlers específicos.
    
    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.
        
    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    
    try:
        # 1. Obtener contexto actual
        context = get_conversation_state(phone_number) or {}
        # 2. Usar IA para extraer intención y entidades
        ai_result = classify_intent(incoming_msg)
        intent = ai_result.get('intent', 'unknown')
        entities = ai_result.get('entities', {})
        # 3. Actualizar contexto con nuevos datos extraídos
        for key in ['fecha', 'hora', 'nombre', 'profesional', 'especialidad']:
            if entities.get(key):
                context[key] = entities[key]
        context['last_intent'] = intent
        # 4. Guardar el contexto actualizado
        update_conversation_state(phone_number, **context)
        # 5. Lógica de flujo conversacional
        if intent == "appointment_request" or context.get('last_intent') == "appointment_request":
            if not context.get('fecha'):
                msg.body("¿Para qué fecha deseas el turno?")
                return resp
            if not context.get('hora'):
                msg.body(f"¿A qué hora el {context['fecha']}?")
                return resp
            if not context.get('nombre'):
                msg.body("¿A nombre de quién reservo el turno?")
                return resp
            # Si ya están todos los datos, reservar el turno (ejemplo simplificado)
            # Aquí deberías llamar a la función que inserta el turno en la base de datos
            clear_conversation_state(phone_number)
            msg.body(f"¡Listo! Turno reservado para {context['nombre']} el {context['fecha']} a las {context['hora']}.")
            return resp
        elif intent == "appointment_cancellation":
            from app.handlers.cancellation_handler import handle as cancel_handle
            return cancel_handle(phone_number, incoming_msg)
        elif intent == "appointment_confirmation":
            from app.handlers.confirmation_handler import handle as confirm_handle
            return confirm_handle(phone_number, incoming_msg)
        elif intent == "urgency":
            from app.handlers.urgency_handler import handle as urgency_handle
            return urgency_handle(phone_number, incoming_msg)
        elif intent == "question_cost":
            from app.handlers.faq_handler import handle as faq_handle
            return faq_handle('costo', phone_number, incoming_msg)
        elif intent == "question_insurance":
            from app.handlers.faq_handler import handle as faq_handle
            return faq_handle('obra_social', phone_number, incoming_msg)
        elif intent == "question_location":
            from app.handlers.faq_handler import handle as faq_handle
            return faq_handle('ubicacion', phone_number, incoming_msg)
        elif intent == "feedback":
            # Procesar feedback (ya implementado en webhook.py)
            from app.db.queries import insert_feedback
            if context.get('patient_name'):
                insert_feedback(context['patient_name'], phone_number, incoming_msg)
                msg.body("¡Gracias por tu mensaje! Tu opinión es muy valiosa para nosotros.")
                return resp
            else:
                msg.body("Gracias por contactarnos. ¿En qué puedo ayudarte?")
                return resp
        else:
            # Generar respuesta contextual con IA
            ai_response = generate_contextual_response(intent, entities, context)
            msg.body(ai_response)
            return resp
            
    except Exception as e:
        logging.error(f"Error in AI handler: {e}")
        # Fallback al handler por defecto
        from app.handlers.default_handler import handle as default_handle
        return default_handle(phone_number, incoming_msg) 