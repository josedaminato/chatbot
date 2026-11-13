"""
Configuración centralizada de la aplicación
Carga variables de entorno usando python-dotenv
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración general
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
ENV = os.getenv('ENV', 'development')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
CLINIC_NAME = os.getenv('CLINIC_NAME', 'Clínica Demo')

# Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://asistente_user:tu_password_segura@localhost/asistente_salud')

# Otros tokens/servicios
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Validación de configuración mínima

def validate_config():
    required = [SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, OPENAI_API_KEY]
    return all(required) 