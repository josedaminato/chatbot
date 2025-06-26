from flask import Blueprint, request
from app.db.queries import get_connection
from datetime import datetime

confirm_bp = Blueprint('confirm', __name__)

@confirm_bp.route('/confirmar_turno')
def confirmar_turno():
    turno_id = request.args.get('id')
    if not turno_id:
        return 'ID de turno no especificado.'
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT patient_name, appointment_date FROM appointments WHERE id = %s', (turno_id,))
    turno = c.fetchone()
    if not turno:
        conn.close()
        return 'Turno no encontrado.'
    # Cambiar estado a confirmado
    c.execute('UPDATE appointments SET status = %s WHERE id = %s', ('confirmado', turno_id))
    conn.commit()
    conn.close()
    return f'Turno confirmado correctamente para {turno[0]} el {datetime.strptime(turno[1], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y a las %H:%M")}' 