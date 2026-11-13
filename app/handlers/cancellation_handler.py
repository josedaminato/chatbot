from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    """Procesa la solicitud de cancelación de turno y responde solicitando confirmación.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Seguro que deseas cancelar tu turno? Responde SÍ para confirmar.")
    return resp 