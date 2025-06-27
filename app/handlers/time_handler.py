from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("Por favor, indícame tu nombre completo para finalizar la reserva del turno.")
    return resp 