# Funciones para consultar e insertar datos en la base de datos 

import os
from app.db.postgres import get_connection
from datetime import datetime, timedelta
import hashlib
import logging

def get_last_appointment(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM appointments WHERE phone_number = %s ORDER BY appointment_date DESC LIMIT 1''', (phone_number,))
    result = c.fetchone()
    conn.close()
    return result

def get_last_appointment_id_by_phone(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id FROM appointments WHERE phone_number = %s ORDER BY appointment_date DESC LIMIT 1''', (phone_number,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def insert_pending_appointment(phone_number, appointment_date, profesional=None, especialidad=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO pending_appointments (phone_number, appointment_date, profesional, especialidad) VALUES (%s, %s, %s, %s) ON CONFLICT (phone_number) DO UPDATE SET appointment_date = EXCLUDED.appointment_date, profesional = EXCLUDED.profesional, especialidad = EXCLUDED.especialidad''',
              (phone_number, appointment_date, profesional, especialidad))
    conn.commit()
    conn.close()

def get_pending_appointment(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT appointment_date, profesional, especialidad FROM pending_appointments WHERE phone_number = %s''', (phone_number,))
    result = c.fetchone()
    conn.close()
    return result

def delete_pending_appointment(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM pending_appointments WHERE phone_number = %s', (phone_number,))
    conn.commit()
    conn.close()

def insert_appointment(patient_name, phone_number, appointment_date, profesional, especialidad, status, confirmation_sent=False):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO appointments (patient_name, phone_number, appointment_date, profesional, especialidad, status, confirmation_sent) VALUES (%s, %s, %s, %s, %s, %s, %s)''',
              (patient_name, phone_number, appointment_date, profesional, especialidad, status, confirmation_sent))
    conn.commit()
    conn.close()

def mark_appointment_as_confirmed(appointment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE appointments SET status = %s WHERE id = %s', ('confirmado', appointment_id))
    conn.commit()
    conn.close()

def cancel_appointment(appointment_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM appointments WHERE id = %s', (appointment_id,))
    conn.commit()
    conn.close()

def get_upcoming_appointments(phone_number, now=None):
    if now is None:
        now = datetime.now()
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM appointments WHERE phone_number = %s AND appointment_date > %s AND status IN ('pendiente', 'confirmado') ORDER BY appointment_date ASC''', (phone_number, now))
    results = c.fetchall()
    conn.close()
    return results

def get_past_unattended_appointments(now=None):
    if now is None:
        now = datetime.now()
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT * FROM appointments WHERE status = 'confirmado' AND appointment_date < %s AND (attended IS NULL OR attended = FALSE)''', (now,))
    results = c.fetchall()
    conn.close()
    return results

def insert_attachment(appointment_id, phone_number, filename, file_path):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO attachments (appointment_id, phone_number, filename, file_path) VALUES (%s, %s, %s, %s)''',
              (appointment_id, phone_number, filename, file_path))
    conn.commit()
    conn.close()

def insert_feedback(patient_name, phone_number, feedback_text):
    """Inserta un feedback de paciente en la base de datos.

    Args:
        patient_name (str): Nombre del paciente.
        phone_number (str): Teléfono del paciente.
        feedback_text (str): Texto del feedback.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO feedback (patient_name, phone_number, feedback_text) VALUES (%s, %s, %s)''',
              (patient_name, phone_number, feedback_text))
    conn.commit()
    conn.close()

def get_all_feedback():
    """Obtiene todos los feedbacks registrados en la base de datos.

    Returns:
        list: Lista de tuplas con los feedbacks.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT patient_name, phone_number, feedback_date, feedback_text FROM feedback ORDER BY feedback_date DESC''')
    results = c.fetchall()
    conn.close()
    return results

def hash_password(password):
    """Genera hash seguro de la contraseña usando salt.
    
    Args:
        password (str): Contraseña en texto plano.
        
    Returns:
        str: Hash de la contraseña.
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + key.hex()

def verify_password(stored_password, provided_password):
    """Verifica si la contraseña proporcionada coincide con el hash almacenado.
    
    Args:
        stored_password (str): Hash almacenado en la base de datos.
        provided_password (str): Contraseña proporcionada por el usuario.
        
    Returns:
        bool: True si la contraseña es correcta.
    """
    salt = bytes.fromhex(stored_password[:64])
    stored_key = bytes.fromhex(stored_password[64:])
    key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return stored_key == key

def create_user(username, password, full_name, email, role='professional'):
    """Crea un nuevo usuario en la base de datos.
    
    Args:
        username (str): Nombre de usuario único.
        password (str): Contraseña en texto plano.
        full_name (str): Nombre completo del profesional.
        email (str): Email único del profesional.
        role (str): Rol del usuario (default: 'professional').
        
    Returns:
        bool: True si se creó exitosamente.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('''INSERT INTO users (username, password_hash, full_name, email, role) 
                     VALUES (%s, %s, %s, %s, %s)''', 
                  (username, password_hash, full_name, email, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return False

def authenticate_user(username, password):
    """Autentica un usuario con username y contraseña.
    
    Args:
        username (str): Nombre de usuario.
        password (str): Contraseña en texto plano.
        
    Returns:
        dict: Datos del usuario si la autenticación es exitosa, None si no.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash, full_name, email, role FROM users WHERE username = %s', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and verify_password(user[2], password):
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[3],
                'email': user[4],
                'role': user[5]
            }
        return None
    except Exception as e:
        logging.error(f"Error authenticating user: {e}")
        return None

def get_user_by_id(user_id):
    """Obtiene un usuario por su ID.
    
    Args:
        user_id (int): ID del usuario.
        
    Returns:
        dict: Datos del usuario o None si no existe.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, username, full_name, email, role FROM users WHERE id = %s', (user_id,))
        user = c.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[2],
                'email': user[3],
                'role': user[4]
            }
        return None
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return None

# Funciones para el dashboard
def get_dashboard_stats():
    """Obtiene estadísticas generales para el dashboard.
    
    Returns:
        dict: Estadísticas de turnos, urgencias, etc.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        
        # Turnos hoy
        today = datetime.now().date()
        c.execute("SELECT COUNT(*) FROM appointments WHERE DATE(appointment_date) = %s", (today,))
        appointments_today = c.fetchone()[0]
        
        # Turnos pendientes
        c.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date > NOW() AND status = 'pendiente'")
        pending_appointments = c.fetchone()[0]
        
        # Ausencias recientes
        c.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date < NOW() AND (attended IS NULL OR attended = FALSE)")
        recent_absences = c.fetchone()[0]
        
        # Feedback reciente
        c.execute("SELECT COUNT(*) FROM feedback WHERE feedback_date > NOW() - INTERVAL '7 days'")
        recent_feedback = c.fetchone()[0]
        
        conn.close()
        
        return {
            'appointments_today': appointments_today,
            'pending_appointments': pending_appointments,
            'recent_absences': recent_absences,
            'recent_feedback': recent_feedback
        }
    except Exception as e:
        logging.error(f"Error getting dashboard stats: {e}")
        return {}

def get_recent_appointments(limit=10):
    """Obtiene los turnos más recientes.
    
    Args:
        limit (int): Número máximo de turnos a obtener.
        
    Returns:
        list: Lista de turnos recientes.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT patient_name, phone_number, appointment_date, status, especialidad 
            FROM appointments 
            ORDER BY appointment_date DESC 
            LIMIT %s
        """, (limit,))
        appointments = c.fetchall()
        conn.close()
        return appointments
    except Exception as e:
        logging.error(f"Error getting recent appointments: {e}")
        return []

def get_urgent_messages(limit=10):
    """Obtiene mensajes urgentes recientes.
    
    Args:
        limit (int): Número máximo de mensajes a obtener.
        
    Returns:
        list: Lista de mensajes urgentes.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT patient_name, phone_number, appointment_date, status 
            FROM appointments 
            WHERE status = 'urgente' OR especialidad = 'urgencia'
            ORDER BY appointment_date DESC 
            LIMIT %s
        """, (limit,))
        urgent_messages = c.fetchall()
        conn.close()
        return urgent_messages
    except Exception as e:
        logging.error(f"Error getting urgent messages: {e}")
        return []

def get_recent_images(limit=10):
    """Obtiene las imágenes más recientes subidas por pacientes.
    
    Args:
        limit (int): Número máximo de imágenes a obtener.
        
    Returns:
        list: Lista de imágenes recientes.
    """
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT a.patient_name, a.phone_number, att.filename, att.upload_date, att.file_path
            FROM attachments att
            LEFT JOIN appointments a ON att.appointment_id = a.id
            ORDER BY att.upload_date DESC 
            LIMIT %s
        """, (limit,))
        images = c.fetchall()
        conn.close()
        return images
    except Exception as e:
        logging.error(f"Error getting recent images: {e}")
        return [] 

# --- CONTEXTO CONVERSACIONAL ---
def get_conversation_state(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT last_intent, fecha, hora, nombre, profesional, especialidad 
        FROM conversation_state WHERE phone_number = %s
    """, (phone_number,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "last_intent": row[0],
            "fecha": row[1],
            "hora": row[2],
            "nombre": row[3],
            "profesional": row[4],
            "especialidad": row[5]
        }
    return None

def update_conversation_state(phone_number, **kwargs):
    conn = get_connection()
    c = conn.cursor()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = %s")
        values.append(v)
    values.append(phone_number)
    set_clause = ", ".join(fields) + ", last_update = NOW()"
    # Insertar o actualizar
    insert_fields = ', '.join(['phone_number'] + list(kwargs.keys()) + ['last_update'])
    insert_values = ', '.join(['%s'] * (len(kwargs) + 2))
    c.execute(f"""
        INSERT INTO conversation_state ({insert_fields})
        VALUES ({', '.join(['%s'] * (len(kwargs) + 2))})
        ON CONFLICT (phone_number) DO UPDATE SET {set_clause}
    """, [phone_number] + list(kwargs.values()) + [datetime.now()])
    conn.commit()
    conn.close()

def clear_conversation_state(phone_number):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM conversation_state WHERE phone_number = %s", (phone_number,))
    conn.commit()
    conn.close() 