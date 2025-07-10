"""
Rutas del dashboard para panel de administración
Gestión de turnos, usuarios y estadísticas
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
import logging
from datetime import datetime, date, timedelta
from app.services import agenda_service, notification_service, ai_service
from app.schemas import TurnoCreate, TurnoUpdate, UsuarioLogin
from app.config import CLINIC_NAME
from app.logging_config import log_error_with_context
from app.db.queries import (
    get_all_appointments, get_appointments_by_date_range,
    get_user_by_username, create_user, get_all_users,
    get_notifications_stats, get_conversation_stats
)

logger = logging.getLogger('asistente_salud')

# Crear blueprint para dashboard
dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('dashboard.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login del dashboard"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Validar credenciales
            user = get_user_by_username(username)
            if user and user['password'] == password:  # En producción usar bcrypt
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_role'] = user['role']
                session['full_name'] = user['full_name']
                
                logger.info(f"Usuario {username} inició sesión")
                flash('Sesión iniciada correctamente', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('Credenciales inválidas', 'error')
                
        except Exception as e:
            log_error_with_context(logger, e)
            flash('Error al iniciar sesión', 'error')
    
    return render_template('dashboard/login.html', clinic_name=CLINIC_NAME)

@dashboard_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('dashboard.login'))

@dashboard_bp.route('/')
@login_required
def index():
    """Página principal del dashboard"""
    try:
        # Obtener estadísticas
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Turnos de hoy
        today_appointments = agenda_service.get_appointments_by_date(today)
        
        # Turnos de la semana
        week_appointments = get_appointments_by_date_range(week_start, week_end)
        
        # Estadísticas de notificaciones
        notification_stats = get_notifications_stats()
        
        # Estadísticas de conversaciones
        conversation_stats = get_conversation_stats()
        
        context = {
            'clinic_name': CLINIC_NAME,
            'today_appointments': today_appointments,
            'week_appointments': week_appointments,
            'notification_stats': notification_stats,
            'conversation_stats': conversation_stats,
            'user': {
                'username': session.get('username'),
                'full_name': session.get('full_name'),
                'role': session.get('user_role')
            }
        }
        
        return render_template('dashboard/index.html', **context)
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error cargando el dashboard', 'error')
        return render_template('dashboard/index.html', clinic_name=CLINIC_NAME)

@dashboard_bp.route('/appointments')
@login_required
def appointments():
    """Página de gestión de turnos"""
    try:
        # Parámetros de filtrado
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        # Obtener turnos filtrados
        if start_date and end_date:
            appointments = get_appointments_by_date_range(
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                datetime.strptime(end_date, '%Y-%m-%d').date()
            )
        else:
            # Por defecto mostrar turnos de la próxima semana
            today = date.today()
            week_end = today + timedelta(days=7)
            appointments = get_appointments_by_date_range(today, week_end)
        
        # Filtrar por estado si se especifica
        if status:
            appointments = [apt for apt in appointments if apt['status'] == status]
        
        context = {
            'clinic_name': CLINIC_NAME,
            'appointments': appointments,
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'status': status
            }
        }
        
        return render_template('dashboard/appointments.html', **context)
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error cargando turnos', 'error')
        return render_template('dashboard/appointments.html', clinic_name=CLINIC_NAME)

@dashboard_bp.route('/appointments/<int:appointment_id>')
@login_required
def appointment_detail(appointment_id):
    """Detalle de un turno específico"""
    try:
        appointment = agenda_service.get_appointment(appointment_id)
        
        if not appointment:
            flash('Turno no encontrado', 'error')
            return redirect(url_for('dashboard.appointments'))
        
        context = {
            'clinic_name': CLINIC_NAME,
            'appointment': appointment
        }
        
        return render_template('dashboard/appointment_detail.html', **context)
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error cargando detalle del turno', 'error')
        return redirect(url_for('dashboard.appointments'))

@dashboard_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Cancelar un turno"""
    try:
        reason = request.form.get('reason', 'Cancelado por administrador')
        result = agenda_service.cancel_appointment(appointment_id, reason)
        
        if result['success']:
            flash('Turno cancelado exitosamente', 'success')
        else:
            flash(f"Error cancelando turno: {result.get('message', 'Error desconocido')}", 'error')
            
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error cancelando turno', 'error')
    
    return redirect(url_for('dashboard.appointment_detail', appointment_id=appointment_id))

@dashboard_bp.route('/appointments/<int:appointment_id>/mark-absent', methods=['POST'])
@login_required
def mark_absent(appointment_id):
    """Marcar turno como ausente"""
    try:
        result = agenda_service.mark_absent(appointment_id)
        
        if result['success']:
            flash('Turno marcado como ausente', 'success')
        else:
            flash(f"Error marcando ausente: {result.get('message', 'Error desconocido')}", 'error')
            
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error marcando ausente', 'error')
    
    return redirect(url_for('dashboard.appointment_detail', appointment_id=appointment_id))

@dashboard_bp.route('/notifications')
@login_required
def notifications():
    """Página de notificaciones"""
    try:
        # Obtener notificaciones pendientes
        pending_notifications = notification_service.get_pending_notifications()
        
        context = {
            'clinic_name': CLINIC_NAME,
            'pending_notifications': pending_notifications
        }
        
        return render_template('dashboard/notifications.html', **context)
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error cargando notificaciones', 'error')
        return render_template('dashboard/notifications.html', clinic_name=CLINIC_NAME)

@dashboard_bp.route('/notifications/retry', methods=['POST'])
@login_required
def retry_notifications():
    """Reintentar notificaciones fallidas"""
    try:
        result = notification_service.retry_failed_notifications()
        
        if result['success']:
            flash(f"Reintentadas {result['retried']} notificaciones. {result['successful']} exitosas, {result['failed']} fallidas", 'info')
        else:
            flash(f"Error reintentando notificaciones: {result.get('error', 'Error desconocido')}", 'error')
            
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error reintentando notificaciones', 'error')
    
    return redirect(url_for('dashboard.notifications'))

@dashboard_bp.route('/users')
@admin_required
def users():
    """Página de gestión de usuarios (solo admin)"""
    try:
        users = get_all_users()
        
        context = {
            'clinic_name': CLINIC_NAME,
            'users': users
        }
        
        return render_template('dashboard/users.html', **context)
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        flash('Error cargando usuarios', 'error')
        return render_template('dashboard/users.html', clinic_name=CLINIC_NAME)

@dashboard_bp.route('/api/appointments', methods=['GET'])
@login_required
def api_appointments():
    """API para obtener turnos (para AJAX)"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            appointments = get_appointments_by_date_range(
                datetime.strptime(start_date, '%Y-%m-%d').date(),
                datetime.strptime(end_date, '%Y-%m-%d').date()
            )
        else:
            appointments = get_all_appointments()
        
        return jsonify({
            'success': True,
            'appointments': appointments
        })
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/available-slots', methods=['GET'])
@login_required
def api_available_slots():
    """API para obtener horarios disponibles"""
    try:
        target_date = request.args.get('date')
        if not target_date:
            return jsonify({'error': 'Fecha requerida'}), 400
        
        date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        available_slots = agenda_service.get_available_slots(date_obj)
        
        return jsonify({
            'success': True,
            'available_slots': available_slots
        })
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/conversations/<phone_number>')
@login_required
def api_conversation_summary(phone_number):
    """API para obtener resumen de conversación"""
    try:
        summary = ai_service.get_conversation_summary(phone_number)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        log_error_with_context(logger, e, user_id=session.get('user_id'))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 