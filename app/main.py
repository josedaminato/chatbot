import logging
from app.utils.logging_config import setup_logging
setup_logging()
from flask import Flask, jsonify
from .db.init_db import init_db
from .webhook import webhook_bp
from .setup_routes import setup_bp
from .confirm_routes import confirm_bp
from .scheduler import init_scheduler
from .dashboard.auth import auth_bp
from .dashboard.routes import dashboard_bp
from .handlers.admin_handler import admin_bp
from .utils.config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Inicializar base de datos
init_db()

# Registrar Blueprints
app.register_blueprint(webhook_bp)
app.register_blueprint(setup_bp)
app.register_blueprint(confirm_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)

# Iniciar schedulers
init_scheduler(app)

# Manejador global de errores
@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Error inesperado en la aplicación:")
    return jsonify({
        "error": "Ha ocurrido un error inesperado. Por favor, intenta nuevamente más tarde o contacta al soporte si el problema persiste."
    }), 500 