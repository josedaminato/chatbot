import logging
import os
from logging.handlers import RotatingFileHandler
import json

LOG_FILE = os.getenv('LOG_FILE', 'asistente_salud.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_JSON = os.getenv('LOG_JSON', 'False').lower() in ('true', '1', 'yes')

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging():
    logger = logging.getLogger('asistente_salud')
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    # Formatos
    default_fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    json_fmt = JsonFormatter()

    # Handler de archivo rotativo
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(json_fmt if LOG_JSON else default_fmt)
    logger.addHandler(file_handler)

    # Handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(json_fmt if LOG_JSON else default_fmt)
    logger.addHandler(console_handler)

    return logger 