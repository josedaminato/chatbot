from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Tu turno fue cancelado correctamente. Si deseas agendar otro, avísame.")
    return resp 