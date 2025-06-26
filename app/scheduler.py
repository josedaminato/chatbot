from apscheduler.schedulers.background import BackgroundScheduler
from app.services.whatsapp_service import send_whatsapp_message
from app.db.queries import get_past_unattended_appointments, get_connection
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()

def send_followup_messages():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id, patient_name, phone_number, appointment_date FROM appointments WHERE status = 'confirmado' AND followup_sent = 0 AND appointment_date < %s''', (yesterday,))
    turnos = c.fetchall()
    for turno in turnos:
        turno_id, patient_name, phone_number, appointment_date = turno
        message = f"Hola {patient_name}, ¿cómo te fue en la consulta? Si querés dejar una reseña o reprogramar otro turno, escribime 😊"
        send_whatsapp_message(phone_number, message)
        c.execute('UPDATE appointments SET followup_sent = 1 WHERE id = %s', (turno_id,))
    conn.commit()
    conn.close()

def mark_absences_and_send_followup():
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
        send_whatsapp_message(phone_number, message)
        c.execute('UPDATE appointments SET followup_sent = 1 WHERE id = %s', (turno_id,))
    conn.commit()
    conn.close()

def init_scheduler(app=None):
    scheduler.add_job(send_followup_messages, 'cron', hour=8, minute=0)  # Seguimiento post-turno
    scheduler.add_job(mark_absences_and_send_followup, 'cron', hour=9, minute=0)  # Gestión de ausencias
    scheduler.start() 