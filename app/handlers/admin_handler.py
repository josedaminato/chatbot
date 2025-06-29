from flask import Blueprint, request, Response, render_template_string
from app.db.queries import get_upcoming_appointments, get_past_unattended_appointments, get_all_feedback
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__)

ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin123')

def check_auth(username, password):
    """Verifica usuario y contraseña para autenticación básica."""
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    """Envía respuesta 401 para solicitar autenticación."""
    return Response(
        'Acceso restringido. Ingrese usuario y contraseña.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Decorador para requerir autenticación básica en la ruta."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin')
@requires_auth
def admin():
    """Ruta protegida que muestra turnos futuros, ausencias y feedback en tabla HTML."""
    now = datetime.now()
    # Obtener todos los turnos futuros
    conn = None
    try:
        from app.db.postgres import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT patient_name, phone_number, appointment_date, status FROM appointments WHERE appointment_date > %s ORDER BY appointment_date ASC", (now,))
        futuros = c.fetchall()
        c.execute("SELECT patient_name, phone_number, appointment_date FROM appointments WHERE status = 'confirmado' AND appointment_date < %s AND (attended IS NULL OR attended = FALSE)", (now,))
        ausentes = c.fetchall()
        # Obtener feedback
        feedbacks = get_all_feedback()
    finally:
        if conn:
            conn.close()
    html = '''
    <h2>Turnos futuros</h2>
    <table border="1">
        <tr><th>Nombre</th><th>Teléfono</th><th>Fecha</th><th>Estado</th></tr>
        {% for t in futuros %}
        <tr><td>{{t[0]}}</td><td>{{t[1]}}</td><td>{{t[2]}}</td><td>{{t[3]}}</td></tr>
        {% endfor %}
    </table>
    
    <h2>Ausencias detectadas</h2>
    <table border="1">
        <tr><th>Nombre</th><th>Teléfono</th><th>Fecha</th></tr>
        {% for a in ausentes %}
        <tr><td>{{a[0]}}</td><td>{{a[1]}}</td><td>{{a[2]}}</td></tr>
        {% endfor %}
    </table>
    
    <h2>Feedback de pacientes</h2>
    <table border="1">
        <tr><th>Nombre</th><th>Teléfono</th><th>Fecha</th><th>Mensaje</th></tr>
        {% for f in feedbacks %}
        <tr><td>{{f[0]}}</td><td>{{f[1]}}</td><td>{{f[2]}}</td><td>{{f[3]}}</td></tr>
        {% endfor %}
    </table>
    '''
    return render_template_string(html, futuros=futuros, ausentes=ausentes, feedbacks=feedbacks) 