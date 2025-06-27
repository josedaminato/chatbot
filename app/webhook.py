from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from app.utils.keywords import (
    SALUDOS, CANCEL_KEYWORDS, CONFIRM_KEYWORDS, URGENCY_KEYWORDS,
    PREGUNTAS_OBRA_SOCIAL, PREGUNTAS_COSTO, PREGUNTAS_UBICACION, PREGUNTAS_GRATIS,
    match_keywords, normalize_text
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
from app.utils.validators import is_valid_name, is_valid_phone, is_valid_date, is_valid_image
import re
from datetime import datetime, timedelta
from app.handlers import greeting_handler, appointment_handler, date_handler, time_handler, patient_name_handler, cancellation_handler, confirmation_handler, urgency_handler, image_handler, faq_handler, default_handler

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
    if not is_valid_name(incoming_msg):
        msg.body("El nombre ingresado no es válido. Por favor, ingresa solo letras y espacios.")
        return resp
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
    filename = request.values.get('MediaFileName0', 'archivo.jpg')
    if not is_valid_image(filename):
        msg.body("Solo se permiten imágenes JPG o PNG.")
        return str(resp)
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
    incoming_msg = request.values.get('Body', '')
    phone_number = request.values.get('From', '')
    norm_msg = normalize_text(incoming_msg)
    # Validar teléfono
    if not is_valid_phone(phone_number):
        resp = MessagingResponse()
        msg = resp.message()
        msg.body("El número de teléfono no es válido. Por favor, verifica el formato.")
        return str(resp)
    # Saludo
    if match_keywords(norm_msg, SALUDOS):
        return str(greeting_handler.handle(phone_number, incoming_msg))
    # Cancelación
    if match_keywords(norm_msg, CANCEL_KEYWORDS):
        return str(cancellation_handler.handle(phone_number, incoming_msg))
    # Confirmación
    if match_keywords(norm_msg, CONFIRM_KEYWORDS):
        return str(confirmation_handler.handle(phone_number, incoming_msg))
    # Urgencia
    if match_keywords(norm_msg, URGENCY_KEYWORDS):
        return str(urgency_handler.handle(phone_number, incoming_msg))
    # Imagen
    if request.values.get('MediaUrl0'):
        media_url = request.values.get('MediaUrl0')
        filename = request.values.get('MediaFileName0', 'archivo.jpg')
        return str(image_handler.handle(phone_number, incoming_msg, media_url, filename))
    # Preguntas frecuentes (ejemplo)
    if match_keywords(norm_msg, PREGUNTAS_OBRA_SOCIAL):
        return str(faq_handler.handle('obra_social', phone_number, incoming_msg))
    if match_keywords(norm_msg, PREGUNTAS_COSTO):
        return str(faq_handler.handle('costo', phone_number, incoming_msg))
    if match_keywords(norm_msg, PREGUNTAS_UBICACION):
        return str(faq_handler.handle('ubicacion', phone_number, incoming_msg))
    if match_keywords(norm_msg, PREGUNTAS_GRATIS):
        return str(faq_handler.handle('gratis', phone_number, incoming_msg))
    # Solicitud de turno
    if 'turno' in norm_msg:
        return str(appointment_handler.handle(phone_number, incoming_msg))
    # Fecha (DD/MM/YYYY)
    fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', norm_msg)
    if fecha_match:
        fecha_str = fecha_match.group(1)
        if not is_valid_date(fecha_str):
            resp = MessagingResponse()
            msg = resp.message()
            msg.body("La fecha ingresada no es válida. Usa el formato DD/MM/YYYY.")
            return str(resp)
        return str(date_handler.handle(phone_number, incoming_msg))
    # Hora (HH:MM)
    if re.search(r'\b([0-1][0-9]|2[0-3]):[0-5][0-9]\b', norm_msg):
        return str(time_handler.handle(phone_number, incoming_msg))
    # Nombre del paciente (simplificado)
    if len(norm_msg.split()) >= 2 and norm_msg.replace(' ', '').isalpha():
        return str(patient_name_handler.handle(phone_number, incoming_msg))
    # Respuesta por defecto
    return str(default_handler.handle(phone_number, incoming_msg)) 