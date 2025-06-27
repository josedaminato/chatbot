# Funciones para consultar e insertar datos en la base de datos 

import os
from app.db.postgres import get_connection
from datetime import datetime

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