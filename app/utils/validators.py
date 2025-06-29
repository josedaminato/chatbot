import re
from datetime import datetime

# Validar nombre: solo letras, espacios y tildes
NAME_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}$")
def is_valid_name(name):
    """Valida que el nombre contenga solo letras, espacios y tildes.

    Args:
        name (str): Nombre a validar.

    Returns:
        bool: True si es válido, False si no.
    """
    return bool(NAME_REGEX.fullmatch(name.strip()))

# Validar teléfono: solo números, puede empezar con +, 10-15 dígitos
PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")
def is_valid_phone(phone):
    """Valida que el teléfono tenga solo números, opcional +, y 10-15 dígitos.

    Args:
        phone (str): Teléfono a validar.

    Returns:
        bool: True si es válido, False si no.
    """
    return bool(PHONE_REGEX.fullmatch(phone.strip()))

# Validar fecha: formato DD/MM/YYYY
DATE_FORMAT = "%d/%m/%Y"
def is_valid_date(date_str):
    """Valida que la fecha esté en formato DD/MM/YYYY.

    Args:
        date_str (str): Fecha a validar.

    Returns:
        bool: True si es válido, False si no.
    """
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False

# Validar imagen: extensión .jpg o .png
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
def is_valid_image(filename):
    """Valida que el archivo sea una imagen JPG o PNG.

    Args:
        filename (str): Nombre del archivo.

    Returns:
        bool: True si es válido, False si no.
    """
    ext = filename.lower().rsplit('.', 1)[-1]
    return f'.{ext}' in IMAGE_EXTENSIONS 