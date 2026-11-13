import re

# Validar nombre: solo letras, espacios y tildes
NAME_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}$")
def is_valid_name(name):
    """Valida que el nombre contenga solo letras, espacios y tildes."""
    return bool(NAME_REGEX.fullmatch(name.strip()))

# Validar teléfono: solo números, puede empezar con +, 10-15 dígitos
PHONE_REGEX = re.compile(r"^\+?\d{10,15}$")
def is_valid_phone(phone_number):
    phone_number = phone_number.strip()
    if phone_number.startswith('whatsapp:'):
        phone_number = phone_number[len('whatsapp:'):]
    phone_number = phone_number.strip()
    return re.fullmatch(r'\+?\d{10,15}', phone_number) is not None

# Validar imagen: extensión .jpg o .png
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
def is_valid_image(filename):
    """Valida que el archivo sea una imagen JPG o PNG."""
    ext = filename.lower().rsplit('.', 1)[-1]
    return f'.{ext}' in IMAGE_EXTENSIONS 