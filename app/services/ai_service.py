"""
Servicio de IA para interpretación de mensajes y contexto conversacional
Integración con OpenAI GPT-4 para procesamiento de lenguaje natural
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.config import OPENAI_API_KEY
from app.db.queries import (
    get_conversation_state, update_conversation_state,
    create_conversation_state
)

logger = logging.getLogger('asistente_salud')

class AIService:
    """Servicio para procesamiento de IA y contexto conversacional"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.clinic_name = "Clínica Dental Cecilia Farreras"
        
    def analyze_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Analiza un mensaje usando IA para determinar la intención
        
        Args:
            phone_number: Número de teléfono del usuario
            message: Mensaje a analizar
            
        Returns:
            Dict con la interpretación del mensaje
        """
        try:
            # Obtener contexto de la conversación
            context = self._get_conversation_context(phone_number)
            
            # Crear prompt para OpenAI
            prompt = self._create_analysis_prompt(message, context)
            
            # Llamar a OpenAI
            response = self._call_openai(prompt)
            
            # Procesar respuesta
            analysis = self._parse_ai_response(response)
            
            # Actualizar contexto
            self._update_conversation_context(phone_number, message, analysis)
            
            logger.info(f"Mensaje analizado para {phone_number}: {analysis.get('intention', 'unknown')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando mensaje: {str(e)}")
            return {
                'intention': 'unknown',
                'confidence': 0.0,
                'entities': {},
                'response_type': 'fallback',
                'error': str(e)
            }
    
    def generate_response(self, phone_number: str, intention: str, 
                         entities: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Genera una respuesta basada en la intención y contexto
        
        Args:
            phone_number: Número de teléfono
            intention: Intención detectada
            entities: Entidades extraídas
            context: Contexto adicional
            
        Returns:
            Respuesta generada
        """
        try:
            # Obtener contexto de conversación
            conversation_context = self._get_conversation_context(phone_number)
            
            # Crear prompt para respuesta
            prompt = self._create_response_prompt(intention, entities, conversation_context, context)
            
            # Llamar a OpenAI
            response = self._call_openai(prompt)
            
            # Limpiar respuesta
            clean_response = self._clean_ai_response(response)
            
            logger.info(f"Respuesta generada para {phone_number}: {intention}")
            
            return clean_response
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return self._get_fallback_response(intention)
    
    def extract_entities(self, message: str) -> Dict[str, Any]:
        """
        Extrae entidades del mensaje (fechas, horas, nombres, etc.)
        
        Args:
            message: Mensaje a procesar
            
        Returns:
            Dict con entidades extraídas
        """
        try:
            prompt = f"""
            Extrae las siguientes entidades del mensaje: fecha, hora, nombre, urgencia, teléfono.
            Responde solo en formato JSON.
            
            Mensaje: "{message}"
            
            Formato esperado:
            {{
                "fecha": "YYYY-MM-DD o null",
                "hora": "HH:MM o null", 
                "nombre": "string o null",
                "urgencia": "alta/mediana/baja o null",
                "telefono": "string o null"
            }}
            """
            
            response = self._call_openai(prompt)
            entities = self._parse_json_response(response)
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extrayendo entidades: {str(e)}")
            return {}
    
    def _get_conversation_context(self, phone_number: str) -> Dict[str, Any]:
        """Obtiene el contexto de la conversación"""
        try:
            context = get_conversation_state(phone_number)
            return context if context else {}
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {str(e)}")
            return {}
    
    def _update_conversation_context(self, phone_number: str, message: str, analysis: Dict[str, Any]):
        """Actualiza el contexto de la conversación"""
        try:
            current_context = self._get_conversation_context(phone_number)
            
            # Actualizar contexto con nueva información
            updated_context = {
                'last_message': message,
                'last_intention': analysis.get('intention'),
                'last_entities': analysis.get('entities', {}),
                'last_timestamp': datetime.now().isoformat(),
                'conversation_step': current_context.get('conversation_step', 0) + 1
            }
            
            # Mantener información importante del contexto anterior
            if 'appointment_date' in current_context:
                updated_context['appointment_date'] = current_context['appointment_date']
            if 'appointment_time' in current_context:
                updated_context['appointment_time'] = current_context['appointment_time']
            if 'patient_name' in current_context:
                updated_context['patient_name'] = current_context['patient_name']
            
            # Actualizar entidades si se encontraron
            entities = analysis.get('entities', {})
            if entities.get('fecha'):
                updated_context['appointment_date'] = entities['fecha']
            if entities.get('hora'):
                updated_context['appointment_time'] = entities['hora']
            if entities.get('nombre'):
                updated_context['patient_name'] = entities['nombre']
            
            # Guardar en BD
            if current_context:
                update_conversation_state(phone_number, updated_context)
            else:
                create_conversation_state(phone_number, updated_context)
                
        except Exception as e:
            logger.error(f"Error actualizando contexto: {str(e)}")
    
    def _create_analysis_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Crea el prompt para análisis de mensaje"""
        
        context_info = ""
        if context:
            context_info = f"""
            Contexto de la conversación:
            - Última intención: {context.get('last_intention', 'none')}
            - Fecha del turno: {context.get('appointment_date', 'no especificada')}
            - Hora del turno: {context.get('appointment_time', 'no especificada')}
            - Nombre del paciente: {context.get('patient_name', 'no especificado')}
            - Paso de conversación: {context.get('conversation_step', 0)}
            """
        
        return f"""
        Eres un asistente virtual de {self.clinic_name}. Analiza el siguiente mensaje y determina la intención del usuario.
        
        {context_info}
        
        Mensaje del usuario: "{message}"
        
        Responde en formato JSON con:
        {{
            "intention": "greeting|appointment_request|appointment_confirmation|cancellation|reschedule|faq|image_upload|unknown",
            "confidence": 0.0-1.0,
            "entities": {{
                "fecha": "YYYY-MM-DD o null",
                "hora": "HH:MM o null",
                "nombre": "string o null",
                "urgencia": "alta/mediana/baja o null"
            }},
            "response_type": "greeting|ask_date|ask_time|ask_name|confirm_appointment|provide_info|fallback",
            "needs_more_info": true/false
        }}
        
        Intenciones posibles:
        - greeting: Saludos iniciales
        - appointment_request: Solicitud de turno
        - appointment_confirmation: Confirmación de turno existente
        - cancellation: Cancelación de turno
        - reschedule: Reprogramación de turno
        - faq: Preguntas frecuentes
        - image_upload: Envío de imagen
        - unknown: No reconocida
        """
    
    def _create_response_prompt(self, intention: str, entities: Dict[str, Any], 
                               conversation_context: Dict[str, Any], additional_context: Dict[str, Any] = None) -> str:
        """Crea el prompt para generar respuesta"""
        
        context_info = f"""
        Contexto de la conversación:
        - Intención: {intention}
        - Entidades: {entities}
        - Conversación anterior: {conversation_context}
        """
        
        if additional_context:
            context_info += f"\nContexto adicional: {additional_context}"
        
        return f"""
        Eres un asistente virtual amigable de {self.clinic_name}. 
        Genera una respuesta natural y útil basada en la intención del usuario.
        
        {context_info}
        
        Instrucciones:
        - Sé amigable y profesional
        - Usa emojis apropiados
        - Proporciona información clara
        - Si necesitas más información, pídela de forma natural
        - Mantén el contexto de la conversación
        
        Responde solo el mensaje, sin formato adicional.
        """
    
    def _call_openai(self, prompt: str) -> str:
        """Llama a la API de OpenAI"""
        try:
            import openai
            
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un asistente virtual de salud profesional y amigable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {str(e)}")
            raise
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parsea la respuesta de IA"""
        try:
            import json
            
            # Intentar parsear como JSON
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # Si no es JSON, crear respuesta básica
            return {
                'intention': 'unknown',
                'confidence': 0.5,
                'entities': {},
                'response_type': 'fallback',
                'raw_response': response
            }
            
        except Exception as e:
            logger.error(f"Error parseando respuesta de IA: {str(e)}")
            return {
                'intention': 'unknown',
                'confidence': 0.0,
                'entities': {},
                'response_type': 'fallback',
                'error': str(e)
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parsea respuesta JSON de IA"""
        try:
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            return {}
    
    def _clean_ai_response(self, response: str) -> str:
        """Limpia la respuesta de IA"""
        # Remover comillas si las tiene
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        # Remover saltos de línea extra
        response = response.replace('\n', ' ').strip()
        
        return response
    
    def _get_fallback_response(self, intention: str) -> str:
        """Obtiene respuesta de fallback"""
        fallback_responses = {
            'greeting': f"¡Hola! Soy el asistente virtual de {self.clinic_name}. ¿En qué puedo ayudarte?",
            'appointment_request': "Para agendar un turno, necesito algunos datos. ¿Qué fecha te gustaría?",
            'unknown': f"Disculpa, no entendí bien. ¿Podrías reformular tu mensaje? Estoy aquí para ayudarte con tu turno en {self.clinic_name}.",
            'faq': f"Para consultas específicas, te recomiendo contactar directamente con {self.clinic_name}.",
            'cancellation': "Para cancelar tu turno, necesito más información. ¿Podrías proporcionar tu número de teléfono?",
            'reschedule': "Para reprogramar tu turno, necesito algunos datos. ¿Cuál es tu número de teléfono?"
        }
        
        return fallback_responses.get(intention, fallback_responses['unknown'])
    
    def get_conversation_summary(self, phone_number: str) -> Dict[str, Any]:
        """Obtiene un resumen de la conversación"""
        try:
            context = self._get_conversation_context(phone_number)
            
            return {
                'phone_number': phone_number,
                'conversation_step': context.get('conversation_step', 0),
                'appointment_date': context.get('appointment_date'),
                'appointment_time': context.get('appointment_time'),
                'patient_name': context.get('patient_name'),
                'last_intention': context.get('last_intention'),
                'last_timestamp': context.get('last_timestamp')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de conversación: {str(e)}")
            return {}
    
    def clear_conversation_context(self, phone_number: str) -> bool:
        """Limpia el contexto de conversación"""
        try:
            update_conversation_state(phone_number, {})
            logger.info(f"Contexto de conversación limpiado para {phone_number}")
            return True
        except Exception as e:
            logger.error(f"Error limpiando contexto: {str(e)}")
            return False 