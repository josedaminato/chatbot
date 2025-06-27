from twilio.twiml.messaging_response import MessagingResponse
from app.utils.config import get_clinic_name_and_email

def handle(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    clinic_name, _ = get_clinic_name_and_email()
    msg.body(f"¡Hola! Soy el asistente virtual de {clinic_name}. ¿En qué puedo ayudarte?")
    return resp 