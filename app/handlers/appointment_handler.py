from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("¿Para qué fecha deseas el turno? (DD/MM/YYYY)")
    return resp 