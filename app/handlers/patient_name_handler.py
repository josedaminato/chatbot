from twilio.twiml.messaging_response import MessagingResponse
from app.utils.validators import is_valid_name

def handle(phone_number, incoming_msg):
    """Procesa el nombre del paciente, valida y responde.

    Args:
        phone_number (str): Teléfono del paciente.
        incoming_msg (str): Nombre ingresado por el usuario.

    Returns:
        MessagingResponse: Respuesta Twilio.
    """
    resp = MessagingResponse()
    msg = resp.message()
    if not is_valid_name(incoming_msg):
        msg.body("El nombre ingresado no es válido. Por favor, ingresa solo letras y espacios.")
        return resp
    msg.body("¡Turno reservado exitosamente! Te esperamos.")
    return resp 