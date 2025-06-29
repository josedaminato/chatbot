# Funciones para cargar configuración global y variables de entorno 

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Email/SMTP
SMTP_USER = os.getenv('SMTP_USER', 'usuario@gmail.com')
SMTP_PASS = os.getenv('SMTP_PASS', 'contraseña')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Clínica
CLINIC_NAME = os.getenv('CLINIC_NAME', 'Clínica Dental Cecilia Farreras')
PROFESSIONAL_EMAIL = os.getenv('PROFESSIONAL_EMAIL', 'profesional@ejemplo.com')

def get_clinic_name_and_email():
    """Obtiene el nombre de la clínica y el email profesional desde las variables de entorno.

    Returns:
        tuple: (nombre_clinica, email_profesional)
    """
    return CLINIC_NAME, PROFESSIONAL_EMAIL

# Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# 360Dialog
DIALOG_API_KEY = os.getenv('DIALOG_API_KEY')
DIALOG_PHONE_NUMBER = os.getenv('DIALOG_PHONE_NUMBER')

# Dashboard y sesiones
SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-muy-segura')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hora

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Proveedor de WhatsApp
WHATSAPP_PROVIDER = os.getenv('WHATSAPP_PROVIDER', 'twilio') 