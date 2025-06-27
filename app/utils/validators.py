import re
from datetime import datetime

# Validar nombre: solo letras, espacios y tildes
NAME_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}$")
def is_valid_name(name):
    return bool(NAME_REGEX.fullmatch(name.strip()))

# Validar teléfono: solo números, puede empezar con +, 10-15 dígitos
PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")
def is_valid_phone(phone):
    return bool(PHONE_REGEX.fullmatch(phone.strip()))

# Validar fecha: formato DD/MM/YYYY
DATE_FORMAT = "%d/%m/%Y"
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False

# Validar imagen: extensión .jpg o .png
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
def is_valid_image(filename):
    ext = filename.lower().rsplit('.', 1)[-1]
    return f'.{ext}' in IMAGE_EXTENSIONS 