import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from app.services import VideoEngine

# Definimos el Blueprint principal
bp = Blueprint('main', __name__)

# --- RUTAS DE NAVEGACIÓN ---

@bp.route('/')
def index():
    """Pantalla de inicio con el selector visual de galería"""
    return render_template('index.html')

@bp.route('/editor')
def editor():
    """Pantalla del editor. Recibe la ruta del video automáticamente"""
    video_path = request.args.get('path', '')
    return render_template('editor.html', video_path=video_path)

@bp.route('/gallery')
def gallery():
    """Muestra todas las carpetas de cortes generados"""
    export_path = os.path.join('media', 'exports')
    if not os.path.exists(export_path):
        os.makedirs(export_path, exist_ok=True)
        
    # Listamos carpetas de proyectos (ordenadas por la más reciente)
    projects = [d for d in os.listdir(export_path) if os.path.isdir(os.path.join(export_path, d))]
    projects.sort(reverse=True)
    return render_template('dashboard.html', projects=projects)

# --- RUTAS DE API Y AUTOMATIZACIÓN ---

@bp.route('/api/auto-upload', methods=['POST'])
def auto_upload():
    """
    Recibe el video seleccionado de la galería de Android.
    Lo guarda y redirige al editor sin que el usuario escriba nada.
    """
    if 'video_file' not in request.files:
        return redirect(url_for('main.index'))
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 1. Limpiar nombre y definir ruta en media/raw
    filename = secure_filename(file.filename)
    upload_path = os.path.join('media', 'raw', filename)
    
    # 2. Guardar el video físicamente en el servidor/Termux
    try:
        file.save(upload_path)
    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")
        return "Error al procesar el archivo de galería", 500
    
    # 3. ÉXITO: Mandar al editor con la ruta interna ya lista
    return redirect(url_for('main.editor', path=upload_path))

@bp.route('/api/cut', methods=['POST'])
def process_cut():
    """
    Llamada desde app.js para iniciar la fragmentación Nitro.
    """
    data = request.json
    v_path = data.get('path')
    v_seconds = data.get('seconds', 60)
    
    if not v_path or not os.path.exists(v_path):
        return jsonify({"status": "error", "message": "Archivo no encontrado"}), 404

    # Ejecutar el motor de paralelismo de services.py
    result_dir = VideoEngine.execute_parallel_cut(v_path, v_seconds)
    
    if result_dir:
        return jsonify({
            "status": "success", 
            "folder": result_dir,
            "message": "Fragmentación completada en tiempo récord"
        })
    
    return jsonify({"status": "error", "message": "Fallo en el motor V10"}), 500

@bp.route('/api/open-folder')
def open_folder():
    """Opcional: Intenta abrir la carpeta de archivos (útil en PC)"""
    import platform
    import subprocess
    
    path = os.path.realpath(os.path.join('media', 'exports'))
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "No se puede abrir automáticamente en este dispositivo"})
