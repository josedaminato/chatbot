"""
Tests para los servicios principales
Validación de funcionalidad básica
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import date, time
from app.services import agenda_service, notification_service, ai_service
from app.schemas import TurnoCreate, EstadoTurno

class TestAgendaService(unittest.TestCase):
    """Tests para el servicio de agenda"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.agenda_service = agenda_service
    
    @patch('app.services.agenda_service.get_appointments_by_date')
    def test_get_available_slots(self, mock_get_appointments):
        """Test para obtener horarios disponibles"""
        # Mock de turnos existentes
        mock_get_appointments.return_value = [
            {'appointment_time': time(9, 0)},
            {'appointment_time': time(14, 30)}
        ]
        
        # Test
        available_slots = self.agenda_service.get_available_slots(date(2024, 1, 15))
        
        # Verificar que se excluyen los horarios ocupados
        self.assertNotIn('09:00', available_slots)
        self.assertNotIn('14:30', available_slots)
        self.assertIn('10:00', available_slots)
        self.assertIn('15:00', available_slots)
    
    @patch('app.services.agenda_service.create_appointment')
    def test_create_appointment_success(self, mock_create):
        """Test para crear turno exitosamente"""
        # Mock de creación exitosa
        mock_create.return_value = 1
        
        # Datos de test
        turno_data = TurnoCreate(
            phone_number="+5491112345678",
            appointment_date=date(2024, 1, 15),
            appointment_time=time(14, 30),
            patient_name="Juan Pérez"
        )
        
        # Test
        result = self.agenda_service.create_appointment(turno_data)
        
        # Verificar resultado
        self.assertTrue(result['success'])
        self.assertIn('Turno confirmado', result['message'])
        self.assertEqual(result['appointment_id'], 1)
    
    @patch('app.services.agenda_service.get_appointment')
    def test_get_appointment_not_found(self, mock_get):
        """Test para obtener turno inexistente"""
        # Mock de turno no encontrado
        mock_get.return_value = None
        
        # Test
        result = self.agenda_service.get_appointment(999)
        
        # Verificar resultado
        self.assertIsNone(result)

class TestNotificationService(unittest.TestCase):
    """Tests para el servicio de notificaciones"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.notification_service = notification_service
    
    @patch('app.services.notification_service._send_via_twilio')
    def test_send_whatsapp_success(self, mock_send):
        """Test para envío exitoso de WhatsApp"""
        # Mock de envío exitoso
        mock_send.return_value = {'success': True, 'message_id': 'test_123'}
        
        # Test
        result = self.notification_service.send_whatsapp(
            phone_number="+5491112345678",
            message="Test message"
        )
        
        # Verificar resultado
        self.assertTrue(result['success'])
        self.assertEqual(result['message_id'], 'test_123')
    
    @patch('app.services.notification_service._send_via_twilio')
    def test_send_whatsapp_failure(self, mock_send):
        """Test para envío fallido de WhatsApp"""
        # Mock de envío fallido
        mock_send.return_value = {'success': False, 'error': 'Test error'}
        
        # Test
        result = self.notification_service.send_whatsapp(
            phone_number="+5491112345678",
            message="Test message"
        )
        
        # Verificar resultado
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Test error')
    
    def test_send_appointment_confirmation(self):
        """Test para envío de confirmación de turno"""
        with patch.object(self.notification_service, 'send_whatsapp') as mock_send:
            mock_send.return_value = {'success': True}
            
            # Test
            result = self.notification_service.send_appointment_confirmation(
                phone_number="+5491112345678",
                appointment_date=date(2024, 1, 15),
                appointment_time="14:30",
                patient_name="Juan Pérez"
            )
            
            # Verificar que se llamó send_whatsapp
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            self.assertEqual(call_args[0][0], "+5491112345678")  # phone_number
            self.assertIn("confirmado", call_args[0][1])  # message

class TestAIService(unittest.TestCase):
    """Tests para el servicio de IA"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.ai_service = ai_service
    
    @patch('app.services.ai_service._call_openai')
    def test_analyze_message(self, mock_call):
        """Test para análisis de mensaje"""
        # Mock de respuesta de OpenAI
        mock_call.return_value = '''
        {
            "intention": "greeting",
            "confidence": 0.95,
            "entities": {},
            "response_type": "greeting",
            "needs_more_info": false
        }
        '''
        
        # Test
        result = self.ai_service.analyze_message(
            phone_number="+5491112345678",
            message="Hola"
        )
        
        # Verificar resultado
        self.assertEqual(result['intention'], 'greeting')
        self.assertEqual(result['confidence'], 0.95)
        self.assertEqual(result['response_type'], 'greeting')
    
    @patch('app.services.ai_service._call_openai')
    def test_generate_response(self, mock_call):
        """Test para generación de respuesta"""
        # Mock de respuesta de OpenAI
        mock_call.return_value = "¡Hola! ¿En qué puedo ayudarte?"
        
        # Test
        result = self.ai_service.generate_response(
            phone_number="+5491112345678",
            intention="greeting",
            entities={}
        )
        
        # Verificar resultado
        self.assertEqual(result, "¡Hola! ¿En qué puedo ayudarte?")
    
    def test_get_fallback_response(self):
        """Test para respuestas de fallback"""
        # Test con intención conocida
        result = self.ai_service._get_fallback_response('greeting')
        self.assertIn("¡Hola!", result)
        
        # Test con intención desconocida
        result = self.ai_service._get_fallback_response('unknown')
        self.assertIn("Disculpa", result)

class TestSchemas(unittest.TestCase):
    """Tests para los schemas de Pydantic"""
    
    def test_turno_create_valid(self):
        """Test para creación válida de turno"""
        turno_data = TurnoCreate(
            phone_number="+5491112345678",
            appointment_date=date(2024, 1, 15),
            appointment_time=time(14, 30),
            patient_name="Juan Pérez"
        )
        
        self.assertEqual(turno_data.phone_number, "+5491112345678")
        self.assertEqual(turno_data.appointment_date, date(2024, 1, 15))
        self.assertEqual(turno_data.appointment_time, time(14, 30))
        self.assertEqual(turno_data.patient_name, "Juan Pérez")
    
    def test_turno_create_invalid_phone(self):
        """Test para validación de teléfono inválido"""
        with self.assertRaises(ValueError):
            TurnoCreate(
                phone_number="123",  # Teléfono muy corto
                appointment_date=date(2024, 1, 15),
                appointment_time=time(14, 30)
            )
    
    def test_turno_create_past_date(self):
        """Test para validación de fecha en el pasado"""
        with self.assertRaises(ValueError):
            TurnoCreate(
                phone_number="+5491112345678",
                appointment_date=date(2020, 1, 15),  # Fecha en el pasado
                appointment_time=time(14, 30)
            )

if __name__ == '__main__':
    unittest.main() 