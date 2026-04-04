import os
import threading
from flask import Blueprint, render_template, request, jsonify
from app.services import VideoEngine

# Inicialización del Blueprint Imperial
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Interfaz de un solo botón: Sin esperas, sin cargas."""
    return render_template('index.html')

@bp.route('/api/direct-fire', methods=['POST'])
def direct_fire():
    """
    EL DISPARADOR: 
    Busca el video localmente en media/raw/ para evitar el lag del navegador.
    """
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"status": "error", "message": "Falta el nombre del archivo"}), 400

    filename = data.get('filename')
    # Ruta absoluta para que el motor no se pierda
    raw_path = os.path.join(os.getcwd(), 'media', 'raw', filename)

    # Verificación instantánea
    if not os.path.exists(raw_path):
        return jsonify({
            "status": "error", 
            "message": f"No existe: {filename} en media/raw/"
        }), 404

    # --- EJECUCIÓN NITRO ASÍNCRONA ---
    # Lanzamos el motor en un hilo separado. 
    # La web te responde "OK" en milisegundos y el motor sigue trabajando solo.
    try:
        engine_thread = threading.Thread(
            target=VideoEngine.execute_parallel_cut, 
            args=(raw_path, 60) # Segmentos de 60 segundos por defecto
        )
        engine_thread.daemon = True # El motor sigue vivo aunque cierres la pestaña
        engine_thread.start()
        
        return jsonify({
            "status": "success", 
            "message": f"🔥 MOTOR V10 INICIADO: {filename}. Revisa Telegram."
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/check')
def check():
    """Verifica que el Imperio esté en línea"""
    return "SERVER ACTIVE - MODE: ZERO PATIENCE"
