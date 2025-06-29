from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    """Procesa la respuesta de fecha y solicita horario al paciente.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Qué horario prefieres?")
    return resp 