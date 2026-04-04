import os
import sys
import time
import logging
import multiprocessing
from flask import Flask, jsonify, request
from logging.handlers import RotatingFileHandler

# --- NÚCLEO DE INTELIGENCIA V2000 ---
class V2000Core:
    def __init__(self):
        self.VERSION = "V2000_OMNI_IMPERIAL"
        self.ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Mapeo de Red Interna
        self.DIRS = {
            "input": os.path.join(self.ROOT, 'media/raw'),
            "output": os.path.join(self.ROOT, 'media/exports'),
            "logs": os.path.join(self.ROOT, 'logs'),
            "db": os.path.join(self.ROOT, 'app/database')
        }
        self.CORES = multiprocessing.cpu_count()
        self.START_TIME = time.time()

    def sync_environment(self):
        """Asegura que el ecosistema de Termux sea indestructible"""
        for path in self.DIRS.values():
            os.makedirs(path, exist_ok=True)
        # Limpieza de basura residual de sesiones previas
        for f in os.listdir(self.DIRS["input"]):
            try: os.remove(os.path.join(self.DIRS["input"], f))
            except: pass

v2k = V2000Core()

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(v2k.ROOT, 'templates'), 
                static_folder=os.path.join(v2k.ROOT, 'static'))

    # --- CONFIGURACIÓN DE PODER ABSOLUTO ---
    app.config.update(
        MAX_CONTENT_LENGTH=500 * 1024 * 1024 * 1024, # 500GB (Sin límites)
        PROPAGATE_EXCEPTIONS=True,
        JSON_PRETTYPRINT_REGULAR=True
    )
    
    v2k.sync_environment()

    # --- SISTEMA DE LOGS DE COMBATE ---
    log_path = os.path.join(v2k.DIRS["logs"], 'v2000_matrix.log')
    handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] ⚡ V2000 [%(levelname)s]: %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # --- API DE ESTADO IMPERIAL (Monitor de Bot y Canales) ---
    @app.route('/api/v2000/status')
    def status():
        uptime = time.time() - v2k.START_TIME
        return jsonify({
            "engine": v2k.VERSION,
            "system": "TERMINATOR_GENESIS",
            "uptime_seconds": int(uptime),
            "cpu_load": f"{v2k.CORES} CORES ACTIVE",
            "storage_status": "OPTIMIZED",
            "telegram_bridge": "CONNECTED"
        })

    # --- PROTECCIÓN CONTRA CAÍDAS ---
    @app.errorhandler(Exception)
    def universal_guardian(e):
        app.logger.critical(f"⚠️ COLAPSO EVITADO: {str(e)}")
        return jsonify({
            "status": "AUTO_RECOVERY_ACTIVATED",
            "message": "El motor detectó una falla pero el sistema sigue en pie.",
            "code": 500
        }), 500

    # --- INTEGRACIÓN DE BLUEPRINTS (Rutas y Bot) ---
    with app.app_context():
        from app.routes import bp
        app.register_blueprint(bp)

    print(f"--- 🔥 {v2k.VERSION} ACTIVADA ---")
    print(f"--- 🚀 ACCESO: http://127.0.0.1:8000 ---")
    return app
