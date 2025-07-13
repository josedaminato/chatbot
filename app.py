from flask import Flask, request, jsonify, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
import requests
import base64
import uuid
from werkzeug.utils import secure_filename
from app.services.calendar_service import (
    get_google_calendar_service,
    is_slot_available_in_calendar,
    create_calendar_event
)
from app.db.queries import get_settings, get_connection

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

# Configuración del plan
PLAN = 'gratuito'  # Cambia a 'premium' para activar funciones avanzadas
BRANDING = os.getenv('CLINIC_NAME', 'Clínica Dental Cecilia Farreras')
# Configuración de email para notificaciones
PROFESSIONAL_EMAIL = os.getenv('PROFESSIONAL_EMAIL', 'profesional@ejemplo.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', 'usuario@gmail.com')
SMTP_PASS = os.getenv('SMTP_PASS', 'contraseña')

# Función para enviar email de notificación
def send_email_notification(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error enviando email: {e}")

# Función para verificar disponibilidad y agendar en Google Calendar

def is_slot_available_in_calendar(service, calendar_id, start_datetime, end_datetime):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_datetime.isoformat() + 'Z',
        timeMax=end_datetime.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return len(events) == 0

def create_calendar_event(service, calendar_id, summary, description, start_datetime, end_datetime):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
    }
    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created_event.get('id')

CANCEL_KEYWORDS = ['cancelar', 'anular', 'borrar']
CONFIRM_KEYWORDS = ['si', 'sí', 'confirmo']

URGENCY_KEYWORDS = [
    'urgente', 'urgencia', 'mucho dolor', 'me duele', 'me sangra', 'sangrado', 'no aguanto', 'no soporto', 'emergencia', 'dolor fuerte', 'no puedo más', 'no puedo mas'
]

