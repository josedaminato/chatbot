# Asistente Virtual para Clínicas y Consultorios

Este bot automatiza la gestión de turnos y responde preguntas frecuentes por WhatsApp para tu clínica o consultorio.

## Instalación

1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Copia el archivo `.env.example` a `.env` y edítalo:
   ```
   cp .env.example .env
   ```
4. Abre el archivo `.env` y cambia el valor de `CLINIC_NAME` por el nombre de tu clínica o consultorio.
   ```
   CLINIC_NAME=Clínica Dental Cecilia Farreras
   # Ejemplo: CLINIC_NAME=Consultorio Odontológico Dr. Pérez
   ```
5. Ejecuta la aplicación:
   ```
   python app.py
   ```

## Personalización
- Cambia el nombre de la clínica en el archivo `.env` para que aparezca en todos los mensajes del bot.
- Puedes modificar las preguntas frecuentes y respuestas en el archivo `app.py` según tus necesidades.

## Soporte
Si tienes dudas o necesitas ayuda, contacta al desarrollador o revisa la documentación incluida. 