from apscheduler.schedulers.background import BackgroundScheduler
from app.services.agenda_service import send_followup_messages, mark_absences_and_send_followup

scheduler = BackgroundScheduler()

def init_scheduler(app=None):
    """Inicializa el scheduler y programa los jobs periódicos.

    Args:
        app: Instancia opcional de Flask app.
    """
    scheduler.add_job(send_followup_messages, 'cron', hour=8, minute=0)  # Seguimiento post-turno
    scheduler.add_job(mark_absences_and_send_followup, 'cron', hour=9, minute=0)  # Gestión de ausencias
    scheduler.start() 