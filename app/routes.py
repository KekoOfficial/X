import os
import threading
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
from app.services import VideoEngine

# --- INICIALIZACIÓN DEL NODO V2000 ---
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Portal de Mando Principal"""
    return render_template('index.html')

@bp.route('/api/brutal-process', methods=['POST'])
def brutal_process():
    """
    DISPARADOR NITRO: 
    Recibe, valida y delega el video al motor en < 100ms.
    """
    # 1. VERIFICACIÓN DE INTEGRIDAD
    if 'video_file' not in request.files:
        current_app.logger.error("❌ V2000: Intento de acceso sin paquete de datos.")
        return jsonify({"status": "error", "msg": "DATOS_INVALIDOS"}), 400
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 2. PROCESAMIENTO FLASH DE ARCHIVO
    # Generamos un ID único para evitar colisiones si subes 2 videos seguidos
    unique_prefix = uuid.uuid4().hex[:6]
    filename = f"{unique_prefix}_{secure_filename(file.filename)}"
    
    raw_path = os.path.join('media', 'raw', filename)
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    
    try:
        # El guardado en disco es lo único que el navegador espera
        file.save(raw_path)
        current_app.logger.info(f"📥 V2000: Archivo recibido -> {filename}")
    except Exception as e:
        current_app.logger.error(f"❌ FALLO DE ESCRITURA: {str(e)}")
        return jsonify({"status": "critical_fail", "msg": "STORAGE_ERROR"}), 500

    # 3. DELEGACIÓN ASÍNCRONA TOTAL (Cero latencia)
    # Lanzamos el motor V2000 en un hilo Daemon para que Flask libere al usuario YA.
    motor_thread = threading.Thread(
        target=VideoEngine.execute_parallel_cut, 
        args=(raw_path, 60),
        name=f"V2000_Motor_{unique_prefix}"
    )
    motor_thread.daemon = True
    motor_thread.start()
    
    # 4. REDIRECCIÓN INSTANTÁNEA
    # El usuario vuelve al index mientras el motor trabaja en las sombras
    return redirect(url_for('main.index'))

@bp.route('/api/v2000/system-info')
def system_info():
    """Endpoint de telemetría para el estado del servidor"""
    return jsonify({
        "node": "MALLY_CUTS_V2000",
        "status": "ACTIVE",
        "storage_check": os.path.exists('media/raw'),
        "threads_active": threading.active_count()
    })
