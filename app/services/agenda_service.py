"""
Servicio de agenda para gestión de turnos y citas
Maneja la lógica de negocio para turnos
"""

import logging
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from app.config import CLINIC_NAME
from app.schemas.turno_schema import TurnoCreate, TurnoUpdate, TurnoResponse, EstadoTurno
from app.db.queries import (
    create_appointment, get_appointment, update_appointment,
    delete_appointment, get_appointments_by_date, get_all_appointments,
    get_appointments_by_phone, mark_appointment_absent
)

logger = logging.getLogger('asistente_salud')

class AgendaService:
    """Servicio para gestión de agenda y turnos"""
    
    def __init__(self):
        self.clinic_name = CLINIC_NAME
    
    def create_appointment(self, turno_data: TurnoCreate) -> Dict[str, Any]:
        """
        Crea un nuevo turno
        
        Args:
            turno_data: Datos del turno a crear
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Validar disponibilidad
            if not self._check_availability(turno_data.appointment_date, turno_data.appointment_time):
                return {
                    'success': False,
                    'message': f'No hay disponibilidad para el {turno_data.appointment_date} a las {turno_data.appointment_time}',
                    'error': 'SLOT_UNAVAILABLE'
                }
            
            # Crear el turno
            appointment_id = create_appointment(
                phone_number=turno_data.phone_number,
                patient_name=turno_data.patient_name,
                appointment_date=turno_data.appointment_date,
                appointment_time=turno_data.appointment_time,
                urgency_level=turno_data.urgency_level,
                notes=turno_data.notes
            )
            
            logger.info(f"Turno creado exitosamente - ID: {appointment_id}, Teléfono: {turno_data.phone_number}")
            
            return {
                'success': True,
                'message': f'Turno confirmado para el {turno_data.appointment_date} a las {turno_data.appointment_time}',
                'appointment_id': appointment_id,
                'appointment_date': turno_data.appointment_date,
                'appointment_time': turno_data.appointment_time
            }
            
        except Exception as e:
            logger.error(f"Error creando turno: {str(e)}")
            return {
                'success': False,
                'message': 'Error interno al crear el turno',
                'error': str(e)
            }
    
    def get_appointment(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un turno por ID
        
        Args:
            appointment_id: ID del turno
            
        Returns:
            Datos del turno o None si no existe
        """
        try:
            appointment = get_appointment(appointment_id)
            if appointment:
                return self._format_appointment_response(appointment)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo turno {appointment_id}: {str(e)}")
            return None
    
    def update_appointment(self, appointment_id: int, update_data: TurnoUpdate) -> Dict[str, Any]:
        """
        Actualiza un turno existente
        
        Args:
            appointment_id: ID del turno
            update_data: Datos a actualizar
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Verificar que el turno existe
            existing_appointment = get_appointment(appointment_id)
            if not existing_appointment:
                return {
                    'success': False,
                    'message': 'Turno no encontrado',
                    'error': 'APPOINTMENT_NOT_FOUND'
                }
            
            # Validar disponibilidad si se cambia fecha/hora
            if update_data.appointment_date and update_data.appointment_time:
                if not self._check_availability(update_data.appointment_date, update_data.appointment_time, exclude_id=appointment_id):
                    return {
                        'success': False,
                        'message': f'No hay disponibilidad para el {update_data.appointment_date} a las {update_data.appointment_time}',
                        'error': 'SLOT_UNAVAILABLE'
                    }
            
            # Actualizar el turno
            update_appointment(appointment_id, update_data.dict(exclude_unset=True))
            
            logger.info(f"Turno {appointment_id} actualizado exitosamente")
            
            return {
                'success': True,
                'message': 'Turno actualizado exitosamente'
            }
            
        except Exception as e:
            logger.error(f"Error actualizando turno {appointment_id}: {str(e)}")
            return {
                'success': False,
                'message': 'Error interno al actualizar el turno',
                'error': str(e)
            }
    
    def cancel_appointment(self, appointment_id: int, reason: str = None) -> Dict[str, Any]:
        """
        Cancela un turno
        
        Args:
            appointment_id: ID del turno
            reason: Motivo de la cancelación
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            # Verificar que el turno existe
            existing_appointment = get_appointment(appointment_id)
            if not existing_appointment:
                return {
                    'success': False,
                    'message': 'Turno no encontrado',
                    'error': 'APPOINTMENT_NOT_FOUND'
                }
            
            # Actualizar estado a cancelado
            update_data = TurnoUpdate(status=EstadoTurno.CANCELADO)
            update_appointment(appointment_id, update_data.dict(exclude_unset=True))
            
            logger.info(f"Turno {appointment_id} cancelado - Motivo: {reason}")
            
            return {
                'success': True,
                'message': 'Turno cancelado exitosamente'
            }
            
        except Exception as e:
            logger.error(f"Error cancelando turno {appointment_id}: {str(e)}")
            return {
                'success': False,
                'message': 'Error interno al cancelar el turno',
                'error': str(e)
            }
    
    def mark_absent(self, appointment_id: int) -> Dict[str, Any]:
        """
        Marca un turno como ausente
        
        Args:
            appointment_id: ID del turno
            
        Returns:
            Dict con el resultado de la operación
        """
        try:
            result = mark_appointment_absent(appointment_id)
            if result:
                logger.info(f"Turno {appointment_id} marcado como ausente")
                return {
                    'success': True,
                    'message': 'Turno marcado como ausente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Turno no encontrado',
                    'error': 'APPOINTMENT_NOT_FOUND'
                }
        except Exception as e:
            logger.error(f"Error marcando ausente turno {appointment_id}: {str(e)}")
            return {
                'success': False,
                'message': 'Error interno al marcar ausente',
                'error': str(e)
            }
    
    def get_appointments_by_date(self, target_date: date) -> List[Dict[str, Any]]:
        """
        Obtiene todos los turnos de una fecha específica
        
        Args:
            target_date: Fecha para buscar turnos
            
        Returns:
            Lista de turnos
        """
        try:
            appointments = get_appointments_by_date(target_date)
            return [self._format_appointment_response(apt) for apt in appointments]
        except Exception as e:
            logger.error(f"Error obteniendo turnos para {target_date}: {str(e)}")
            return []
    
    def get_appointments_by_phone(self, phone_number: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los turnos de un número de teléfono
        
        Args:
            phone_number: Número de teléfono
            
        Returns:
            Lista de turnos
        """
        try:
            appointments = get_appointments_by_phone(phone_number)
            return [self._format_appointment_response(apt) for apt in appointments]
        except Exception as e:
            logger.error(f"Error obteniendo turnos para {phone_number}: {str(e)}")
            return []
    
    def get_available_slots(self, target_date: date) -> List[str]:
        """
        Obtiene horarios disponibles para una fecha
        
        Args:
            target_date: Fecha para buscar disponibilidad
            
        Returns:
            Lista de horarios disponibles
        """
        try:
            # Horarios de trabajo (configurable)
            work_hours = [
                '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
                '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
            ]
            
            # Obtener turnos existentes para la fecha
            existing_appointments = get_appointments_by_date(target_date)
            booked_times = {apt['appointment_time'].strftime('%H:%M') for apt in existing_appointments}
            
            # Filtrar horarios disponibles
            available_slots = [time for time in work_hours if time not in booked_times]
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error obteniendo horarios disponibles para {target_date}: {str(e)}")
            return []
    
    def _check_availability(self, appointment_date: date, appointment_time: time, exclude_id: int = None) -> bool:
        """
        Verifica disponibilidad de un horario
        
        Args:
            appointment_date: Fecha del turno
            appointment_time: Hora del turno
            exclude_id: ID de turno a excluir (para actualizaciones)
            
        Returns:
            True si está disponible, False si no
        """
        try:
            existing_appointments = get_appointments_by_date(appointment_date)
            
            # Filtrar por hora y excluir el turno actual si se está actualizando
            conflicting_appointments = [
                apt for apt in existing_appointments
                if apt['appointment_time'] == appointment_time
                and (exclude_id is None or apt['id'] != exclude_id)
            ]
            
            return len(conflicting_appointments) == 0
            
        except Exception as e:
            logger.error(f"Error verificando disponibilidad: {str(e)}")
            return False
    
    def _format_appointment_response(self, appointment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea la respuesta de un turno
        
        Args:
            appointment: Datos del turno desde la base de datos
            
        Returns:
            Datos formateados
        """
        return {
            'id': appointment['id'],
            'phone_number': appointment['phone_number'],
            'patient_name': appointment['patient_name'],
            'appointment_date': appointment['appointment_date'].isoformat() if appointment['appointment_date'] else None,
            'appointment_time': appointment['appointment_time'].strftime('%H:%M') if appointment['appointment_time'] else None,
            'urgency_level': appointment['urgency_level'],
            'notes': appointment['notes'],
            'status': appointment['status'],
            'created_at': appointment['created_at'].isoformat() if appointment['created_at'] else None,
            'updated_at': appointment['updated_at'].isoformat() if appointment['updated_at'] else None
        } 