from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Seguro que deseas cancelar tu turno? Responde SÍ para confirmar.")
    return resp 