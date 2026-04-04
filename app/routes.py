import os
import threading
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.services import VideoEngine

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/brutal-process', methods=['POST'])
def brutal_process():
    # Buscamos 'video_file' que es el nombre que pusimos en el HTML
    if 'video_file' not in request.files:
        return "Error: No se encontró el archivo en la solicitud (400)", 400
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 1. Guardado ultra-rápido
    filename = secure_filename(file.filename)
    raw_path = os.path.join('media', 'raw', filename)
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    file.save(raw_path)
    
    # 2. DISPARO ASÍNCRONO (Cero espera para el navegador)
    # El motor trabaja mientras tú ya estás de vuelta en la pantalla principal
    thread = threading.Thread(target=VideoEngine.execute_parallel_cut, args=(raw_path, 60))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('main.index'))
