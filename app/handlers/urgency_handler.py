from twilio.twiml.messaging_response import MessagingResponse
from app.utils.config import get_clinic_name_and_email
from app.services.email_service import send_email_notification

def handle(phone_number, incoming_msg):
    """Procesa mensajes de urgencia, notifica por email y responde al paciente.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Lamento mucho lo que estás pasando. Voy a notificar al profesional para darte prioridad. ¿Te gustaría agendar lo antes posible?")
    clinic_name, professional_email = get_clinic_name_and_email()
    subject = f"URGENTE: Paciente requiere atención prioritaria en {clinic_name}"
    body = f"Mensaje urgente recibido de un paciente:\n\nTeléfono: {phone_number}\nMensaje: {incoming_msg}\n\nPor favor, evalúa si puedes hacer un espacio extra en la agenda o si con los turnos actuales puedes atenderlo."
    send_email_notification(professional_email, subject, body)
    return resp 