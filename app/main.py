import logging
from app.utils.logging_config import setup_logging
setup_logging()
from flask import Flask, jsonify
from .db.init_db import init_db
from .webhook import webhook_bp
from .setup_routes import setup_bp
from .confirm_routes import confirm_bp
from .scheduler import init_scheduler

app = Flask(__name__)

# Inicializar base de datos
init_db()

# Registrar Blueprints
app.register_blueprint(webhook_bp)
app.register_blueprint(setup_bp)
app.register_blueprint(confirm_bp)

# Iniciar schedulers
init_scheduler(app)

# Manejador global de errores
@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Error inesperado en la aplicación:")
    return jsonify({
        "error": "Ha ocurrido un error inesperado. Por favor, intenta nuevamente más tarde o contacta al soporte si el problema persiste."
    }), 500 