import os
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.services import VideoEngine

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/auto-process', methods=['POST'])
def auto_process():
    if 'video_file' not in request.files:
        return redirect(url_for('main.index'))
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 1. Guardado automático en media/raw
    filename = secure_filename(file.filename)
    raw_path = os.path.join('media', 'raw', filename)
    file.save(raw_path)
    
    # 2. Ejecución inmediata del motor (60 segundos fijos)
    # El motor usará todos los núcleos para terminar en segundos
    VideoEngine.execute_parallel_cut(raw_path, segment_seconds=60)
    
    # 3. Limpieza opcional del archivo original para ahorrar espacio en Termux
    # os.remove(raw_path) 

    # 4. Regresa al inicio listo para el siguiente video
    return redirect(url_for('main.index'))
