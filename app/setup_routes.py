from flask import Blueprint, request, render_template_string
from app.db.queries import get_connection

setup_bp = Blueprint('setup', __name__)

@setup_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        clinic_name = request.form.get('clinic_name')
        professional_email = request.form.get('professional_email')
        conn = get_connection()
        c = conn.cursor()
        c.execute('DELETE FROM settings')
        c.execute('INSERT INTO settings (id, clinic_name, professional_email) VALUES (1, %s, %s)', (clinic_name, professional_email))
        conn.commit()
        conn.close()
        return 'Configuración guardada correctamente.'
    # Formulario simple HTML
    form_html = '''
    <form method="post">
        <label>Nombre de la clínica:</label><br>
        <input type="text" name="clinic_name" required><br><br>
        <label>Email del profesional:</label><br>
        <input type="email" name="professional_email" required><br><br>
        <input type="submit" value="Guardar">
    </form>
    '''
    return render_template_string(form_html) 