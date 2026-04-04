import os
import logging
from flask import Flask, jsonify, send_from_directory
from logging.handlers import RotatingFileHandler

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.abspath('templates'), 
                static_folder=os.path.abspath('static'))

    # CONFIGURACIÓN INFINITA
    app.config.update(
        MAX_CONTENT_LENGTH=1024 * 1024 * 1024 * 1024, # 1 Terabyte de Buffer
        PROPAGATE_EXCEPTIONS=True
    )

    # SILENCIAR EL ERROR DEL FAVICON (Evita el Colapso 500)
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    # AUTO-CONSTRUCCIÓN DE ESTRUCTURA
    for d in ['media/raw', 'media/exports', 'logs']:
        os.makedirs(d, exist_ok=True)

    # LOGGING DE ALTA FIDELIDAD
    handler = RotatingFileHandler('logs/matrix_v1trillion.log', maxBytes=20*1024*1024, backupCount=1)
    handler.setFormatter(logging.Formatter('[%(asctime)s] ⚡ CORE_V1T: %(message)s'))
    app.logger.addHandler(handler)

    # GUARDIÁN DE EXCEPCIONES (Mantiene el servidor vivo pase lo que pase)
    @app.errorhandler(Exception)
    def engine_shield(e):
        app.logger.warning(f"🛡️ ESCUDO ACTIVADO: {str(e)}")
        return jsonify({"status": "CORE_ACTIVE", "shield": "ON"}), 200

    with app.app_context():
        from app.routes import bp
        app.register_blueprint(bp)

    print("--- 🌌 MALLY V1,000,000,000,000,000 ACTIVADA ---")
    return app
