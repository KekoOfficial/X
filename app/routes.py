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
    if 'video_file' not in request.files:
        return redirect(url_for('main.index'))
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # Guardamos rápido en la carpeta interna
    filename = secure_filename(file.filename)
    raw_path = os.path.join('media', 'raw', filename)
    file.save(raw_path)
    
    # --- AQUÍ ESTÁ EL TRUCO DE LA VELOCIDAD ---
    # Lanzamos el motor en un hilo "Daemon" para que Flask responda 
    # de inmediato y no se quede la pantalla en blanco.
    def run_engine():
        VideoEngine.execute_parallel_cut(raw_path, 60)
        # Opcional: Borrar original para no llenar memoria
        # os.remove(raw_path)

    thread = threading.Thread(target=run_engine)
    thread.daemon = True
    thread.start()
    
    # Volvemos al inicio al instante
    return redirect(url_for('main.index'))
