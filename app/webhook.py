from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.utils.keywords import (
    SALUDOS, CANCEL_KEYWORDS, CONFIRM_KEYWORDS, URGENCY_KEYWORDS,
    PREGUNTAS_OBRA_SOCIAL, PREGUNTAS_COSTO, PREGUNTAS_UBICACION, PREGUNTAS_GRATIS
)
from app.db.queries import (
    get_last_appointment, insert_pending_appointment, get_pending_appointment, delete_pending_appointment,
    insert_appointment, mark_appointment_as_confirmed, cancel_appointment
)
from app.services.calendar_service import get_google_calendar_service, is_slot_available_in_calendar, create_calendar_event
from app.services.email_service import send_email_notification
from app.services.whatsapp_service import send_whatsapp_message
from app.services.image_handler import save_image_and_notify
from app.utils.config import get_clinic_name_and_email, WHATSAPP_PROVIDER, PLAN
import re
from datetime import datetime, timedelta

webhook_bp = Blueprint('webhook', __name__)

# --- HANDLERS ---
def handle_greeting(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    clinic_name, _ = get_clinic_name_and_email()
    msg.body(f"¡Hola! Soy el asistente virtual de {clinic_name}. ¿En qué puedo ayudarte?")
    return resp

def handle_appointment_request(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Para qué fecha deseas el turno? (DD/MM/YYYY)")
    return resp

def handle_date_response(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Qué horario prefieres?")
    return resp

def handle_time_response(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Por favor, indícame tu nombre completo para finalizar la reserva del turno.")
    return resp

def handle_patient_name(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¡Turno reservado exitosamente! Te esperamos.")
    return resp

def handle_cancellation(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Seguro que deseas cancelar tu turno? Responde SÍ para confirmar.")
    return resp

def handle_confirmation(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Tu turno fue cancelado correctamente. Si deseas agendar otro, avísame.")
    return resp

def handle_urgency(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Lamento mucho lo que estás pasando. Voy a notificar al profesional para darte prioridad. ¿Te gustaría agendar lo antes posible?")
    clinic_name, professional_email = get_clinic_name_and_email()
    subject = f"URGENTE: Paciente requiere atención prioritaria en {clinic_name}"
    body = f"Mensaje urgente recibido de un paciente:\n\nTeléfono: {phone_number}\nMensaje: {incoming_msg}\n\nPor favor, evalúa si puedes hacer un espacio extra en la agenda o si con los turnos actuales puedes atenderlo."
    send_email_notification(professional_email, subject, body)
    return resp

def handle_image_upload(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    media_url = request.values.get('MediaUrl0')
    success = save_image_and_notify(phone_number, None, media_url)
    clinic_name, _ = get_clinic_name_and_email()
    if success:
        msg.body(f"{clinic_name}: Imagen recibida correctamente. El profesional la revisará antes de tu consulta.")
    else:
        msg.body(f"{clinic_name}: Hubo un problema al procesar la imagen. Por favor, inténtalo de nuevo.")
    return resp

# --- ENDPOINT ---
@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    phone_number = request.values.get('From', '')
    # Saludo
    if any(saludo in incoming_msg for saludo in SALUDOS):
        return str(handle_greeting(phone_number, incoming_msg))
    # Cancelación
    if any(word in incoming_msg for word in CANCEL_KEYWORDS):
        return str(handle_cancellation(phone_number, incoming_msg))
    # Confirmación
    if any(word in incoming_msg for word in CONFIRM_KEYWORDS):
        return str(handle_confirmation(phone_number, incoming_msg))
    # Urgencia
    if any(word in incoming_msg for word in URGENCY_KEYWORDS):
        return str(handle_urgency(phone_number, incoming_msg))
    # Imagen
    if request.values.get('MediaUrl0'):
        return str(handle_image_upload(phone_number, incoming_msg))
    # Preguntas frecuentes (ejemplo)
    if any(p in incoming_msg for p in PREGUNTAS_OBRA_SOCIAL):
        resp = MessagingResponse()
        msg = resp.message()
        clinic_name, _ = get_clinic_name_and_email()
        msg.body(f"{clinic_name}: Sí, trabajamos con las siguientes obras sociales: [Lista de obras sociales]. ¿Te gustaría agendar un turno?")
        return str(resp)
    if any(p in incoming_msg for p in PREGUNTAS_COSTO):
        resp = MessagingResponse()
        msg = resp.message()
        clinic_name, _ = get_clinic_name_and_email()
        msg.body(f"{clinic_name}: El costo de la consulta es de $XXXX. ¿Deseas agendar un turno?")
        return str(resp)
    if any(p in incoming_msg for p in PREGUNTAS_UBICACION):
        resp = MessagingResponse()
        msg = resp.message()
        clinic_name, _ = get_clinic_name_and_email()
        msg.body(f"{clinic_name}: Estamos ubicados en [Dirección de la clínica]. ¿Te gustaría agendar un turno?")
        return str(resp)
    if any(p in incoming_msg for p in PREGUNTAS_GRATIS):
        resp = MessagingResponse()
        msg = resp.message()
        clinic_name, _ = get_clinic_name_and_email()
        msg.body(f"{clinic_name}: Las consultas no son gratuitas. Si deseas saber el costo o agendar un turno, avísame.")
        return str(resp)
    # Solicitud de turno
    if 'turno' in incoming_msg:
        return str(handle_appointment_request(phone_number, incoming_msg))
    # Fecha (DD/MM/YYYY)
    if re.search(r'(\d{2}/\d{2}/\d{4})', incoming_msg):
        return str(handle_date_response(phone_number, incoming_msg))
    # Hora (HH:MM)
    if re.search(r'\b([0-1][0-9]|2[0-3]):[0-5][0-9]\b', incoming_msg):
        return str(handle_time_response(phone_number, incoming_msg))
    # Nombre del paciente (simplificado)
    if len(incoming_msg.split()) >= 2 and incoming_msg.replace(' ', '').isalpha():
        return str(handle_patient_name(phone_number, incoming_msg))
    # Respuesta por defecto
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("No entendí tu mensaje. ¿Podrías reformularlo?")
    return str(resp) 