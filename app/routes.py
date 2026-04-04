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
        return "Error 400: No hay video", 400
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    filename = secure_filename(file.filename)
    raw_path = os.path.join('media', 'raw', filename)
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    file.save(raw_path) #
    
    # DISPARO ASÍNCRONO SIMPLE
    thread = threading.Thread(target=VideoEngine.execute_parallel_cut, args=(raw_path, 60))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('main.index'))
