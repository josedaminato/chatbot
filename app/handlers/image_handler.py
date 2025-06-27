from twilio.twiml.messaging_response import MessagingResponse
from app.utils.validators import is_valid_image
from app.services.image_handler import save_image_and_notify
from app.utils.config import get_clinic_name_and_email

def handle(phone_number, incoming_msg, media_url, filename):
    resp = MessagingResponse()
    msg = resp.message()
    if not is_valid_image(filename):
        msg.body("Solo se permiten imágenes JPG o PNG.")
        return str(resp)
    success = save_image_and_notify(phone_number, None, media_url)
    clinic_name, _ = get_clinic_name_and_email()
    if success:
        msg.body(f"{clinic_name}: Imagen recibida correctamente. El profesional la revisará antes de tu consulta.")
    else:
        msg.body(f"{clinic_name}: Hubo un problema al procesar la imagen. Por favor, inténtalo de nuevo.")
    return resp 