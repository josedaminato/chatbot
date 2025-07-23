from flask import Flask, render_template_string, request, redirect, session, url_for
import os
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

# Ruta al archivo de credenciales de Google (debes descargarlo de Google Cloud Console)
GOOGLE_CLIENT_SECRETS = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Template HTML simple
FORM_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Alta de Cliente - Asistente Salud</title>
</head>
<body>
    <h2>Alta de Cliente</h2>
    <form method="post">
        <label>Nombre de la clínica:</label><br>
        <input type="text" name="clinica" required><br><br>
        <label>Email profesional:</label><br>
        <input type="email" name="email" required><br><br>
        <label>Número de WhatsApp:</label><br>
        <input type="text" name="whatsapp" required><br><br>
        <button type="submit">Siguiente</button>
    </form>
</body>
</html>
'''

SUCCESS_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>¡Listo!</title>
</head>
<body>
    <h2>¡Cliente registrado y Google Calendar conectado!</h2>
    <p>Ya podés usar el asistente de salud con integración total.</p>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['clinica'] = request.form['clinica']
        session['email'] = request.form['email']
        session['whatsapp'] = request.form['whatsapp']
        return redirect(url_for('authorize'))
    return render_template_string(FORM_HTML)

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Guardar el token y los datos del cliente
    cliente_id = session['email'].replace('@', '_').replace('.', '_')
    os.makedirs('clientes', exist_ok=True)
    with open(f'clientes/{cliente_id}_token.pickle', 'wb') as token:
        pickle.dump(credentials, token)
    with open(f'clientes/{cliente_id}_info.txt', 'w', encoding='utf-8') as info:
        info.write(f"Clinica: {session['clinica']}\nEmail: {session['email']}\nWhatsApp: {session['whatsapp']}\n")
    return render_template_string(SUCCESS_HTML)

if __name__ == '__main__':
    app.run(port=8080, debug=True) 