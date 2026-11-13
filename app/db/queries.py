"""
Queries completas para la base de datos
Funciones para interactuar con la BD - versión completa
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta

logger = logging.getLogger('asistente_salud')

# Simulación de base de datos en memoria para desarrollo
_appointments = []
_notifications = []
_conversation_states = {}
_feedback = []
_attachments = []

# ========================================
# FUNCIONES DE TURNOS
# ========================================

def save_appointment(appointment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Guarda un turno en la base de datos"""
    try:
        appointment_id = len(_appointments) + 1
        appointment = {
            'id': appointment_id,
            'phone_number': appointment_data.get('phone_number'),
            'patient_name': appointment_data.get('patient_name'),
            'appointment_date': appointment_data.get('appointment_date'),
            'appointment_time': appointment_data.get('appointment_time'),
            'urgency_level': appointment_data.get('urgency_level'),
            'notes': appointment_data.get('notes'),
            'status': 'pendiente',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        _appointments.append(appointment)
        logger.info(f"Turno guardado: ID {appointment_id}")
        return appointment
    except Exception as e:
        logger.error(f"Error guardando turno: {str(e)}")
        return {}

def create_appointment(appointment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea un nuevo turno en la base de datos"""
    return save_appointment(appointment_data)

def get_appointments(phone_number: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene turnos de la base de datos"""
    try:
        if phone_number:
            return [apt for apt in _appointments if apt.get('phone_number') == phone_number]
        return _appointments
    except Exception as e:
        logger.error(f"Error obteniendo turnos: {str(e)}")
        return []

def get_all_appointments() -> List[Dict[str, Any]]:
    """Obtiene todos los turnos de la base de datos"""
    return get_appointments()

def get_appointment(appointment_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un turno específico por ID"""
    try:
        for appointment in _appointments:
            if appointment.get('id') == appointment_id:
                return appointment
        return None
    except Exception as e:
        logger.error(f"Error obteniendo turno: {str(e)}")
        return None

def update_appointment(appointment_id: int, update_data: Dict[str, Any]) -> bool:
    """Actualiza un turno existente"""
    try:
        for appointment in _appointments:
            if appointment.get('id') == appointment_id:
                appointment.update(update_data)
                appointment['updated_at'] = datetime.now().isoformat()
                logger.info(f"Turno actualizado: ID {appointment_id}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error actualizando turno: {str(e)}")
        return False

def delete_appointment(appointment_id: int) -> bool:
    """Elimina un turno de la base de datos"""
    try:
        for i, appointment in enumerate(_appointments):
            if appointment.get('id') == appointment_id:
                del _appointments[i]
                logger.info(f"Turno eliminado: ID {appointment_id}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error eliminando turno: {str(e)}")
        return False

def get_appointments_by_date(date: str) -> List[Dict[str, Any]]:
    """Obtiene todos los turnos para una fecha específica"""
    try:
        appointments = []
        for appointment in _appointments:
            if appointment.get('appointment_date') == date:
                appointments.append(appointment)
        return appointments
    except Exception as e:
        logger.error(f"Error obteniendo turnos por fecha: {str(e)}")
        return []

def get_upcoming_appointments() -> List[Dict[str, Any]]:
    """Obtiene turnos futuros"""
    try:
        today = datetime.now().date()
        upcoming = []
        for appointment in _appointments:
            apt_date = appointment.get('appointment_date')
            if apt_date and apt_date >= today.isoformat():
                upcoming.append(appointment)
        return upcoming
    except Exception as e:
        logger.error(f"Error obteniendo turnos futuros: {str(e)}")
        return []

def get_past_unattended_appointments() -> List[Dict[str, Any]]:
    """Obtiene turnos pasados sin asistir"""
    try:
        today = datetime.now().date()
        past_unattended = []
        for appointment in _appointments:
            apt_date = appointment.get('appointment_date')
            if apt_date and apt_date < today.isoformat() and appointment.get('status') == 'pendiente':
                past_unattended.append(appointment)
        return past_unattended
    except Exception as e:
        logger.error(f"Error obteniendo turnos pasados sin asistir: {str(e)}")
        return []

def get_last_appointment(phone_number: str) -> Optional[Dict[str, Any]]:
    """Obtiene el último turno de un paciente"""
    try:
        appointments = [apt for apt in _appointments if apt.get('phone_number') == phone_number]
        if appointments:
            return max(appointments, key=lambda x: x.get('created_at', ''))
        return None
    except Exception as e:
        logger.error(f"Error obteniendo último turno: {str(e)}")
        return None

def get_last_appointment_id_by_phone(phone_number: str) -> Optional[int]:
    """Obtiene el ID del último turno de un paciente"""
    try:
        last_appointment = get_last_appointment(phone_number)
        return last_appointment.get('id') if last_appointment else None
    except Exception as e:
        logger.error(f"Error obteniendo ID del último turno: {str(e)}")
        return None

def mark_appointment_absent(appointment_id: int) -> bool:
    """Marca un turno como ausente"""
    try:
        return update_appointment(appointment_id, {"status": "ausente"})
    except Exception as e:
        logger.error(f"Error marcando turno como ausente: {str(e)}")
        return False

# ========================================
# FUNCIONES DE NOTIFICACIONES
# ========================================

def save_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """Guarda una notificación en la base de datos"""
    try:
        notification_id = len(_notifications) + 1
        notification = {
            'id': notification_id,
            'phone_number': notification_data.get('phone_number'),
            'message': notification_data.get('message'),
            'notification_type': notification_data.get('notification_type'),
            'status': 'pendiente',
            'created_at': datetime.now().isoformat(),
            'sent_at': None,
            'error_message': None,
            'retry_count': 0
        }
        _notifications.append(notification)
        logger.info(f"Notificación guardada: ID {notification_id}")
        return notification
    except Exception as e:
        logger.error(f"Error guardando notificación: {str(e)}")
        return {}

def get_notifications(phone_number: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtiene notificaciones de la base de datos"""
    try:
        if phone_number:
            return [notif for notif in _notifications if notif.get('phone_number') == phone_number]
        return _notifications
    except Exception as e:
        logger.error(f"Error obteniendo notificaciones: {str(e)}")
        return []

def update_notification(notification_id: int, update_data: Dict[str, Any]) -> bool:
    """Actualiza una notificación existente"""
    try:
        for notification in _notifications:
            if notification.get('id') == notification_id:
                notification.update(update_data)
                logger.info(f"Notificación actualizada: ID {notification_id}")
                return True
        return False
    except Exception as e:
        logger.error(f"Error actualizando notificación: {str(e)}")
        return False

# ========================================
# FUNCIONES DE ESTADO DE CONVERSACIÓN
# ========================================

def get_conversation_state(phone_number: str) -> Dict[str, Any]:
    """Obtiene el estado de conversación de un usuario"""
    return _conversation_states.get(phone_number, {})

def save_conversation_state(phone_number: str, state: Dict[str, Any]) -> bool:
    """Guarda el estado de conversación de un usuario"""
    try:
        _conversation_states[phone_number] = state
        logger.info(f"Estado de conversación guardado para {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Error guardando estado de conversación: {str(e)}")
        return False

def update_conversation_state(phone_number: str, state: Dict[str, Any]) -> bool:
    """Actualiza el estado de conversación de un usuario"""
    try:
        if phone_number in _conversation_states:
            _conversation_states[phone_number].update(state)
        else:
            _conversation_states[phone_number] = state
        logger.info(f"Estado de conversación actualizado para {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Error actualizando estado de conversación: {str(e)}")
        return False

def create_conversation_state(phone_number: str, state: Dict[str, Any]) -> bool:
    """Crea un nuevo estado de conversación para un usuario"""
    try:
        _conversation_states[phone_number] = state
        logger.info(f"Nuevo estado de conversación creado para {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Error creando estado de conversación: {str(e)}")
        return False

def clear_conversation_state(phone_number: str) -> bool:
    """Limpia el estado de conversación de un usuario"""
    try:
        if phone_number in _conversation_states:
            del _conversation_states[phone_number]
            logger.info(f"Estado de conversación limpiado para {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Error limpiando estado de conversación: {str(e)}")
        return False

# ========================================
# FUNCIONES DE FEEDBACK
# ========================================

def insert_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserta feedback en la base de datos"""
    try:
        feedback_id = len(_feedback) + 1
        feedback = {
            'id': feedback_id,
            'phone_number': feedback_data.get('phone_number'),
            'rating': feedback_data.get('rating'),
            'comment': feedback_data.get('comment'),
            'created_at': datetime.now().isoformat()
        }
        _feedback.append(feedback)
        logger.info(f"Feedback insertado: ID {feedback_id}")
        return feedback
    except Exception as e:
        logger.error(f"Error insertando feedback: {str(e)}")
        return {}

def get_all_feedback() -> List[Dict[str, Any]]:
    """Obtiene todo el feedback"""
    try:
        return _feedback
    except Exception as e:
        logger.error(f"Error obteniendo feedback: {str(e)}")
        return []

# ========================================
# FUNCIONES DE ADJUNTOS
# ========================================

def insert_attachment(attachment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserta un adjunto en la base de datos"""
    try:
        attachment_id = len(_attachments) + 1
        attachment = {
            'id': attachment_id,
            'appointment_id': attachment_data.get('appointment_id'),
            'phone_number': attachment_data.get('phone_number'),
            'filename': attachment_data.get('filename'),
            'file_type': attachment_data.get('file_type'),
            'file_size': attachment_data.get('file_size'),
            'created_at': datetime.now().isoformat()
        }
        _attachments.append(attachment)
        logger.info(f"Adjunto insertado: ID {attachment_id}")
        return attachment
    except Exception as e:
        logger.error(f"Error insertando adjunto: {str(e)}")
        return {}

def get_settings() -> Dict[str, Any]:
    """Obtiene configuraciones del sistema"""
    return {
        'clinic_name': 'Clínica Demo',
        'professional_email': 'profesional@clinica.com',
        'whatsapp_provider': 'twilio'
    }

# ========================================
# FUNCIONES DE CONEXIÓN (para compatibilidad)
# ========================================

def get_connection():
    """Obtiene conexión a la base de datos (simulado)"""
    return None

def close_connection(connection):
    """Cierra la conexión a la base de datos (simulado)"""
    pass

def test_connection() -> bool:
    """Prueba la conexión a la base de datos (simulado)"""
    return True

def get_appointments_by_date_range(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """Obtiene turnos en un rango de fechas"""
    try:
        appointments = []
        for appointment in _appointments:
            apt_date = appointment.get('appointment_date')
            if apt_date and start_date <= apt_date <= end_date:
                appointments.append(appointment)
        return appointments
    except Exception as e:
        logger.error(f"Error obteniendo turnos por rango de fechas: {str(e)}")
        return []

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por nombre de usuario"""
    # Implementación simplificada - retorna None
    return None

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea un nuevo usuario"""
    # Implementación simplificada
    return {
        'id': 1,
        'username': user_data.get('username'),
        'email': user_data.get('email'),
        'full_name': user_data.get('full_name'),
        'role': user_data.get('role', 'asistente'),
        'status': 'activo'
    }

def get_all_users() -> List[Dict[str, Any]]:
    """Obtiene todos los usuarios"""
    # Implementación simplificada - retorna lista vacía
    return []

def get_notifications_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de notificaciones"""
    # Implementación simplificada
    return {
        'total': 0,
        'sent': 0,
        'failed': 0,
        'pending': 0
    }

def get_conversation_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de conversaciones"""
    # Implementación simplificada
    return {
        'total_conversations': 0,
        'active_conversations': 0,
        'messages_today': 0
    }
