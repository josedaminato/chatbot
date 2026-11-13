from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    """Procesa la confirmación de cancelación y responde al paciente.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Tu turno fue cancelado correctamente. Si deseas agendar otro, avísame.")
    return resp 