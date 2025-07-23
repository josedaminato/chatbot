import shutil
import os

TEMPLATE = 'config.example.env'
OUTPUT = '.env'

print('=== Configuración rápida para nuevo cliente ===')
clinica = input('Nombre de la clínica: ').strip()
email = input('Email del profesional: ').strip()
whatsapp = input('Número de WhatsApp (formato whatsapp:+549XXXXXXXXX): ').strip()

# Leer template
with open(TEMPLATE, 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar campos mínimos
content = content.replace('CLINIC_NAME=', f'CLINIC_NAME={clinica}')
content = content.replace('PROFESSIONAL_EMAIL=', f'PROFESSIONAL_EMAIL={email}')
content = content.replace('TWILIO_WHATSAPP_NUMBER=', f'TWILIO_WHATSAPP_NUMBER={whatsapp}')

# Guardar nuevo .env
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Archivo {OUTPUT} generado correctamente. Completa el resto de los datos técnicos antes de levantar el servicio.') 