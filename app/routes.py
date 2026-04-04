import os
import threading
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.services import VideoEngine

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/process', methods=['POST'])
def process():
    if 'video_file' not in request.files:
        return redirect(url_for('main.index'))
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 1. Guardado ultra-rápido en RAM/Disco
    filename = secure_filename(file.filename)
    raw_path = os.path.join('media', 'raw', filename)
    file.save(raw_path)
    
    # 2. SEGUNDO PLANO (Background Engine)
    # Lanzamos el motor y devolvemos la respuesta al navegador para liberar memoria
    thread = threading.Thread(
        target=VideoEngine.execute_parallel_cut, 
        args=(raw_path, 60) # Siempre fragmentos de 60s
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('main.index'))