@app.route('/webhook', methods=['POST'])
def webhook():
    # Obtener configuración dinámica
    clinic_name, professional_email = get_settings()
    # Obtener el mensaje entrante
    incoming_msg = request.values.get('Body', '').lower()
    phone_number = request.values.get('From', '')
    resp = MessagingResponse()
    msg = resp.message()

    # Lógica mejorada para detectar saludos e intenciones
    saludos = ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'buen dia', 'buenas', 'saludos']
    preguntas_gratis = ['es gratis', 'sin costo', 'no cobran', 'no tiene costo', 'gratuito']
    preguntas_obra_social = ['obra social', 'aceptan', 'atienden', 'prepaga', 'cobertura']
    preguntas_costo = ['costo', 'cuánto sale', 'precio', 'valor', 'cuanto cuesta']
    preguntas_ubicacion = ['dónde están', 'ubicación', 'dirección', 'cómo llego', 'donde queda']

    # Preguntas frecuentes básicas (plan gratuito)
    if any(p in incoming_msg for p in preguntas_ubicacion):
        msg.body(f"{clinic_name}: Estamos ubicados en [Dirección de la clínica]. ¿Te gustaría agendar un turno?")
        return str(resp)
    if any(p in incoming_msg for p in preguntas_obra_social):
        msg.body(f"{clinic_name}: Sí, trabajamos con las siguientes obras sociales: [Lista de obras sociales]. ¿Te gustaría agendar un turno?")
        return str(resp)
    if any(p in incoming_msg for p in preguntas_costo):
        msg.body(f"{clinic_name}: El costo de la consulta es de $XXXX. ¿Deseas agendar un turno?")
        return str(resp)
    if any(p in incoming_msg for p in preguntas_gratis):
        msg.body(f"{clinic_name}: Las consultas no son gratuitas. Si deseas saber el costo o agendar un turno, avísame.")
        return str(resp)

    # Branding en saludos
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT profesional, especialidad FROM appointments WHERE phone_number = %s ORDER BY appointment_date DESC LIMIT 1''', (phone_number,))
    last_appointment = c.fetchone()
    conn.close()
    if any(saludo in incoming_msg for saludo in saludos):
        if last_appointment:
            profesional, especialidad = last_appointment
            msg.body(f"¡Hola de nuevo! Te atiende el asistente virtual de {clinic_name}. ¿Deseas reservar con el mismo profesional ({profesional}) o especialidad ({especialidad}) que la última vez?\n\nResponde con:\n- 'Repetir' para reservar igual\n- 'Historial' para ver tus turnos previos\n- 'Nuevo' para elegir otro profesional o especialidad")
        else:
            msg.body(f"¡Hola! Soy el asistente virtual de {clinic_name}. ¿En qué puedo ayudarte?\n\nPuedes consultar sobre:\n- Turnos disponibles\n- Obras sociales\n- Costos de consulta\n- Otras dudas que tengas")
        return str(resp)

    # Lógica para manejar respuesta de paciente frecuente
    if last_appointment:
        if 'repetir' in incoming_msg:
            profesional, especialidad = last_appointment
            msg.body(f"Perfecto, reservaremos con {profesional} ({especialidad}). Por favor, indícame la fecha deseada (DD/MM/YYYY)")
            # Guardar en pending_appointments (sin fecha aún)
            conn = get_connection()
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO pending_appointments (phone_number, profesional, especialidad) VALUES (%s, %s, %s)''',
                      (phone_number, profesional, especialidad))
            conn.commit()
            conn.close()
            return str(resp)
        elif 'historial' in incoming_msg:
            conn = get_connection()
            c = conn.cursor()
            c.execute('''SELECT appointment_date, profesional, especialidad FROM appointments WHERE phone_number = %s ORDER BY appointment_date DESC LIMIT 5''', (phone_number,))
            historial = c.fetchall()
            conn.close()
            if historial:
                historial_str = '\n'.join([f"{datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')} - {row[1]} ({row[2]})" for row in historial])
                msg.body(f"Tus últimos turnos:\n{historial_str}")
            else:
                msg.body("No se encontraron turnos previos.")
            return str(resp)
        elif 'nuevo' in incoming_msg:
            msg.body("Por favor, indícame el profesional o especialidad que deseas para tu próximo turno.")
            return str(resp)

    # Detectar si el mensaje contiene una fecha en formato DD/MM/YYYY
    fecha_match = re.search(r'(\d{2}/\d{2}/\d{4})', incoming_msg)
    if fecha_match:
        fecha_str = fecha_match.group(1)
        try:
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
            horarios_fijos = [f"{h:02d}:00" for h in range(9, 18)]
            conn = get_connection()
            c = conn.cursor()
            c.execute('''SELECT strftime('%H:%M', appointment_date) FROM appointments WHERE date(appointment_date) = %s''', (fecha.strftime('%Y-%m-%d'),))
            ocupados = [row[0] for row in c.fetchall()]
            conn.close()
            disponibles = [h for h in horarios_fijos if h not in ocupados]
            if disponibles:
                horarios_str = '\n'.join(disponibles)
                msg.body(f"Horarios disponibles para el {fecha_str} son:\n{horarios_str}\n\nResponde con el horario que prefieras (por ejemplo: 10:00)")
            else:
                msg.body(f"Lo siento, no hay horarios disponibles para el {fecha_str}. Por favor, elige otra fecha.")
        except ValueError:
            msg.body("La fecha ingresada no es válida. Por favor, usa el formato DD/MM/YYYY.")
        return str(resp)

    # Detectar si el mensaje contiene un horario válido (ejemplo: 10:00)
    horario_match = re.search(r'\b([0-1][0-9]|2[0-3]):[0-5][0-9]\b', incoming_msg)
    if horario_match:
        horario_str = horario_match.group(1)
        # Buscar la última fecha consultada por este usuario (opcional: podrías guardar la fecha en pending_appointments también)
        # Para simplificar, pedimos que el usuario primero envíe la fecha y luego el horario
        # Buscamos la última fecha consultada en los últimos minutos (no implementado aquí, pero se puede mejorar)
        # Por ahora, intentamos reservar el horario para hoy si no hay fecha previa
        today = datetime.now().strftime('%Y-%m-%d')
        appointment_date = f"{today} {horario_str}:00"
        # Verificar si el horario está disponible
        conn = get_connection()
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM appointments WHERE appointment_date = %s''', (appointment_date,))
        ocupado = c.fetchone()[0]
        if ocupado:
            msg.body(f"El horario {horario_str} ya está ocupado. Por favor, elige otro horario o fecha.")
        else:
            # Guardar en pending_appointments
            c.execute('''INSERT OR REPLACE INTO pending_appointments (phone_number, appointment_date) VALUES (%s, %s)''',
                      (phone_number, appointment_date))
            conn.commit()
            msg.body("Por favor, indícame tu nombre completo para finalizar la reserva del turno.")
        conn.close()
        return str(resp)

    if 'turno' in incoming_msg or 'agenda' in incoming_msg or 'sacar' in incoming_msg or 'quiero' in incoming_msg:
        msg.body("Para consultar turnos disponibles, por favor indícame la fecha deseada (DD/MM/YYYY)")
    else:
        msg.body("Hola! Soy el asistente virtual. Puedo ayudarte con:\n- Consulta de turnos\n- Información sobre obras sociales\n- Costos de consulta\n¿En qué puedo ayudarte?")

    # Detectar si el usuario tiene un turno pendiente de completar nombre
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT appointment_date, profesional, especialidad FROM pending_appointments WHERE phone_number = %s', (phone_number,))
    pending = c.fetchone()
    if pending:
        patient_name = incoming_msg.strip().title()
        appointment_date, profesional, especialidad = pending
        # --- PREMIUM: Confirmación automática y Google Calendar ---
        if PLAN == 'premium':
            # Verificar disponibilidad en Google Calendar
            service = get_google_calendar_service()
            calendar_id = 'primary'
            start_dt = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M:%S')
            end_dt = start_dt + timedelta(hours=1)
            if is_slot_available_in_calendar(service, calendar_id, start_dt, end_dt):
                # Crear evento en Google Calendar
                event_id = create_calendar_event(
                    service,
                    calendar_id,
                    summary=f"Turno: {patient_name}",
                    description=f"Paciente: {patient_name}\nTeléfono: {phone_number}\nProfesional: {profesional or '-'}\nEspecialidad: {especialidad or '-'}",
                    start_datetime=start_dt,
                    end_datetime=end_dt
                )
                # Guardar el turno como confirmado
                c.execute('''INSERT INTO appointments (patient_name, phone_number, appointment_date, profesional, especialidad, status, confirmation_sent) VALUES (%s, %s, %s, %s, %s, %s, 0)''',
                          (patient_name, phone_number, appointment_date, profesional, especialidad, 'confirmado'))
                c.execute('DELETE FROM pending_appointments WHERE phone_number = %s', (phone_number,))
                conn.commit()
                conn.close()
                # Notificar por email
                subject = f"Turno confirmado en {clinic_name}"
                body = f"Se ha confirmado un turno:\n\nNombre: {patient_name}\nTeléfono: {phone_number}\nFecha y hora: {start_dt.strftime('%d/%m/%Y a las %H:%M')}\nProfesional: {profesional or '-'}\nEspecialidad: {especialidad or '-'}\n\nEl turno fue agendado en Google Calendar."
                body += f"\n\nPara confirmar el turno, haz clic aquí: http://localhost:5000/confirmar_turno?id={event_id}"
                send_email_notification(professional_email, subject, body)
                msg.body(f"{clinic_name}: ¡Tu turno fue confirmado y agendado! Te esperamos el {start_dt.strftime('%d/%m/%Y a las %H:%M')}.")
                return str(resp)
            else:
                conn.close()
                msg.body(f"{clinic_name}: El horario solicitado ya no está disponible. Por favor, elige otro horario.")
                return str(resp)
        # --- FIN PREMIUM ---
        # ... flujo gratuito ...
        # Guardar el turno como pendiente (plan gratuito)
        c.execute('''INSERT INTO appointments (patient_name, phone_number, appointment_date, profesional, especialidad, status, confirmation_sent) VALUES (%s, %s, %s, %s, %s, %s, 0)''',
                  (patient_name, phone_number, appointment_date, profesional, especialidad, 'pendiente'))
        c.execute('DELETE FROM pending_appointments WHERE phone_number = %s', (phone_number,))
        conn.commit()
        conn.close()
        subject = f"Nueva solicitud de turno en {clinic_name}"
        body = f"Se ha solicitado un nuevo turno:\n\nNombre: {patient_name}\nTeléfono: {phone_number}\nFecha y hora: {datetime.strptime(appointment_date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y a las %H:%M')}\nProfesional: {profesional or '-'}\nEspecialidad: {especialidad or '-'}\n\nPor favor, confirma o rechaza el turno en tu sistema."
        body += f"\n\nPara confirmar el turno, haz clic aquí: http://localhost:5000/confirmar_turno?id={event_id}"
        send_email_notification(professional_email, subject, body)
        msg.body(f"{clinic_name}: Tu solicitud fue recibida, te confirmaremos el turno a la brevedad.")
        return str(resp)
    conn.close()

    # Cancelación de turno por parte del paciente
    if any(word in incoming_msg for word in CANCEL_KEYWORDS):
        # Buscar el próximo turno futuro
        now = datetime.now()
        conn = get_connection()
        c = conn.cursor()
        c.execute('''SELECT id, appointment_date, profesional, especialidad FROM appointments WHERE phone_number = %s AND appointment_date > %s AND status IN (%s, %s) ORDER BY appointment_date ASC LIMIT 1''', (phone_number, now, 'pendiente', 'confirmado'))
        turno = c.fetchone()
        conn.close()
        if turno:
            turno_id, fecha, profesional, especialidad = turno
            fecha_str = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y a las %H:%M')
            # Guardar en sesión temporal (en pending_appointments) que está por cancelar
            conn = get_connection()
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO pending_appointments (phone_number, appointment_date, profesional, especialidad) VALUES (%s, %s, %s, %s)''',
                      (phone_number, fecha, profesional, especialidad))
            conn.commit()
            conn.close()
            msg.body(f"¿Seguro que deseas cancelar tu turno del {fecha_str}? Responde SÍ para confirmar.")
        else:
            msg.body("No tienes turnos futuros para cancelar.")
        return str(resp)

    # Confirmación de cancelación
    if any(word in incoming_msg for word in CONFIRM_KEYWORDS):
        # Verificar si hay una cancelación pendiente
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT appointment_date, profesional, especialidad FROM pending_appointments WHERE phone_number = %s', (phone_number,))
        pending_cancel = c.fetchone()
        if pending_cancel:
            fecha, profesional, especialidad = pending_cancel
            # Buscar el turno a cancelar
            c.execute('''SELECT id FROM appointments WHERE phone_number = %s AND appointment_date = %s AND status IN (%s, %s)''', (phone_number, fecha, 'pendiente', 'confirmado'))
            turno = c.fetchone()
            if turno:
                turno_id = turno[0]
                # Eliminar de Google Calendar si es premium
                if PLAN == 'premium':
                    service = get_google_calendar_service()
                    calendar_id = 'primary'
                    start_dt = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
                    end_dt = start_dt + timedelta(hours=1)
                    # Buscar y eliminar el evento (por resumen y hora)
                    events_result = service.events().list(
                        calendarId=calendar_id,
                        timeMin=start_dt.isoformat() + 'Z',
                        timeMax=end_dt.isoformat() + 'Z',
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    events = events_result.get('items', [])
                    for event in events:
                        if event.get('summary', '').startswith('Turno:'):
                            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
                # Eliminar de la base de datos
                c.execute('DELETE FROM appointments WHERE id = %s', (turno_id,))
                # Borrar el pendiente
                c.execute('DELETE FROM pending_appointments WHERE phone_number = %s', (phone_number,))
                conn.commit()
                conn.close()
                # Notificar al profesional
                subject = f"Turno cancelado en {clinic_name}"
                body = f"El paciente ha cancelado su turno:\n\nTeléfono: {phone_number}\nFecha y hora: {datetime.strptime(fecha, '%Y-%m-%d %H:%M').strftime('%d/%m/%Y a las %H:%M')}\nProfesional: {profesional or '-'}\nEspecialidad: {especialidad or '-'}"
                send_email_notification(professional_email, subject, body)
                msg.body(f"{clinic_name}: Tu turno fue cancelado correctamente. Si deseas agendar otro, avísame.")
                return str(resp)
        conn.close()

    # Detección de emociones o urgencias
    if any(word in incoming_msg for word in URGENCY_KEYWORDS):
        msg.body("Lamento mucho lo que estás pasando. Voy a notificar al profesional para darte prioridad. ¿Te gustaría agendar lo antes posible?")
        # Notificar al profesional por email
        subject = f"URGENTE: Paciente requiere atención prioritaria en {clinic_name}"
        body = f"Mensaje urgente recibido de un paciente:\n\nTeléfono: {phone_number}\nMensaje: {request.values.get('Body', '')}\n\nPor favor, evalúa si puedes hacer un espacio extra en la agenda o si con los turnos actuales puedes atenderlo."
        send_email_notification(professional_email, subject, body)
        # (Opcional) Notificar por WhatsApp también
        send_whatsapp_message(phone_number=professional_email, message=body)  # Solo si el profesional tiene WhatsApp conectado
        return str(resp)

    # Detectar si el mensaje contiene una imagen
    media_url = request.values.get('MediaUrl0')
    if media_url:
        # Es una imagen
        success = save_image_and_notify(phone_number, None, media_url)
        if success:
            msg.body(f"{clinic_name}: Imagen recibida correctamente. El profesional la revisará antes de tu consulta.")
        else:
            msg.body(f"{clinic_name}: Hubo un problema al procesar la imagen. Por favor, inténtalo de nuevo.")
        return str(resp)

    return str(resp)

@app.route('/check_appointments', methods=['GET'])
def check_appointments():
    # Verificar turnos próximos y enviar recordatorios
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now()
    one_hour_later = now + timedelta(hours=1)
    
    c.execute('''SELECT * FROM appointments 
                 WHERE appointment_date BETWEEN %s AND %s
                 AND confirmation_sent = 0''', (now, one_hour_later))
    
    appointments = c.fetchall()
    for appointment in appointments:
        # Enviar mensaje de confirmación
        send_confirmation_message(appointment)
        
        # Marcar como enviado
        c.execute('UPDATE appointments SET confirmation_sent = 1 WHERE id = %s''', 
                 (appointment[0],))
    
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

def send_confirmation_message(appointment):
    # Implementar lógica para enviar mensaje de confirmación
    pass

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        clinic_name = request.form.get('clinic_name')
        professional_email = request.form.get('professional_email')
        conn = get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM settings')
        c.execute('INSERT INTO settings (id, clinic_name, professional_email) VALUES (1, %s, %s)', (clinic_name, professional_email))
        conn.commit()
        conn.close()
        return 'Configuración guardada correctamente.'
    # Formulario simple HTML
    form_html = '''
    <form method="post">
        <label>Nombre de la clínica:</label><br>
        <input type="text" name="clinic_name" required><br><br>
        <label>Email del profesional:</label><br>
        <input type="email" name="professional_email" required><br><br>
        <input type="submit" value="Guardar">
    </form>
    '''
    return render_template_string(form_html)

@app.route('/confirmar_turno')
def confirmar_turno():
    turno_id = request.args.get('id')
    if not turno_id:
        return 'ID de turno no especificado.'
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT patient_name, appointment_date FROM appointments WHERE id = %s', (turno_id,))
    turno = c.fetchone()
    if not turno:
        conn.close()
        return 'Turno no encontrado.'
    # Cambiar estado a confirmado
    c.execute('UPDATE appointments SET status = %s WHERE id = %s', ('confirmado', turno_id))
    conn.commit()
    conn.close()
    # (Opcional) Notificar al paciente (no implementado aquí, pero se puede agregar)
    return f'Turno confirmado correctamente para {turno[0]} el {datetime.strptime(turno[1], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y a las %H:%M")}'

def send_whatsapp_message(phone_number, message):
    provider = os.getenv('WHATSAPP_PROVIDER', 'twilio').lower()
    if provider == 'twilio':
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        to_whatsapp_number = f'whatsapp:{phone_number}' if not phone_number.startswith('whatsapp:') else phone_number

        client = Client(account_sid, auth_token)
        try:
            client.messages.create(
                body=message,
                from_=from_whatsapp_number,
                to=to_whatsapp_number
            )
            print(f"Mensaje enviado a {phone_number} por Twilio")
        except Exception as e:
            print(f"Error enviando WhatsApp con Twilio: {e}")

    elif provider == '360dialog':
        api_key = os.getenv('DIALOG_API_KEY')
        from_number = os.getenv('DIALOG_PHONE_NUMBER')
        url = "https://waba.360dialog.io/v1/messages"
        headers = {
            "D360-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        data = {
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print(f"Mensaje enviado a {phone_number} por 360Dialog")
            else:
                print(f"Error 360Dialog: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error enviando WhatsApp con 360Dialog: {e}")
    else:
        print("Proveedor de WhatsApp no soportado.")

def send_followup_messages():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT id, patient_name, phone_number, appointment_date FROM appointments WHERE status = 'confirmado' AND followup_sent = 0 AND appointment_date < %s''', (yesterday,))
    turnos = c.fetchall()
    for turno in turnos:
        turno_id, patient_name, phone_number, appointment_date = turno
        message = f"Hola {patient_name}, ¿cómo te fue en la consulta? Si querés dejar una reseña o reprogramar otro turno, escribime 😊"
        send_whatsapp_message(phone_number, message)
        c.execute('UPDATE appointments SET followup_sent = 1 WHERE id = %s', (turno_id,))
    conn.commit()
    conn.close()

def mark_absences_and_send_followup():
    now = datetime.now()
    conn = get_connection()
    c = conn.cursor()
    # Buscar turnos confirmados pasados que no tienen attended ni followup_sent
    c.execute('''SELECT id, patient_name, phone_number, appointment_date FROM appointments WHERE status = 'confirmado' AND appointment_date < %s AND (attended IS NULL OR attended = 0) AND followup_sent = 0''', (now,))
    turnos = c.fetchall()
    for turno in turnos:
        turno_id, patient_name, phone_number, appointment_date = turno
        # Marcar como ausente
        c.execute('UPDATE appointments SET attended = 0 WHERE id = %s', (turno_id,))
        # Enviar mensaje de seguimiento por ausencia
        message = f"Hola {patient_name}, notamos que no asististe a tu turno. ¿Querés reprogramar o necesitas ayuda? Si fue un error, avísanos 😊"
        send_whatsapp_message(phone_number, message)
        c.execute('UPDATE appointments SET followup_sent = 1 WHERE id = %s', (turno_id,))
    conn.commit()
    conn.close()

def save_image_and_notify(phone_number, image_data, media_url=None):
    # Crear carpeta uploads si no existe
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    filename = f"patient_{phone_number}_{timestamp}_{unique_id}.jpg"
    file_path = os.path.join('uploads', filename)
    
    # Guardar imagen
    try:
        if image_data:
            # Si tenemos datos de imagen directamente
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(image_data))
        elif media_url:
            # Si tenemos URL de Twilio, descargar
            import requests
            response = requests.get(media_url)
            with open(file_path, 'wb') as f:
                f.write(response.content)
        
        # Buscar turno asociado al paciente
        conn = get_connection()
        c = conn.cursor()
        c.execute('''SELECT id FROM appointments WHERE phone_number = %s AND status IN (%s, %s) ORDER BY appointment_date DESC LIMIT 1''', (phone_number, 'pendiente', 'confirmado'))
        appointment = c.fetchone()
        appointment_id = appointment[0] if appointment else None
        
        # Guardar referencia en base de datos
        c.execute('''INSERT INTO attachments (appointment_id, phone_number, filename, file_path) VALUES (%s, %s, %s, %s)''',
                  (appointment_id, phone_number, filename, file_path))
        conn.commit()
        conn.close()
        
        # Notificar al profesional
        clinic_name, professional_email = get_settings()
        subject = f"Nueva imagen recibida de paciente en {clinic_name}"
        body = f"Un paciente ha enviado una imagen:\n\nTeléfono: {phone_number}\nArchivo: {filename}\n\nLa imagen está guardada en el servidor. Revisa el archivo adjunto."
        
        # Enviar email con imagen adjunta
        send_email_with_attachment(professional_email, subject, body, file_path)
        
        return True
    except Exception as e:
        print(f"Error guardando imagen: {e}")
        return False

def send_email_with_attachment(to_email, subject, body, file_path):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Adjuntar imagen
    with open(file_path, 'rb') as attachment:
        part = MIMEText(attachment.read(), 'base64')
        part['Content-Type'] = 'image/jpeg'
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        msg.attach(part)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error enviando email con adjunto: {e}")

if __name__ == '__main__':
    init_db()
    # Programar el job de seguimiento diario y ausencias
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_followup_messages, 'cron', hour=8, minute=0)  # Seguimiento post-turno
    scheduler.add_job(mark_absences_and_send_followup, 'cron', hour=9, minute=0)  # Gestión de ausencias
    scheduler.start()
    app.run(debug=True)
