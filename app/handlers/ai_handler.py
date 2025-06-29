from twilio.twiml.messaging_response import MessagingResponse
from app.services.ai_service import classify_intent, extract_appointment_details, generate_contextual_response
from app.db.queries import get_last_appointment
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
        # Clasificar intención con IA
        ai_result = classify_intent(incoming_msg)
        intent = ai_result.get('intent', 'unknown')
        confidence = ai_result.get('confidence', 0.0)
        entities = ai_result.get('entities', {})
        
        logging.info(f"AI classified '{incoming_msg}' as {intent} (confidence: {confidence})")
        
        # Obtener contexto del paciente
        last_appointment = get_last_appointment(phone_number)
        context = {
            "has_recent_appointment": last_appointment is not None,
            "last_appointment_date": last_appointment[3] if last_appointment else None,
            "patient_name": last_appointment[1] if last_appointment else None
        }
        
        # Delegar según la intención
        if confidence > 0.7:  # Solo usar IA si la confianza es alta
            if intent == "greeting":
                from app.handlers.greeting_handler import handle as greeting_handle
                return greeting_handle(phone_number, incoming_msg)
                
            elif intent == "appointment_request":
                # Extraer detalles específicos del turno
                details = extract_appointment_details(incoming_msg)
                if details.get('date') and details.get('time'):
                    # Si ya tiene fecha y hora, pedir nombre
                    from app.handlers.patient_name_handler import handle as name_handle
                    return name_handle(phone_number, incoming_msg)
                elif details.get('date'):
                    # Si solo tiene fecha, pedir hora
                    from app.handlers.time_handler import handle as time_handle
                    return time_handle(phone_number, incoming_msg)
                else:
                    # Si no tiene fecha, pedir fecha
                    from app.handlers.appointment_handler import handle as appointment_handle
                    return appointment_handle(phone_number, incoming_msg)
                    
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
                
        else:
            # Si la confianza es baja, usar el handler por defecto
            from app.handlers.default_handler import handle as default_handle
            return default_handle(phone_number, incoming_msg)
            
    except Exception as e:
        logging.error(f"Error in AI handler: {e}")
        # Fallback al handler por defecto
        from app.handlers.default_handler import handle as default_handle
        return default_handle(phone_number, incoming_msg) 