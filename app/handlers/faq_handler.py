from twilio.twiml.messaging_response import MessagingResponse
from app.utils.config import get_clinic_name_and_email

def handle(tipo, phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    clinic_name, _ = get_clinic_name_and_email()
    if tipo == 'obra_social':
        msg.body(f"{clinic_name}: Sí, trabajamos con las siguientes obras sociales: [Lista de obras sociales]. ¿Te gustaría agendar un turno?")
    elif tipo == 'costo':
        msg.body(f"{clinic_name}: El costo de la consulta es de $XXXX. ¿Deseas agendar un turno?")
    elif tipo == 'ubicacion':
        msg.body(f"{clinic_name}: Estamos ubicados en [Dirección de la clínica]. ¿Te gustaría agendar un turno?")
    elif tipo == 'gratis':
        msg.body(f"{clinic_name}: Las consultas no son gratuitas. Si deseas saber el costo o agendar un turno, avísame.")
    return resp 