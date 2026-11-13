from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    """Procesa la respuesta de horario y solicita nombre completo al paciente.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Por favor, indícame tu nombre completo para finalizar la reserva del turno.")
    return resp 