from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/auto-upload', methods=['POST'])
def auto_upload():
    if 'video_file' not in request.files:
        return redirect(url_for('main.index'))
    
    file = request.files['video_file']
    if file.filename == '':
        return redirect(url_for('main.index'))

    # 1. Asegurar nombre y guardar en la estructura imperial
    filename = secure_filename(file.filename)
    upload_path = os.path.join('media', 'raw', filename)
    
    # 2. Guardar físicamente el archivo
    file.save(upload_path)
    
    # 3. Redirigir al editor pasando la ruta generada automáticamente
    # Así ya no tienes que escribir NADA.
    return redirect(url_for('main.editor', path=upload_path))

@bp.route('/editor')
def editor():
    video_path = request.args.get('path', '')
    return render_template('editor.html', video_path=video_path)

@bp.route('/gallery')
def gallery():
    export_path = 'media/exports'
    projects = [d for d in os.listdir(export_path) if os.path.isdir(os.path.join(export_path, d))]
    projects.sort(reverse=True)
    return render_template('dashboard.html', projects=projects)
