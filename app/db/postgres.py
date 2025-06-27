import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'asistente_salud'),
        user=os.getenv('POSTGRES_USER', 'asistente_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'tu_password_segura'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', 5432)
    ) 