# Funciones para envío de mensajes por WhatsApp usando Twilio o 360dialog 
import requests
import logging
from app.utils.config import WHATSAPP_PROVIDER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, DIALOG_API_KEY, DIALOG_PHONE_NUMBER
try:
    from twilio.rest import Client
except ImportError:
    Client = None

def send_whatsapp_message(phone_number, message):
    provider = WHATSAPP_PROVIDER.lower()
    if provider == 'twilio':
        if not Client:
            logging.error('Twilio Client not installed.')
            return
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        from_whatsapp_number = TWILIO_WHATSAPP_NUMBER
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
    elif provider == '360dialog':
        api_key = DIALOG_API_KEY
        url = "https://waba.360dialog.io/v1/messages"
        headers = {
            "D360-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        data = {
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info(f"Mensaje enviado a {phone_number} por 360Dialog")
            else:
                logging.error(f"Error 360Dialog: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error enviando WhatsApp con 360Dialog: {e}")
    else:
        logging.error("Proveedor de WhatsApp no soportado.") 