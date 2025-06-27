from twilio.twiml.messaging_response import MessagingResponse

def handle(phone_number, incoming_msg):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("No entendí tu mensaje. ¿Podrías reformularlo?")
    return resp 