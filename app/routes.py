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
    """
    Recibe el video de la galería e inicia el bombardeo a Telegram.
    """
    if 'video_file' not in request.files:
        return redirect(url_for('main.index'))
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 1. Guardar el archivo en media/raw de forma segura
    filename = secure_filename(file.filename)
    raw_path = os.path.join('media', 'raw', filename)
    file.save(raw_path)
    
    # 2. DISPARO ASÍNCRONO (Cero paciencia)
    # Lanzamos el proceso en segundo plano para que la web no se cuelgue
    engine_thread = threading.Thread(
        target=VideoEngine.execute_parallel_cut, 
        args=(raw_path, 60) # Cortes de 60 segundos fijos
    )
    engine_thread.daemon = True
    engine_thread.start()
    
    # 3. Liberar el navegador de inmediato
    return redirect(url_for('main.index'))
