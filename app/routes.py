from flask import Blueprint, render_template, request, jsonify, send_from_directory
from app.services import VideoEngine
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/editor')
def editor():
    video_path = request.args.get('path', '')
    return render_template('editor.html', video_path=video_path)

@bp.route('/gallery')
def gallery():
    # Lista las carpetas de proyectos en media/exports
    export_path = 'media/exports'
    projects = [d for d in os.listdir(export_path) if os.path.isdir(os.path.join(export_path, d))]
    projects.sort(reverse=True) # Los más nuevos primero
    return render_template('dashboard.html', projects=projects)

@bp.route('/api/cut', methods=['POST'])
def process_cut():
    data = request.json
    # El motor paralelo se activa aquí
    result_dir = VideoEngine.execute_parallel_cut(data['path'], data['seconds'])
    if result_dir:
        return jsonify({"status": "success", "folder": result_dir})
    return jsonify({"status": "error"}), 500
