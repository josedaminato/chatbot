import bcrypt
 
password = "Daminato88"  # <-- pon aquí tu contraseña
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed) 