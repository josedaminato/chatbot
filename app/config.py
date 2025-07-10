"""
Configuración centralizada del proyecto Asistente de Salud
Usa python-dotenv para cargar variables de entorno desde .env
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la Clínica
CLINIC_NAME = os.getenv('CLINIC_NAME', 'Clínica Dental Cecilia Farreras')
PROFESSIONAL_EMAIL = os.getenv('PROFESSIONAL_EMAIL', 'profesional@ejemplo.com')

# Configuración de Email/SMTP
SMTP_USER = os.getenv('SMTP_USER', 'usuario@gmail.com')
SMTP_PASS = os.getenv('SMTP_PASS', 'contraseña')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Configuración de Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# Configuración de 360Dialog (alternativa a Twilio)
DIALOG_API_KEY = os.getenv('DIALOG_API_KEY')
DIALOG_PHONE_NUMBER = os.getenv('DIALOG_PHONE_NUMBER')

# Configuración del Dashboard y sesiones
SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-muy-segura')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 1 hora

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Proveedor de WhatsApp
WHATSAPP_PROVIDER = os.getenv('WHATSAPP_PROVIDER', 'twilio')

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://usuario:contraseña@localhost/asistente_salud')

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # json o text
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
ERROR_LOG_FILE = os.getenv('ERROR_LOG_FILE', 'logs/error.log')

# Configuración de la aplicación Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

def get_clinic_name_and_email():
    """Obtiene el nombre de la clínica y el email profesional desde las variables de entorno.

    Returns:
        tuple: (nombre_clinica, email_profesional)
    """
    return CLINIC_NAME, PROFESSIONAL_EMAIL

def validate_config():
    """Valida que las configuraciones críticas estén presentes.
    
    Returns:
        bool: True si la configuración es válida
    """
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_WHATSAPP_NUMBER',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("   Configura estas variables en tu archivo .env")
        return False
    
    return True 