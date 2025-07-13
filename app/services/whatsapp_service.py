# Funciones para envío de mensajes por WhatsApp usando Twilio o 360dialog 
import requests
import logging
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
try:
    from twilio.rest import Client
except ImportError:
    Client = None

# Proveedor por defecto (puedes ajustar esto según tu .env)
WHATSAPP_PROVIDER = 'twilio'

def send_whatsapp_message(phone_number, message):
    provider = WHATSAPP_PROVIDER.lower()
    if provider == 'twilio':
        if not Client:
            logging.error('Twilio Client not installed.')
            return
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        from_whatsapp_number = TWILIO_PHONE_NUMBER
        to_whatsapp_number = f'whatsapp:{phone_number}' if not phone_number.startswith('whatsapp:') else phone_number
        client = Client(account_sid, auth_token)
        try:
            client.messages.create(
                body=message,
                from_=from_whatsapp_number,
                to=to_whatsapp_number
            )
            logging.info(f"Mensaje enviado a {phone_number} por Twilio")
        except Exception as e:
            logging.error(f"Error enviando WhatsApp con Twilio: {e}")
    else:
        logging.error("Proveedor de WhatsApp no soportado o no implementado en este entorno.") 