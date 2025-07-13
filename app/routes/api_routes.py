"""
Rutas de API REST para integración externa
Endpoints para servicios de terceros y aplicaciones móviles
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, date
from app.services import agenda_service, notification_service, ai_service
from app.schemas import TurnoCreate, TurnoUpdate, NotificacionCreate
from app.utils.validators import is_valid_phone
from app.config import CLINIC_NAME

logger = logging.getLogger('asistente_salud')

# Crear blueprint para API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check de la API"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Asistente de Salud API',
            'version': '1.0.0',
            'clinic_name': CLINIC_NAME,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/appointments', methods=['GET'])
def get_appointments():
    """Obtener turnos con filtros"""
    try:
        # Parámetros de filtrado
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        phone_number = request.args.get('phone_number')
        status = request.args.get('status')
        
        # Validar parámetros
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400
        
        # Obtener turnos según filtros
        if phone_number:
            appointments = agenda_service.get_appointments_by_phone(phone_number)
        elif start_date and end_date:
            appointments = agenda_service.get_appointments_by_date_range(start_date, end_date)
        elif start_date:
            appointments = agenda_service.get_appointments_by_date(start_date)
        else:
            # Sin filtros, devolver error
            return jsonify({'error': 'Se requiere al menos un filtro (start_date, end_date, phone_number)'}), 400
        
        # Filtrar por estado si se especifica
        if status:
            appointments = [apt for apt in appointments if apt.get('status') == status]
        
        return jsonify({
            'success': True,
            'appointments': appointments,
            'total': len(appointments)
        })
        
    except Exception as e:
        logger.error(f"Error al obtener turnos: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/appointments', methods=['POST'])
def create_appointment():
    """Crear un nuevo turno"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Validar datos requeridos
        required_fields = ['phone_number', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Validar número de teléfono
        if not is_valid_phone(data['phone_number']):
            return jsonify({'error': 'Número de teléfono inválido'}), 400
        
        # Crear objeto TurnoCreate
        try:
            appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Formato de fecha/hora inválido'}), 400
        
        turno_data = TurnoCreate(
            phone_number=data['phone_number'],
            patient_name=data.get('patient_name'),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            urgency_level=data.get('urgency_level'),
            notes=data.get('notes')
        )
        
        # Crear turno
        result = agenda_service.create_appointment(turno_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'appointment_id': result['appointment_id']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Error desconocido')
            }), 400
            
    except Exception as e:
        logger.error(f"Error al crear turno: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    """Obtener un turno específico"""
    try:
        appointment = agenda_service.get_appointment(appointment_id)
        
        if not appointment:
            return jsonify({'error': 'Turno no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'appointment': appointment
        })
        
    except Exception as e:
        logger.error(f"Error al obtener turno por ID: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Actualizar un turno"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Crear objeto TurnoUpdate
        update_data = TurnoUpdate()
        
        if 'phone_number' in data:
            if not is_valid_phone(data['phone_number']):
                return jsonify({'error': 'Número de teléfono inválido'}), 400
            update_data.phone_number = data['phone_number']
        
        if 'patient_name' in data:
            update_data.patient_name = data['patient_name']
        
        if 'appointment_date' in data:
            try:
                update_data.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400
        
        if 'appointment_time' in data:
            try:
                update_data.appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
            except ValueError:
                return jsonify({'error': 'Formato de hora inválido (HH:MM)'}), 400
        
        if 'urgency_level' in data:
            update_data.urgency_level = data['urgency_level']
        
        if 'notes' in data:
            update_data.notes = data['notes']
        
        if 'status' in data:
            update_data.status = data['status']
        
        # Actualizar turno
        result = agenda_service.update_appointment(appointment_id, update_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Error desconocido')
            }), 400
            
    except Exception as e:
        logger.error(f"Error al actualizar turno por ID: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancelar un turno"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Cancelado via API')
        
        result = agenda_service.cancel_appointment(appointment_id, reason)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('message', 'Error desconocido')
            }), 400
            
    except Exception as e:
        logger.error(f"Error al cancelar turno por ID: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/available-slots', methods=['GET'])
def get_available_slots():
    """Obtener horarios disponibles"""
    try:
        target_date = request.args.get('date')
        
        if not target_date:
            return jsonify({'error': 'Parámetro date requerido'}), 400
        
        try:
            date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400
        
        available_slots = agenda_service.get_available_slots(date_obj)
        
        return jsonify({
            'success': True,
            'date': target_date,
            'available_slots': available_slots
        })
        
    except Exception as e:
        logger.error(f"Error al obtener horarios disponibles: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/notifications', methods=['POST'])
def send_notification():
    """Enviar notificación"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Validar campos requeridos
        if 'phone_number' not in data or 'message' not in data:
            return jsonify({'error': 'phone_number y message son requeridos'}), 400
        
        # Validar número de teléfono
        if not is_valid_phone(data['phone_number']):
            return jsonify({'error': 'Número de teléfono inválido'}), 400
        
        # Enviar notificación
        result = notification_service.send_whatsapp(
            phone_number=data['phone_number'],
            message=data['message'],
            priority=data.get('priority', 'normal')
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Notificación enviada exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error desconocido')
            }), 400
            
    except Exception as e:
        logger.error(f"Error al enviar notificación: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/conversations/<phone_number>/analyze', methods=['POST'])
def analyze_message(phone_number):
    """Analizar mensaje con IA"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Campo message requerido'}), 400
        
        # Validar número de teléfono
        if not is_valid_phone(phone_number):
            return jsonify({'error': 'Número de teléfono inválido'}), 400
        
        # Analizar mensaje
        analysis = ai_service.analyze_message(phone_number, data['message'])
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error al analizar mensaje con IA: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/conversations/<phone_number>/summary', methods=['GET'])
def get_conversation_summary(phone_number):
    """Obtener resumen de conversación"""
    try:
        # Validar número de teléfono
        if not is_valid_phone(phone_number):
            return jsonify({'error': 'Número de teléfono inválido'}), 400
        
        # Obtener resumen
        summary = ai_service.get_conversation_summary(phone_number)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error al obtener resumen de conversación: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/conversations/<phone_number>/clear', methods=['POST'])
def clear_conversation(phone_number):
    """Limpiar contexto de conversación"""
    try:
        # Validar número de teléfono
        if not is_valid_phone(phone_number):
            return jsonify({'error': 'Número de teléfono inválido'}), 400
        
        # Limpiar contexto
        success = ai_service.clear_conversation_context(phone_number)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Contexto de conversación limpiado'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error limpiando contexto'
            }), 500
            
    except Exception as e:
        logger.error(f"Error al limpiar contexto de conversación: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 