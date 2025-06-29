from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    """Procesa la solicitud de turno y responde solicitando fecha.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Para qué fecha deseas el turno? (DD/MM/YYYY)")
    return resp 