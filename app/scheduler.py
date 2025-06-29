from apscheduler.schedulers.background import BackgroundScheduler
from app.services.whatsapp_service import send_whatsapp_message
from app.db.queries import get_past_unattended_appointments, get_connection
from datetime import datetime, timedelta
import logging
from functools import wraps

scheduler = BackgroundScheduler()

def retry(max_retries=3):
    """Decorador para reintentar una función ante excepción, con logging de errores.

    Args:
        max_retries (int): Número máximo de reintentos.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logging.error(f"Error en {func.__name__}: {e}. Reintento {attempts}/{max_retries}")
            logging.error(f"Fallo definitivo en {func.__name__} tras {max_retries} reintentos.")
        return wrapper
    return decorator

@retry(max_retries=3)
def send_followup_messages():
    """Envía mensajes de seguimiento a pacientes que tuvieron turno el día anterior.

    Reintenta el envío si ocurre un error.
    """
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id, patient_name, phone_number, appointment_date FROM appointments WHERE status = 'confirmado' AND followup_sent = 0 AND appointment_date < %s''', (yesterday,))
    turnos = c.fetchall()
    for turno in turnos:
        turno_id, patient_name, phone_number, appointment_date = turno
        message = f"Hola {patient_name}, ¿cómo te fue en la consulta? Si querés dejar una reseña o reprogramar otro turno, escribime 😊"
        try:
            send_whatsapp_message(phone_number, message)
        except Exception as e:
            logging.error(f"Error enviando WhatsApp a {phone_number}: {e}")
            continue
        c.execute('UPDATE appointments SET followup_sent = 1 WHERE id = %s', (turno_id,))
    conn.commit()
    conn.close()

@retry(max_retries=3)
def mark_absences_and_send_followup():
    """Marca ausencias y envía mensajes de seguimiento a pacientes que no asistieron.

    Reintenta el envío si ocurre un error.
    """
    now = datetime.now()
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id, patient_name, phone_number, appointment_date FROM appointments WHERE status = 'confirmado' AND appointment_date < %s AND (attended IS NULL OR attended = 0) AND followup_sent = 0''', (now,))
    turnos = c.fetchall()
    for turno in turnos:
        turno_id, patient_name, phone_number, appointment_date = turno
        # Marcar como ausente
        c.execute('UPDATE appointments SET attended = 0 WHERE id = %s', (turno_id,))
        # Enviar mensaje de seguimiento por ausencia
        message = f"Hola {patient_name}, notamos que no asististe a tu turno. ¿Querés reprogramar o necesitas ayuda? Si fue un error, avísanos 😊"
        try:
            send_whatsapp_message(phone_number, message)
        except Exception as e:
            logging.error(f"Error enviando WhatsApp a {phone_number}: {e}")
            continue
        c.execute('UPDATE appointments SET followup_sent = 1 WHERE id = %s', (turno_id,))
    conn.commit()
    conn.close()

def init_scheduler(app=None):
    """Inicializa el scheduler y programa los jobs periódicos.

    Args:
        app: Instancia opcional de Flask app.
    """
    scheduler.add_job(send_followup_messages, 'cron', hour=8, minute=0)  # Seguimiento post-turno
    scheduler.add_job(mark_absences_and_send_followup, 'cron', hour=9, minute=0)  # Gestión de ausencias
    scheduler.start() 