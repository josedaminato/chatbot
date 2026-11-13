from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    """Responde cuando el mensaje del usuario no es comprendido.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Mensaje recibido.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("No entendí tu mensaje. ¿Podrías reformularlo?")
    return resp 