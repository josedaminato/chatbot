import openai
import logging
from app.utils.config import OPENAI_API_KEY

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

def classify_intent(message):
    """Clasifica la intención del mensaje usando OpenAI GPT-4.
    
    Args:
        message (str): Mensaje del usuario a clasificar.
        
    Returns:
        dict: Diccionario con la intención y metadatos adicionales.
    """
    try:
        system_prompt = """
        Eres un asistente médico que clasifica mensajes de pacientes. 
        Analiza el mensaje y responde con un JSON que contenga:
        
        {
            "intent": "categoría_principal",
            "confidence": 0.95,
            "entities": {
                "date": "fecha_extraída_si_hay",
                "time": "hora_extraída_si_hay",
                "urgency_level": "bajo/medio/alto",
                "patient_name": "nombre_si_se_menciona"
            },
            "action": "acción_recomendada"
        }
        
        Categorías de intención:
        - "greeting": Saludos iniciales
        - "appointment_request": Solicitud de turno
        - "appointment_cancellation": Cancelación de turno
        - "appointment_confirmation": Confirmación de turno
        - "urgency": Urgencias médicas
        - "question_cost": Preguntas sobre costos
        - "question_insurance": Preguntas sobre obra social
        - "question_location": Preguntas sobre ubicación
        - "feedback": Feedback post-consulta
        - "image_upload": Envío de imágenes
        - "unknown": No se puede clasificar
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Clasifica este mensaje: {message}"}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        # Parsear la respuesta JSON
        import json
        result = json.loads(response.choices[0].message.content)
        logging.info(f"AI classified message '{message}' as {result['intent']} with confidence {result['confidence']}")
        return result
        
    except Exception as e:
        logging.error(f"Error classifying intent with AI: {e}")
        # Fallback a clasificación básica
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "entities": {},
            "action": "default_response"
        }

def extract_appointment_details(message):
    """Extrae detalles específicos de turnos del mensaje usando IA.
    
    Args:
        message (str): Mensaje del usuario.
        
    Returns:
        dict: Detalles extraídos (fecha, hora, especialidad, etc.)
    """
    try:
        system_prompt = """
        Extrae información específica sobre turnos médicos del mensaje.
        Responde con JSON:
        
        {
            "date": "DD/MM/YYYY o null",
            "time": "HH:MM o null", 
            "specialty": "especialidad_mencionada o null",
            "urgency": "bajo/medio/alto",
            "patient_name": "nombre_completo o null"
        }
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extrae detalles de: {message}"}
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        logging.info(f"AI extracted details: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Error extracting details with AI: {e}")
        return {
            "date": None,
            "time": None,
            "specialty": None,
            "urgency": "bajo",
            "patient_name": None
        }

def generate_contextual_response(intent, entities, context=None):
    """Genera una respuesta contextual usando IA basada en la intención y entidades.
    
    Args:
        intent (str): Intención clasificada.
        entities (dict): Entidades extraídas.
        context (dict): Contexto adicional (historial, etc.)
        
    Returns:
        str: Respuesta generada.
    """
    try:
        system_prompt = """
        Eres un asistente médico amigable y profesional. 
        Genera respuestas naturales y útiles basadas en la intención del paciente.
        Mantén un tono cálido pero profesional.
        """
        
        user_prompt = f"""
        Intención: {intent}
        Entidades: {entities}
        Contexto: {context or 'N/A'}
        
        Genera una respuesta apropiada.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        result = response.choices[0].message.content.strip()
        logging.info(f"AI generated response: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Error generating response with AI: {e}")
        return "Disculpa, no pude procesar tu mensaje. ¿Podrías reformularlo?" 